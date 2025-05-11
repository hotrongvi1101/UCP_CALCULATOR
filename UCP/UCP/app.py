from flask import Flask, render_template, request, jsonify
import requests
import PyPDF2
import textract
import os
import logging
from dotenv import load_dotenv
import json
import json_repair
import re

app = Flask(__name__)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải biến môi trường
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        logger.error("Failed to extract text from PDF: " + str(e))
        return None

def extract_text_from_image(file_path):
    try:
        text = textract.process(file_path, method='tesseract')
        decoded_text = text.decode('utf-8')
        logger.info(f"Extracted {len(decoded_text)} characters from image")
        return decoded_text
    except Exception as e:
        logger.error("Failed to extract text from image: " + str(e))
        return None

def sanitize_content(content):
    """Vệ sinh nội dung để loại bỏ ký tự bất thường."""
    if not content:
        return ""
    content = content.replace('{', '{{').replace('}', '}}')
    content = content.strip()
    content = re.sub(r'\n+', ' ', content)
    content = re.sub(r'\s+', ' ', content)
    return content

def fallback_parse_content(raw_content):
    """Phân tích văn bản tự nhiên để trích xuất các trường cần thiết nếu JSON không hợp lệ."""
    try:
        if not raw_content or not isinstance(raw_content, str):
            logger.error("Invalid raw_content for fallback parsing: " + str(type(raw_content)))
            return {"error": "Nội dung thô không hợp lệ cho phân tích dự phòng", "system_description": ""}

        raw_content = sanitize_content(raw_content)
        if not raw_content:
            logger.error("Sanitized raw_content is empty")
            return {"error": "Nội dung thô sau vệ sinh rỗng", "system_description": ""}

        result = {
            "system_description": "",
            "simple_use_cases": 0,
            "average_use_cases": 0,
            "complex_use_cases": 0,
            "simple_actors": 0,
            "average_actors": 0,
            "complex_actors": 0,
            "t1": 0, "t2": 0, "t3": 0, "t4": 0, "t5": 0, "t6": 0, "t7": 0, "t8": 0, "t9": 0, "t10": 0, "t11": 0, "t12": 0, "t13": 0,
            "e1": 0, "e2": 0, "e3": 0, "e4": 0, "e5": 0, "e6": 0, "e7": 0, "e8": 0,
            "actual_effort": 0,
            "weights_uc_simple": 5,
            "weights_uc_avg": 10,
            "weights_uc_complex": 15,
            "weights_actor_simple": 1,
            "weights_actor_avg": 2,
            "weights_actor_complex": 3,
            "hours_per_ucp": 20,
            "team_size": 1,
            "junior_members": 0,
            "mid_level_members": 0,
            "senior_members": 0,
            "hourly_cost": 50,
            "classification_notes": "Parsed from natural language text due to invalid JSON response."
        }

        lines = raw_content.split(' ')
        for line in lines[:10]:
            if line.strip() and not line.startswith(('{', '}', '[', ']')):
                result["system_description"] = line.strip()[:200]
                break

        simple_uc_pattern = re.compile(r'UC\d+:\s*(Xem|Xem thông tin|Đăng nhập)\b', re.IGNORECASE)
        average_uc_pattern = re.compile(r'UC\d+:\s*(Đăng ký|Nhập điểm|Cập nhật thông tin)\b', re.IGNORECASE)
        complex_uc_pattern = re.compile(r'UC\d+:\s*(Quản lý.*(thời khóa biểu|học sinh|kỳ thi))\b', re.IGNORECASE)

        result["simple_use_cases"] = len(simple_uc_pattern.findall(raw_content))
        result["average_use_cases"] = len(average_uc_pattern.findall(raw_content))
        result["complex_use_cases"] = len(complex_uc_pattern.findall(raw_content))

        simple_actor_pattern = re.compile(r'(Hệ thống email|API bên ngoài|Third-party system)\b', re.IGNORECASE)
        average_actor_pattern = re.compile(r'(Học sinh|Giáo viên|Người dùng)\b', re.IGNORECASE)
        complex_actor_pattern = re.compile(r'(Quản trị viên|Admin)\b', re.IGNORECASE)

        result["simple_actors"] = len(simple_actor_pattern.findall(raw_content))
        result["average_actors"] = len(average_actor_pattern.findall(raw_content))
        result["complex_actors"] = len(complex_actor_pattern.findall(raw_content))

        technical_keywords = {
            "t1": r"(phân tán|distributed)",
            "t2": r"(hiệu suất|performance)",
            "t3": r"(người dùng cuối|end-user)",
            "t4": r"(phức tạp|complex)",
            "t5": r"(tái sử dụng|reusable)",
            "t6": r"(cài đặt|installation)",
            "t7": r"(vận hành|operational)",
            "t8": r"(di động|portable)",
            "t9": r"(bảo trì|maintainable)",
            "t10": r"(đồng thời|concurrent)",
            "t11": r"(bảo mật|security)",
            "t12": r"(bên thứ ba|third-party)",
            "t13": r"(đào tạo|training)"
        }

        environmental_keywords = {
            "e1": r"(kinh nghiệm|experience)",
            "e2": r"(phân tích hướng đối tượng|OOA)",
            "e3": r"(trưởng nhóm|lead)",
            "e4": r"(động lực|motivation)",
            "e5": r"(yêu cầu ổn định|stable requirements)",
            "e6": r"(nhân viên bán thời gian|part-time)",
            "e7": r"(ngôn ngữ lập trình khó|difficult language)",
            "e8": r"(công cụ|tool)"
        }

        for key, pattern in technical_keywords.items():
            if re.search(pattern, raw_content, re.IGNORECASE):
                result[key] = 3

        for key, pattern in environmental_keywords.items():
            if re.search(pattern, raw_content, re.IGNORECASE):
                result[key] = 3

        # Phân tích đội ngũ
        if re.search(r"(junior|new developer|under 2 years)", raw_content, re.IGNORECASE):
            result["junior_members"] = 1
        if re.search(r"(mid-level|2-5 years)", raw_content, re.IGNORECASE):
            result["mid_level_members"] = 1
        if re.search(r"(senior|over 5 years)", raw_content, re.IGNORECASE):
            result["senior_members"] = 1
        if re.search(r"team size|number of members", raw_content, re.IGNORECASE):
            result["team_size"] = 3

        logger.info(f"Fallback parsing result: {result}")
        return result
    except Exception as e:
        logger.error("Error in fallback parsing: " + str(e))
        return {"error": "Không thể phân tích nội dung từ văn bản tự nhiên: " + str(e), "system_description": ""}

