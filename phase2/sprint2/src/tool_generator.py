# phase2/sprint2/src/tool_generator.py
from phase2.sprint2.src.parsers.openapi_parser import resolve_ref

def flatten_schema(spec, schema):
    """
    Recursively flattens a schema by resolving all $ref pointers.
    """
    if isinstance(schema, dict):
        if '$ref' in schema:
            # IMPORTANT: Pass the original spec for resolving, not the current sub-schema
            resolved_schema = resolve_ref(spec, schema['$ref'])
            return flatten_schema(spec, resolved_schema)
        
        new_schema = {}
        for key, value in schema.items():
            new_schema[key] = flatten_schema(spec, value)
        return new_schema
    
    elif isinstance(schema, list):
        return [flatten_schema(spec, item) for item in schema]
        
    else:
        return schema

def openapi_to_tool_schema(spec: dict) -> list:
    """
    Converts a parsed OpenAPI specification into a list of tool schemas
    with intelligent ref resolution and requestBody inference.
    """
    tool_schemas = []
    if 'paths' not in spec:
        return tool_schemas

    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            if 'operationId' not in operation:
                continue

            function_name = operation['operationId']
            description = operation.get('description') or operation.get('summary') or "no description"
            
            parameters = {'type': 'object', 'properties': {}, 'required': []}

            # 1. Process path and query parameters
            if 'parameters' in operation:
                for param_ref in operation['parameters']:
                    # First, resolve the reference to the parameter definition
                    param_definition = resolve_ref(spec, param_ref['$ref']) if '$ref' in param_ref else param_ref
                    if not param_definition: continue
                    
                    param_name = param_definition['name']
                    # Then, flatten the schema within the parameter definition
                    param_schema = flatten_schema(spec, param_definition.get('schema', {}))
                    
                    parameters['properties'][param_name] = {
                        'type': param_schema.get('type', 'string'),
                        'description': param_definition.get('description', '')
                    }
                    if param_definition.get('required', False):
                        parameters['required'].append(param_name)

            # 2. Process requestBody
            if 'requestBody' in operation:
                body_content = operation['requestBody'].get('content', {}).get('application/json', {})
                body_schema = body_content.get('schema')

                # --- IMPROVED INFERENCE LOGIC ---
                if not body_schema or not body_schema.get('$ref'):
                    op_id_parts = function_name.lower().replace("_", " ").split()
                    for schema_name in spec.get('components', {}).get('schemas', {}):
                        schema_name_lower = schema_name.lower().replace("_", " ")
                        # Check if all parts of the operationId are present in the schema name
                        if all(part in schema_name_lower for part in op_id_parts):
                            print(f"   - INFO: Inferred requestBody schema for '{function_name}' to be '{schema_name}'")
                            body_schema = {"$ref": f"#/components/schemas/{schema_name}"}
                            break
                
                if body_schema:
                    flat_body_schema = flatten_schema(spec, body_schema)
                    # Add the entire body as a single complex parameter
                    parameters['properties']['request_body'] = {
                        "type": "object",
                        "description": "The JSON body of the request.",
                        "properties": flat_body_schema.get("properties", {}),
                        "required": flat_body_schema.get("required", [])
                    }
                    if operation['requestBody'].get('required', False):
                        parameters['required'].append('request_body')

            tool_schema = {
                "type": "function",
                "function": {
                    "name": function_name,
                    "description": description,
                    "parameters": parameters
                }
            }
            tool_schemas.append(tool_schema)
            print(f"   - Successfully created tool: {function_name}")
            
    return tool_schemas