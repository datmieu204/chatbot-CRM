# phase2/sprint2/main.py

import os
from phase2.sprint2.src.parsers.openapi_parser import parse_openapi_spec
# from src.parsers.postman_parser import parse_postman_collection
from phase2.sprint2.src.tool_generator import openapi_to_tool_schema
from phase2.sprint2.src.orchestrator import ToolOrchestrator

DOCS_PATH = "phase2/sprint2/docs/openapi.json"

def main():
    print("Bắt đầu Phase 0: Phân tích tài liệu CRM và tạo Tools...")
    
    # 1. Khởi tạo Orchestrator
    orchestrator = ToolOrchestrator()
    
    parsed_data = None
    tool_schemas = []

    # 2. Phân tích tài liệu dựa trên đuôi file
    if DOCS_PATH.endswith(('.yaml', '.yml', '.json')) and 'openapi' in DOCS_PATH:
        print(f"Phát hiện file OpenAPI. Bắt đầu phân tích '{DOCS_PATH}'...")
        parsed_data = parse_openapi_spec(DOCS_PATH)
        if parsed_data:
            # 3. Sinh tool schemas
            print("\nBắt đầu sinh tool schemas từ OpenAPI spec...")
            tool_schemas = openapi_to_tool_schema(parsed_data)
            
    elif DOCS_PATH.endswith('.json') and 'postman' in DOCS_PATH:
        print(f"Phát hiện file Postman. Bắt đầu phân tích '{DOCS_PATH}'...")
        # (Gọi hàm parse và generate cho Postman ở đây)
        # parsed_data = parse_postman_collection(DOCS_PATH)
        # tool_schemas = postman_to_tool_schema(parsed_data)
        print("Chức năng phân tích Postman chưa được triển khai.")

    else:
        print(f"Không hỗ trợ loại file: {DOCS_PATH}")
        return

    # 4. Đăng ký các tool vào Orchestrator
    if tool_schemas:
        print("\nBắt đầu đăng ký các tool...")
        orchestrator.register_tools(tool_schemas)

    print(f"\nHoàn thành Tổng số tool: {orchestrator.available_tools_count}")

    # In ra một ví dụ tool đã được tạo
    if orchestrator.available_tools_count > 0:
        print("\nĐã tạo:")
        first_tool = orchestrator.get_all_tool_schemas()[0]
        import json
        print(json.dumps(first_tool, indent=2, ensure_ascii=False))

    if not os.path.exists("phase2/sprint2/output"):
        os.makedirs("phase2/sprint2/output")
    with open("phase2/sprint2/output/tools.json", "w", encoding="utf-8") as f:
        json.dump(orchestrator.get_all_tool_schemas(), f, ensure_ascii=False, indent=2)

    print("\nXong!")

if __name__ == "__main__":
    main()