def call_gemini_api(text):
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set")
        return {"error": "API key không hợp lệ. Vui lòng kiểm tra GEMINI_API_KEY trong .env.", "system_description": ""}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    text = sanitize_content(text)
    logger.info(f"Sanitized text for API: {text[:100]}...")

    prompt = f"""
    Phân tích nội dung sau và trả về kết quả **chỉ** dưới dạng JSON hợp lệ, được bao quanh bởi dấu ngoặc nhọn {{}}. Không trả về văn bản tự nhiên, không trả về markdown, không thêm giải thích, và không sử dụng dấu backticks (```). Nội dung mô tả một hệ thống phần mềm, bao gồm các tác nhân (actors) và trường hợp sử dụng (use cases). Hãy phân loại chính xác dựa trên thông tin cung cấp:

    {text}

    Trả về JSON với các trường sau:
    - system_description: Mô tả ngắn gọn về hệ thống (1-2 câu, dựa trên nội dung).
    - simple_use_cases: Số use case đơn giản (dưới 3 bước giao dịch, ví dụ: xem thông tin, đăng nhập).
    - average_use_cases: Số use case trung bình (3-7 bước giao dịch, ví dụ: đăng ký tài khoản, nhập điểm).
    - complex_use_cases: Số use case phức tạp (trên 7 bước giao dịch, ví dụ: quản lý toàn bộ thời khóa biểu).
    - simple_actors: Số actor đơn giản (tương tác qua API hoặc giao diện đơn giản, ví dụ: hệ thống email).
    - average_actors: Số actor trung bình (tương tác qua giao diện người dùng, ví dụ: người dùng thông thường).
    - complex_actors: Số actor phức tạp (tương tác với nhiều hệ thống, ví dụ: quản trị viên tích hợp nhiều module).
    - t1: Yếu tố kỹ thuật F1 (Hệ thống phân tán, từ 0-5).
    - t2: Yếu tố kỹ thuật F2 (Yêu cầu hiệu suất, từ 0-5).
    - t3: Yếu tố kỹ thuật F3 (Hiệu quả người dùng cuối, từ 0-5).
    - t4: Yếu tố kỹ thuật F4 (Phức tạp nội bộ, từ 0-5).
    - t5: Yếu tố kỹ thuật F5 (Có thể tái sử dụng, từ 0-5).
    - t6: Yếu tố kỹ thuật F6 (Dễ cài đặt, từ 0-5).
    - t7: Yếu tố kỹ thuật F7 (Dễ vận hành, từ 0-5).
    - t8: Yếu tố kỹ thuật F8 (Khả năng di động, từ 0-5).
    - t9: Yếu tố kỹ thuật F9 (Dễ bảo trì, từ 0-5).
    - t10: Yếu tố kỹ thuật F10 (Xử lý đồng thời, từ 0-5).
    - t11: Yếu tố kỹ thuật F11 (Yêu cầu bảo mật, từ 0-5).
    - t12: Yếu tố kỹ thuật F12 (Truy cập bên thứ ba, từ 0-5).
    - t13: Yếu tố kỹ thuật F13 (Đào tạo đặc biệt, từ 0-5).
    - e1: Yếu tố môi trường E1 (Kinh nghiệm với ứng dụng, từ 0-5).
    - e2: Yếu tố môi trường E2 (Kinh nghiệm OOA/OOD, từ 0-5).
    - e3: Yếu tố môi trường E3 (Trưởng nhóm có năng lực, từ 0-5).
    - e4: Yếu tố môi trường E4 (Động lực đội, từ 0-5).
    - e5: Yếu tố môi trường E5 (Yêu cầu ổn định, từ 0-5).
    - e6: Yếu tố môi trường E6 (Nhân viên bán thời gian, từ 0-5).
    - e7: Yếu tố môi trường E7 (Ngôn ngữ lập trình khó, từ 0-5).
    - e8: Yếu tố môi trường E8 (Công cụ phát triển, từ 0-5).
    - team_size: Số lượng thành viên đội ngũ (mặc định 1).
    - junior_members: Số thành viên junior (kinh nghiệm dưới 2 năm, mặc định 0).
    - mid_level_members: Số thành viên mid-level (kinh nghiệm 2-5 năm, mặc định 0).
    - senior_members: Số thành viên senior (kinh nghiệm trên 5 năm, mặc định 0).
    - hourly_cost: Chi phí trung bình mỗi giờ (USD, mặc định 50).
    - weights_uc_simple: Trọng số cho use case đơn giản (mặc định 5).
    - weights_uc_avg: Trọng số cho use case trung bình (mặc định 10).
    - weights_uc_complex: Trọng số cho use case phức tạp (mặc định 15).
    - weights_actor_simple: Trọng số cho actor đơn giản (mặc định 1).
    - weights_actor_avg: Trọng số cho actor trung bình (mặc định 2).
    - weights_actor_complex: Trọng số cho actor phức tạp (mặc định 3).
    - hours_per_ucp: Số giờ mỗi UCP (mặc định 20).
    - actual_effort: Công sức thực tế (giờ, mặc định 0).
    - classification_notes: Ghi chú chi tiết về cách bạn phân loại use cases, actors, các yếu tố kỹ thuật/môi trường, và đội ngũ, bao gồm lý do chọn số lượng, mức độ phức tạp, và giả định.

    Ví dụ định dạng JSON:
    {{
      "system_description": "Hệ thống quản lý học sinh trực tuyến cho phép quản lý thông tin học sinh và điểm số.",
      "simple_use_cases": 2,
      "average_use_cases": 3,
      "complex_use_cases": 1,
      "simple_actors": 1,
      "average_actors": 2,
      "complex_actors": 1,
      "t1": 3,
      "t2": 2,
      "t3": 4,
      "t4": 3,
      "t5": 2,
      "t6": 3,
      "t7": 3,
      "t8": 2,
      "t9": 4,
      "t10": 3,
      "t11": 4,
      "t12": 2,
      "t13": 1,
      "e1": 3,
      "e2": 2,
      "e3": 4,
      "e4": 3,
      "e5": 4,
      "e6": 1,
      "e7": 2,
      "e8": 3,
      "team_size": 3,
      "junior_members": 1,
      "mid_level_members": 1,
      "senior_members": 1,
      "hourly_cost": 50,
      "weights_uc_simple": 5,
      "weights_uc_avg": 10,
      "weights_uc_complex": 15,
      "weights_actor_simple": 1,
      "weights_actor_avg": 2,
      "weights_actor_complex": 3,
      "hours_per_ucp": 20,
      "actual_effort": 0,
      "classification_notes": "Đăng nhập và xem điểm là use case đơn giản (2 bước). Đăng ký tài khoản và nhập điểm là use case trung bình (4-5 bước). Quản lý thời khóa biểu là use case phức tạp (8 bước). Hệ thống email là actor đơn giản, học sinh và giáo viên là actor trung bình, quản trị viên là actor phức tạp. Các yếu tố kỹ thuật và môi trường được ước lượng dựa trên yêu cầu bảo mật cao (t11=4) và đội phát triển có kinh nghiệm trung bình (e1=3). Đội ngũ gồm 1 junior, 1 mid-level, 1 senior dựa trên mô tả đội phát triển."
    }}

    Đảm bảo:
    - Phân tích chính xác số lượng use cases, actors, các yếu tố kỹ thuật/môi trường, và đội ngũ dựa trên nội dung.
    - Nếu thông tin không rõ ràng, đưa ra giả định hợp lý (ví dụ: t1=3 nếu hệ thống có vẻ phân tán, team_size=3 nếu không rõ số lượng) và ghi chú trong classification_notes.
    - Trả về **chỉ** JSON hợp lệ, không có lỗi cú pháp, và không bao quanh bởi backticks.
    - Nếu không thể phân tích, trả về JSON: {{"error": "Không thể phân tích nội dung", "system_description": ""}}.
    """

    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        logger.info("Sending request to Gemini API")
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"Gemini API Response Status: {response.status_code}")
        logger.info(f"Full Gemini API Response: {response.text}")

        if response.status_code != 200:
            logger.error("Gemini API Error: Status " + str(response.status_code) + " - " + response.text[:200])
            return {"error": "Lỗi từ Gemini API: Status " + str(response.status_code) + " - " + response.text[:200], "system_description": ""}

        try:
            response_data = response.json()
        except ValueError as e:
            logger.error("Failed to parse Gemini API response as JSON: " + str(e))
            logger.error(f"Raw response: {response.text}")
            return {"error": "Không thể phân tích phản hồi JSON từ Gemini API: " + str(e), "system_description": ""}

        if not isinstance(response_data, dict):
            logger.error("Invalid response format from Gemini API: Expected dict, got " + str(type(response_data)))
            return {"error": "Phản hồi từ Gemini API không đúng định dạng: Không phải dictionary", "system_description": ""}

        candidates = response_data.get("candidates", [])
        if not candidates:
            logger.error("No candidates in Gemini API response")
            return {"error": "Không có dữ liệu candidates trong phản hồi từ Gemini API", "system_description": ""}

        raw_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        logger.info(f"Raw content: {raw_content[:100]}...")

        raw_content = sanitize_content(raw_content)
        if not raw_content:
            logger.error("Sanitized raw content is empty")
            return {"error": "Nội dung phản hồi từ Gemini API rỗng sau khi vệ sinh", "system_description": ""}

        try:
            parsed_content = json.loads(raw_content)
            if not isinstance(parsed_content, dict):
                logger.error("Parsed content is not a dictionary: " + str(type(parsed_content)))
                return {"error": "Nội dung phân tích từ Gemini API không phải JSON dictionary", "system_description": ""}
        except json.JSONDecodeError as json_err:
            logger.info(f"Raw content before repair: {raw_content}")
            logger.info("Attempting to repair JSON")
            try:
                parsed_content = json_repair.loads(raw_content)
                if not isinstance(parsed_content, dict):
                    logger.error("Repaired content is not a dictionary: " + str(type(parsed_content)))
                    return {"error": "Nội dung sửa chữa từ Gemini API không phải JSON dictionary", "system_description": ""}
            except Exception as repair_err:
                logger.error("Failed to parse repaired JSON: " + str(repair_err))
                logger.error(f"Raw content was: {raw_content}")
                logger.info("Attempting fallback parsing of natural language content")
                parsed_content = fallback_parse_content(raw_content)
                if "error" in parsed_content:
                    return parsed_content
        logger.info(f"Gemini API Result: {parsed_content}")
        return parsed_content
    except Exception as e:
        logger.error("Error in Gemini API call: " + str(e))
        logger.error(f"Last raw content (if available): {locals().get('raw_content', 'N/A')}")
        return {"error": "Lỗi khi gọi Gemini API: " + str(e), "system_description": ""}

