# crm_chatbot/graph/nodes.py

import json, logging
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, BaseMessage

from crm_chatbot.core.llm_client import llm_client
from crm_chatbot.core.http_client import http_client
from crm_chatbot.graph.state import ChatbotState
from crm_chatbot.graph.actions import execute_crm_action

logger = logging.getLogger("CRMChatbot")
llm = llm_client

def router_node(state: ChatbotState) -> Dict[str, Any]:
    query = state["query"]
    agent_names = list(state["domains"].keys())

    prompt = (f"Bạn là một agent định tuyến thông minh. Dựa vào yêu cầu của người dùng, "
              f"hãy chọn một domain phù hợp nhất để xử lý. "
              f"Bạn BẮT BUỘC phải chọn một trong các domain sau: {', '.join(agent_names)}. "
              f"Chỉ trả về TÊN của domain được chọn.\n"
              f"Yêu cầu của người dùng: '{query}'")
    
    response = llm.invoke(user_message=prompt, system_message="Bạn là một agent định tuyến hiệu quả.")
    chosen = response.content.strip()

    if chosen not in agent_names:
        logger.warning(f"Router trả về domain không hợp lệ '{chosen}', mặc định chọn 'agent_General'")
        chosen = "agent_General"

    logger.info(f"Router đã chọn domain: {chosen}")
    return {"chosen_agent": chosen}

def domain_node(state: ChatbotState) -> Dict[str, Any]:
    domain_name = state["chosen_agent"]
    tools = state["domains"].get(domain_name, [])
    query = state["query"]
    logger.info(f"Thực thi domain: {domain_name}")

    # Thêm System Prompt để hướng dẫn LLM không tự bịa ra dữ liệu
    system_prompt = (
        "Bạn là một trợ lý CRM chuyên nghiệp. Nhiệm vụ của bạn là sử dụng các tool được cung cấp để thực hiện yêu cầu của người dùng.\n"
        "QUY TẮC QUAN TRỌNG NHẤT:\n"
        "- **TUYỆT ĐỐI KHÔNG** được tự bịa ra bất kỳ thông tin nào cho các tham số của tool.\n"
        "- Nếu yêu cầu của người dùng không cung cấp đủ thông tin cho các tham số BẮT BUỘC, bạn **PHẢI** hỏi lại người dùng để làm rõ."
    )
    langchain_messages: List[BaseMessage] = [SystemMessage(content=system_prompt), HumanMessage(content=query)]

    if not tools:
        langchain_messages.pop(0) # Xóa system prompt nếu không có tool
        response = llm.multi_llms.invoke(messages=langchain_messages)
        return {"answer": response.content}

    response = llm.multi_llms.invoke(messages=langchain_messages, tools=tools)
    if not response.tool_calls:
        return {"answer": response.content or "Tôi có thể giúp gì khác cho bạn không?"}

    langchain_messages.append(response)

    # Logic xác thực tham số bắt buộc (giữ nguyên)
    for tool_call in response.tool_calls:
        func_name = tool_call['name']
        args = tool_call['args']
        tool_def = next((t['function'] for t in tools if t.get('function', {}).get('name') == func_name), None)
        if tool_def:
            required_params = tool_def.get('parameters', {}).get('required', [])
            missing_params = [p for p in required_params if p not in args or not args[p]]
            if missing_params:
                prompt = f"Người dùng muốn thực hiện '{func_name}' nhưng thiếu: {', '.join(missing_params)}. Hãy hỏi lại người dùng."
                clarification = llm.invoke(user_message=prompt, system_message="Bạn là trợ lý ảo.")
                return {"answer": clarification.content}

    # Logic thực thi và xử lý kết quả tool
    for tool_call in response.tool_calls:
        func_name = tool_call['name']
        args = tool_call['args']
        action = state["action_map"].get(func_name)
        crm_result = execute_crm_action(http_client, action, args)
        if crm_result.get("ok"):
            content = json.dumps(crm_result.get("result"), ensure_ascii=False)
            langchain_messages.append(ToolMessage(content=content, tool_call_id=tool_call['id']))
        else:
            error_msg = crm_result.get("error", "Lỗi không xác định.")
            prompt = f"Một yêu cầu API thất bại với lỗi: ```{error_msg}```. Hãy diễn giải lỗi này sang ngôn ngữ thân thiện cho người dùng."
            error_interpretation = llm.invoke(user_message=prompt, system_message="Bạn là trợ lý chuyên giải thích lỗi.")
            return {"answer": error_interpretation.content}

    # *** LOGIC TÓM TẮT THÔNG MINH (ĐÃ NÂNG CẤP) ***
    
    # Lấy kết quả từ tool call gần nhất để phân tích
    last_tool_result_str = next((m.content for m in reversed(langchain_messages) if isinstance(m, ToolMessage)), "{}")
    try:
        result_data = json.loads(last_tool_result_str)
    except json.JSONDecodeError:
        result_data = {}

    summary_prompt = ""
    # KIỂM TRA XEM KẾT QUẢ CÓ PHẢI LÀ MỘT DANH SÁCH HAY KHÔNG
    is_list_response = isinstance(result_data, dict) and "list" in result_data and isinstance(result_data.get("list"), list)

    if is_list_response:
        total = result_data.get("total", len(result_data["list"]))
        items_to_show = result_data["list"][:5] # Hiển thị tối đa 5 mục
        
        summary_prompt = (
            f"Bạn là một trợ lý CRM. Yêu cầu của người dùng là \"{query}\". "
            f"Hệ thống đã tìm thấy tổng cộng {total} mục. Dữ liệu của 5 mục đầu tiên là:\n"
            f"```json\n{json.dumps(items_to_show, ensure_ascii=False, indent=2)}\n```\n\n"
            "Nhiệm vụ của bạn là tóm tắt kết quả này cho người dùng bằng tiếng Việt. "
            "Hãy thông báo tổng số lượng tìm thấy. Nếu có dữ liệu, hãy liệt kê tên (sử dụng trường 'name', 'subject', hoặc tương tự) của một vài mục đầu tiên để họ có cái nhìn tổng quan. "
            "Ví dụ: 'Đã tìm thấy 12 lead. Dưới đây là 3 lead đầu tiên: Lead ABC, Lead XYZ, Lead 123.'"
        )
    else: # Trường hợp kết quả là một object đơn (tạo mới, cập nhật, get by id)
        summary_prompt = (
            f"Bạn là một trợ lý CRM chuyên nghiệp bằng tiếng Việt. "
            f"Bạn vừa thực hiện thành công yêu cầu: \"{query}\".\n"
            f"Kết quả dữ liệu trả về từ hệ thống là:\n```json\n{last_tool_result_str}\n```\n\n"
            "Dựa vào kết quả trên, hãy soạn một câu trả lời tự nhiên, ngắn gọn để xác nhận với người dùng. "
            "Chỉ đề cập đến những thông tin quan trọng nhất (ví dụ: tên đối tượng, mã ID)."
        )

    final_resp = llm.invoke(user_message=summary_prompt, system_message="Bạn là một trợ lý CRM hữu ích.")
    return {"answer": final_resp.content}
