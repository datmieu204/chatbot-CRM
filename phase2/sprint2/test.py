import os
import json
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS_FILE_PATH = "d:\\skymap\\phase2\\sprint2\\output\\tools.json"
MODEL = "gpt-4o-mini"

def load_tools_from_file(filepath: str) -> list:
    """Đọc và parse file JSON chứa định nghĩa các tool."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tools = json.load(f)
        print(f"Đã tải thành công {len(tools)} tool từ '{filepath}'")
        return tools
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{filepath}'")
        return []
    except json.JSONDecodeError:
        print(f"Lỗi: File '{filepath}' không phải là file JSON hợp lệ.")
        return []

def test_tool_call():
    """
    Gửi một prompt tới LLM và kiểm tra xem nó có gọi đúng tool với các tham số chính xác không.
    """
    # 1. Tải các tool đã được tạo ra
    tools = load_tools_from_file(TOOLS_FILE_PATH)
    if not tools:
        return

    # 2. Tạo một prompt của người dùng để kích hoạt tool "Convert Lead"
    # Prompt này chứa thông tin cho các trường bắt buộc như lead_id, Accounts, Contacts, assign_to
    user_prompt = (
        "Làm ơn chuyển đổi khách hàng tiềm năng có ID 987654321. "
        "Tạo một tài khoản mới tên là 'Global Tech Inc.' và một liên hệ mới có họ là 'Smith'. "
        "Hãy gán nó cho người dùng có id 'user123'. "
        "Và hãy nhớ thêm nó vào bản ghi đã tồn tại."
    )

    print("\n--- Gửi Prompt Tới LLM ---")
    print(f"User Prompt: \"{user_prompt}\"")

    messages = [
        {"role": "system", "content": "You are a helpful assistant that can use tools to interact with a CRM system."},
        {"role": "user", "content": user_prompt}
    ]

    try:
        # 3. Gọi API của OpenAI với danh sách tool
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        print("\n--- Phản Hồi Từ LLM ---")

        # 4. Kiểm tra kết quả
        if tool_calls:
            print("LLM đã quyết định gọi một tool!")
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"   - Tên Tool: {function_name}")
                print(f"   - Tham số được tạo:")
                # In các tham số dưới dạng JSON cho dễ đọc
                print(json.dumps(function_args, indent=4, ensure_ascii=False))

                # Kiểm tra cơ bản
                if function_name == "Convert_Lead" and "lead_id" in function_args:
                    print("\n--- Kết Quả Test ---")
                    print("THÀNH CÔNG: LLM đã gọi đúng tool 'Convert_Lead' và tạo ra các tham số cần thiết.")
                else:
                    print("\n--- Kết Quả Test ---")
                    print("THẤT BẠI: LLM đã gọi một tool không mong muốn hoặc thiếu tham số.")
        else:
            print("\n--- Kết Quả Test ---")
            print("THẤT BẠI: LLM đã không gọi bất kỳ tool nào. Nội dung phản hồi:")
            print(response_message.content)

    except Exception as e:
        print(f"\nĐã xảy ra lỗi khi gọi API của OpenAI: {e}")

if __name__ == "__main__":
    test_tool_call()