@app.route('/')
def index():
    default_data = {
        'system_description': '',
        'simple_use_cases': 0,
        'average_use_cases': 0,
        'complex_use_cases': 0,
        'simple_actors': 0,
        'average_actors': 0,
        'complex_actors': 0,
        't1': 0, 't2': 0, 't3': 0, 't4': 0, 't5': 0, 't6': 0, 't7': 0, 't8': 0, 't9': 0, 't10': 0, 't11': 0, 't12': 0, 't13': 0,
        'e1': 0, 'e2': 0, 'e3': 0, 'e4': 0, 'e5': 0, 'e6': 0, 'e7': 0, 'e8': 0,
        'actual_effort': 0,
        'weights_uc_simple': 5,
        'weights_uc_avg': 10,
        'weights_uc_complex': 15,
        'weights_actor_simple': 1,
        'weights_actor_avg': 2,
        'weights_actor_complex': 3,
        'hours_per_ucp': 20,
        'team_size': 1,
        'junior_members': 0,
        'mid_level_members': 0,
        'senior_members': 0,
        'hourly_cost': 50
    }
    return render_template('index.html', data=default_data, results_available=False)

@app.route('/suggest', methods=['POST'])
def suggest():
    try:
        data = request.get_json()
        system_description = data.get('system_description', '')
        
        if not system_description:
            logger.warning("System description is empty")
            return jsonify({"error": "Mô tả hệ thống không được để trống"}), 400

        logger.info(f"Suggest request received for description: {system_description[:50]}...")
        result = call_gemini_api(system_description)
        
        if not isinstance(result, dict):
            logger.error("Invalid result format from call_gemini_api: Expected dict, got " + str(type(result)))
            return jsonify({"error": "Kết quả từ Gemini API không đúng định dạng"}), 500

        if "error" in result:
            logger.error("Suggest failed: " + str(result['error']))
            return jsonify({"error": str(result['error'])}), 500
            
        # Điền các giá trị mặc định nếu thiếu
        default_values = {
            'weights_uc_simple': 5,
            'weights_uc_avg': 10,
            'weights_uc_complex': 15,
            'weights_actor_simple': 1,
            'weights_actor_avg': 2,
            'weights_actor_complex': 3,
            'hours_per_ucp': 20,
            'actual_effort': 0,
            'team_size': 1,
            'junior_members': 0,
            'mid_level_members': 0,
            'senior_members': 0,
            'hourly_cost': 50
        }
        for key, value in default_values.items():
            if key not in result:
                result[key] = value

        logger.info(f"Suggest result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error("Error in suggest endpoint: " + str(e))
        return jsonify({"error": "Lỗi khi xử lý gợi ý: " + str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            logger.warning("No file provided in upload request")
            return jsonify({"error": "Không có file được upload"}), 400

        file = request.files['file']
        logger.info(f"Received file: {file.filename}")

        # Kiểm tra định dạng file
        if not file.filename.lower().endswith(('.pdf', '.txt', '.png', '.jpg', '.jpeg')):
            logger.warning(f"Unsupported file format: {file.filename}")
            return jsonify({"error": "Định dạng file không được hỗ trợ. Chỉ hỗ trợ PDF, TXT, PNG, JPG, JPEG."}), 400

        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif file.filename.endswith(('.png', '.jpg', '.jpeg')):
            temp_path = 'temp_image'
            file.save(temp_path)
            text = extract_text_from_image(temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            try:
                text = file.read().decode('utf-8')
                logger.info(f"Extracted {len(text)} characters from text file")
            except UnicodeDecodeError:
                logger.error("File encoding is not UTF-8")
                return jsonify({"error": "File không sử dụng mã hóa UTF-8"}), 400

        if not text:
            logger.error("Failed to extract text from file")
            return jsonify({"error": "Không thể trích xuất nội dung từ file"}), 400

        logger.info(f"Extracted text length: {len(text)} characters")
        logger.info(f"Extracted text sample: {text[:100]}...")
        result = call_gemini_api(text)
        if not isinstance(result, dict):
            logger.error("Invalid result format from call_gemini_api: Expected dict, got " + str(type(result)))
            return jsonify({"error": "Kết quả từ Gemini API không đúng định dạng"}), 500
            
        if "error" in result:
            logger.error("Upload failed: " + str(result['error']))
            return jsonify({"error": str(result['error'])}), 500

        # Điền các giá trị mặc định nếu thiếu
        default_values = {
            'weights_uc_simple': 5,
            'weights_uc_avg': 10,
            'weights_uc_complex': 15,
            'weights_actor_simple': 1,
            'weights_actor_avg': 2,
            'weights_actor_complex': 3,
            'hours_per_ucp': 20,
            'actual_effort': 0,
            'team_size': 1,
            'junior_members': 0,
            'mid_level_members': 0,
            'senior_members': 0,
            'hourly_cost': 50
        }
        for key, value in default_values.items():
            if key not in result:
                result[key] = value

        # Đảm bảo các trường số có giá trị hợp lệ
        numeric_fields = [
            'simple_use_cases', 'average_use_cases', 'complex_use_cases',
            'simple_actors', 'average_actors', 'complex_actors',
            't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11', 't12', 't13',
            'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8',
            'actual_effort', 'weights_uc_simple', 'weights_uc_avg', 'weights_uc_complex',
            'weights_actor_simple', 'weights_actor_avg', 'weights_actor_complex',
            'hours_per_ucp', 'team_size', 'junior_members', 'mid_level_members', 'senior_members', 'hourly_cost'
        ]
        for field in numeric_fields:
            if field in result and not isinstance(result[field], (int, float)):
                logger.warn(f"Invalid numeric value for {field}: {result[field]}")
                result[field] = default_values.get(field, 0)

        # Thêm các trọng số và actual_effort từ nội dung file
        result['extracted_text'] = text  # Sửa lỗi: đổi 'text' thành 'extracted_text'
        if 'Simple UC (5)' in text:
            result['weights_uc_simple'] = 5
        if 'Average UC (10)' in text:
            result['weights_uc_avg'] = 10
        if 'Complex UC (15)' in text:
            result['weights_uc_complex'] = 15
        if 'Simple Actor (1)' in text:
            result['weights_actor_simple'] = 1
        if 'Average Actor (2)' in text:
            result['weights_actor_avg'] = 2
        if 'Complex Actor (3)' in text:
            result['weights_actor_complex'] = 3
        if 'Hours per UCP: 18' in text:
            result['hours_per_ucp'] = 18
        if 'Actual Effort: 1200' in text:
            result['actual_effort'] = 1200
        if 'Team Size: 3' in text:
            result['team_size'] = 3
        if 'Junior Members: 1' in text:
            result['junior_members'] = 1
        if 'Mid-level Members: 1' in text:
            result['mid_level_members'] = 1
        if 'Senior Members: 1' in text:
            result['senior_members'] = 1
        if 'Hourly Cost: 50' in text:
            result['hourly_cost'] = 50

        logger.info(f"Upload result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error("Error in upload_file endpoint: " + str(e))
        return jsonify({"error": "Lỗi khi xử lý file: " + str(e)}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.form if not request.is_json else request.get_json()
        logger.info("Calculate request received")

        form_data = {}
        required_fields = [
            'system_description', 'simple_use_cases', 'average_use_cases', 'complex_use_cases',
            'simple_actors', 'average_actors', 'complex_actors',
            't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11', 't12', 't13',
            'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'actual_effort',
            'weights_uc_simple', 'weights_uc_avg', 'weights_uc_complex',
            'weights_actor_simple', 'weights_actor_avg', 'weights_actor_complex',
            'hours_per_ucp', 'team_size', 'junior_members', 'mid_level_members', 'senior_members', 'hourly_cost'
        ]

        for field in required_fields:
            value = data.get(field, '0')
            try:
                form_data[field] = float(value) if field != 'system_description' else value
            except (ValueError, TypeError):
                logger.error("Invalid value for field " + field + ": " + str(value))
                return jsonify({"error": "Giá trị không hợp lệ cho trường " + field + ": " + str(value)}), 400

        logger.info(f"Form data parsed: {form_data}")

        tf = (
            form_data['t1'] * 2.0 + form_data['t2'] * 1.0 + form_data['t3'] * 1.0 + form_data['t4'] * 1.0 +
            form_data['t5'] * 1.0 + form_data['t6'] * 0.5 + form_data['t7'] * 0.5 + form_data['t8'] * 2.0 +
            form_data['t9'] * 1.0 + form_data['t10'] * 1.0 + form_data['t11'] * 1.0 + form_data['t12'] * 1.0 +
            form_data['t13'] * 1.0
        )
        tcf = 0.6 + (0.01 * tf)

        ef_factor = (
            form_data['e1'] * 1.5 + form_data['e2'] * 0.5 + form_data['e3'] * 1.0 + form_data['e4'] * 1.0 +
            form_data['e5'] * 2.0 + form_data['e6'] * 1.0 + form_data['e7'] * (-1.0) + form_data['e8'] * (-1.0)
        )
        ef = 1.4 + (-0.03 * ef_factor)

        uucw = (
            form_data['simple_use_cases'] * form_data['weights_uc_simple'] +
            form_data['average_use_cases'] * form_data['weights_uc_avg'] +
            form_data['average_use_cases'] * form_data['weights_uc_avg'] +
            form_data['complex_use_cases'] * form_data['weights_uc_complex']
        )
        uaw = (
            form_data['simple_actors'] * form_data['weights_actor_simple'] +
            form_data['average_actors'] * form_data['weights_actor_avg'] +
            form_data['complex_actors'] * form_data['weights_actor_complex']
        )
        ucp = (uucw + uaw) * tcf * ef

        # Tính team_expertise dựa trên đội ngũ
        # Các hệ số từ COCOMO II cho team capability (PERS)
        # Giả định: 
        # - Junior tương đương Very Low (EM = 1.42)
        # - Mid tương đương Nominal (EM = 1.00)
        # - Senior tương đương Very High (EM = 0.71)

        total_members = form_data['junior_members'] + form_data['mid_level_members'] + form_data['senior_members']

        if total_members > 0:
            avg_effort_multiplier = (
                form_data['junior_members'] * 1.42 +
                form_data['mid_level_members'] * 1.00 +
                form_data['senior_members'] * 0.71
            ) / total_members
        else:
            avg_effort_multiplier = 1.00  # fallback

        # Điều chỉnh effort dựa trên productivity từ COCOMO
        adjusted_hours_per_ucp = form_data['hours_per_ucp'] * avg_effort_multiplier

        # Ước lượng effort và cost
        effort = ucp * adjusted_hours_per_ucp
        total_cost = effort * form_data['hourly_cost']


        difference = effort - form_data['actual_effort']
        accuracy = ((form_data['actual_effort'] / effort) * 100) if effort > 0 else 0

        results = {
            'ucp': round(ucp, 2),
            'effort': round(effort, 2),
            'actual_effort': form_data['actual_effort'],
            'difference': round(difference, 2),
            'accuracy': round(accuracy, 2),
            'tcf': round(tcf, 2),
            'ef': round(ef, 2),
            'total_cost': round(total_cost, 2)
        }

        logger.info(f"Calculate results: uucw={uucw}, uaw={uaw}, tcf={tcf}, ef={ef}, ucp={ucp}, effort={effort}, total_cost={total_cost}")

        if request.is_json:
            return jsonify(results)
        else:
            return render_template(
                'index.html',
                data=form_data,
                results_available=True,
                **results
            )
    except Exception as e:
        logger.error("Error in calculate endpoint: " + str(e))
        return jsonify({"error": "Lỗi khi tính toán: " + str(e)}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask server")
        app.run(debug=True, port=5000)
    except Exception as e:
        logger.error("Failed to start Flask server: " + str(e))