# Máy Tính Use Case Points (UCP) Nâng Cao với Gợi ý AI

Dự án này là một ứng dụng web được xây dựng bằng Flask (Python) cho backend và HTML/CSS/JavaScript cho frontend, cho phép người dùng ước tính nỗ lực phát triển phần mềm bằng phương pháp Use Case Points (UCP). Điểm đặc biệt của ứng dụng là khả năng tích hợp với Google Gemini API để cung cấp các gợi ý thông minh cho các tham số UCP dựa trên mô tả hệ thống hoặc nội dung tài liệu được tải lên.

## Mục lục

* [Giới thiệu](#giới-thiệu)
* [Tính năng](#tính-năng)
* [Công nghệ sử dụng](#công-nghệ-sử-dụng)
* [Điều kiện tiên quyết](#điều-kiện-tiên-quyết)
* [Cài đặt và Khởi chạy](#cài-đặt-và-khởi-chạy)
    * [Thiết lập Backend (Flask)](#thiết-lập-backend-flask)
    * [Cấu hình Biến môi trường](#cấu-hình-biến-môi-trường)
* [Cách sử dụng](#cách-sử-dụng)
    * [Nhập liệu thủ công](#nhập-liệu-thủ-công)
    * [Sử dụng tính năng Gợi ý AI](#sử-dụng-tính-năng-gợi-ý-ai)
    * [Tải lên và Phân tích Tài liệu](#tải-lên-và-phân-tích-tài-liệu)
    * [Tính toán UCP](#tính-toán-ucp)
    * [Xem kết quả](#xem-kết-quả)
    * [Đa ngôn ngữ](#đa-ngôn-ngữ)
* [Cấu trúc Dự án](#cấu-trúc-dự-án)
* [Chi tiết Kỹ thuật](#chi-tiết-kỹ-thuật)
    * [Tính toán UCP](#tính-toán-ucp-1)
    * [Tích hợp Gemini API](#tích-hợp-gemini-api)
    * [Trích xuất văn bản](#trích-xuất-văn-bản)
    * [Xử lý lỗi và Dự phòng](#xử-lý-lỗi-và-dự-phòng)

## Giới thiệu

Ước tính nỗ lực phần mềm là một bước quan trọng trong quản lý dự án. Phương pháp Use Case Points (UCP) cung cấp một cách tiếp cận dựa trên các trường hợp sử dụng của hệ thống để định lượng kích thước và từ đó ước tính nODE lực. Ứng dụng này không chỉ tự động hóa các phép tính UCP mà còn sử dụng trí tuệ nhân tạo để hỗ trợ người dùng trong việc xác định các tham số đầu vào, giúp quá trình ước tính nhanh chóng và có khả năng chính xác hơn, đặc biệt khi thông tin ban đầu còn hạn chế.

## Tính năng

* **Nhập liệu UCP chi tiết:** Cho phép nhập số lượng Use Cases (Đơn giản, Trung bình, Phức tạp), Actors (Đơn giản, Trung bình, Phức tạp).
* **Hệ số Kỹ thuật (TCF):** Nhập liệu 13 Yếu tố Kỹ thuật (T1-T13) với thang điểm từ 0-5.
* **Hệ số Môi trường (EF):** Nhập liệu 8 Yếu tố Môi trường (E1-E8) với thang điểm từ 0-5.
* **Tùy chỉnh Trọng số:** Cho phép người dùng tùy chỉnh trọng số cho các loại Use Case, Actor và số giờ mỗi UCP.
* **Yếu tố Đội ngũ & Chi phí:**
    * Nhập thông tin về kích thước đội ngũ (tổng số, junior, mid-level, senior).
    * Nhập chi phí trung bình mỗi giờ.
    * Điều chỉnh nỗ lực dựa trên kinh nghiệm trung bình của đội ngũ (lấy cảm hứng từ hệ số của COCOMO II).
* **Gợi ý AI (Google Gemini):**
    * Cung cấp gợi ý cho tất cả các tham số UCP, yếu tố kỹ thuật, môi trường, và đội ngũ dựa trên mô tả hệ thống bằng ngôn ngữ tự nhiên.
    * Hiển thị ghi chú phân loại từ AI giải thích cách các giá trị được đề xuất.
* **Phân tích Tài liệu:**
    * Hỗ trợ tải lên file PDF, TXT, PNG, JPG, JPEG.
    * Tự động trích xuất văn bản từ các định dạng file này.
    * Sử dụng văn bản được trích xuất để yêu cầu gợi ý từ Gemini API.
    * Hiển thị văn bản đã trích xuất.
* **Tính toán và Hiển thị Kết quả:**
    * Tính toán Unadjusted Use Case Weight (UUCW), Unadjusted Actor Weight (UAW).
    * Tính toán Technical Complexity Factor (TCF), Environmental Factor (EF).
    * Tính toán Use Case Points (UCP).
    * Ước tính Tổng Nỗ lực (giờ) và Tổng Chi phí (USD).
    * So sánh Nỗ lực Ước tính với Nỗ lực Thực tế (nếu được cung cấp) để tính toán Độ lệch và Độ chính xác.
    * Hiển thị kết quả trực quan bằng biểu đồ cột (Estimated Effort vs Actual Effort) sử dụng Chart.js.
* **Đa ngôn ngữ:** Hỗ trợ Tiếng Việt (mặc định) và Tiếng Anh, có thể chuyển đổi dễ dàng.
* **Lưu trữ cục bộ:** Tự động lưu trữ dữ liệu form vào LocalStorage và khôi phục khi tải lại trang (trừ khi dữ liệu vừa được cập nhật từ file upload).
* **Giao diện người dùng:**
    * Thiết kế đáp ứng (responsive).
    * Tooltip cung cấp thông tin giải thích cho từng trường nhập liệu.
    * Thông báo trạng thái (loading, error) rõ ràng.
    * Nút Reset để xóa toàn bộ form về giá trị mặc định.

## Công nghệ sử dụng

* **Backend:**
    * Python 3.x
    * Flask: Web framework.
    * Requests: Thư viện HTTP để gọi Gemini API.
    * PyPDF2: Trích xuất văn bản từ file PDF.
    * Textract: Trích xuất văn bản từ hình ảnh (sử dụng Tesseract OCR) và các định dạng khác.
    * python-dotenv: Quản lý biến môi trường.
    * json-repair: Sửa lỗi JSON không hợp lệ từ API response.
* **Frontend:**
    * HTML5
    * CSS3 (Giả định có file `static/css/styles.css`)
    * JavaScript (ES6+)
    * Chart.js: Vẽ biểu đồ.
    * i18next: Hỗ trợ đa ngôn ngữ.
* **API Bên ngoài:**
    * Google Gemini API (Cụ thể là model `gemini-2.0-flash`): Cho tính năng gợi ý AI.

## Điều kiện tiên quyết

Trước khi chạy ứng dụng, bạn cần cài đặt:

* Python 3.7 trở lên.
* Pip (Trình quản lý gói cho Python).
* Tesseract OCR: Cần thiết cho `textract` để xử lý file hình ảnh.
    * **Windows:** Tải và cài đặt từ [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). Đảm bảo thêm đường dẫn cài đặt Tesseract vào biến môi trường PATH.
    * **macOS:** `brew install tesseract`
    * **Linux (Ubuntu/Debian):** `sudo apt-get install tesseract-ocr libtesseract-dev`
* (Có thể cần) Các thư viện hệ thống khác tùy thuộc vào hệ điều hành của bạn để `textract` và `PyPDF2` hoạt động chính xác (ví dụ: `antiword` cho file .doc, `pdftotext` cho một số PDF).

## Cài đặt và Khởi chạy

### Thiết lập Backend (Flask)

1.  **Clone Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Tạo và Kích hoạt Môi trường ảo (Khuyến nghị):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Cài đặt các Dependencies:**
    Tạo file `requirements.txt` với nội dung sau:
    ```txt
    Flask
    requests
    PyPDF2
    textract
    python-dotenv
    json-repair
    # Thêm các thư viện khác nếu có
    ```
    Sau đó chạy:
    ```bash
    pip install -r requirements.txt
    ```

### Cấu hình Biến môi trường

1.  Tạo một file tên là `.env` trong thư mục gốc của dự án.
2.  Thêm khóa API của Google Gemini vào file `.env`:
    ```env
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    Thay thế `"YOUR_GEMINI_API_KEY"` bằng khóa API thực của bạn.

### Khởi chạy ứng dụng

1.  Chạy ứng dụng Flask:
    ```bash
    python app.py
    ```
2.  Mở trình duyệt và truy cập `http://127.0.0.1:5000/`.

## Cách sử dụng

Giao diện người dùng được chia thành nhiều phần trực quan:

### Nhập liệu thủ công

* **Mô tả hệ thống:** Nhập mô tả ngắn gọn về hệ thống của bạn. Trường này được sử dụng cho tính năng Gợi ý AI.
* **Use Cases & Actors:** Nhập số lượng use case và actor tương ứng với các mức độ phức tạp (Simple, Average, Complex).
* **Yếu tố Kỹ thuật (T1-T13):** Đánh giá từng yếu tố từ 0 (không quan trọng/không áp dụng) đến 5 (rất quan trọng).
* **Yếu tố Môi trường (E1-E8):** Đánh giá từng yếu tố từ 0 đến 5.
* **Actual Effort:** Nhập số giờ nỗ lực thực tế (nếu có) để so sánh và đánh giá độ chính xác của ước tính.
* **Tùy chỉnh trọng số:** Điều chỉnh các trọng số mặc định cho use case, actor và số giờ/UCP nếu cần.
* **Yếu tố Đội ngũ:** Nhập thông tin về số lượng thành viên trong đội, số lượng thành viên theo kinh nghiệm (Junior, Mid-level, Senior), và chi phí trung bình mỗi giờ.

### Sử dụng tính năng Gợi ý AI

1.  Nhập mô tả chi tiết về hệ thống vào ô "Mô tả hệ thống".
2.  Nhấn nút "Gợi ý".
3.  Ứng dụng sẽ gửi mô tả đến Gemini API.
4.  Các trường nhập liệu (Use Cases, Actors, Yếu tố Kỹ thuật, Môi trường, Đội ngũ) sẽ được tự động điền với các giá trị gợi ý từ AI.
5.  Một "Ghi chú phân loại" từ AI có thể được hiển thị, giải thích logic đằng sau các gợi ý.
6.  Sau khi nhận gợi ý, ứng dụng sẽ tự động tính toán UCP.

### Tải lên và Phân tích Tài liệu

1.  Nhấn vào "Choose File" trong phần "Upload Tài liệu" để chọn một file (PDF, TXT, PNG, JPG, JPEG).
2.  Nhấn nút "Upload & Phân tích".
3.  Văn bản sẽ được trích xuất từ file và hiển thị trong ô `textarea` bên dưới.
4.  Văn bản này sau đó được gửi đến Gemini API để nhận gợi ý, tương tự như tính năng "Gợi ý".
5.  Các trường sẽ được cập nhật và UCP sẽ được tự động tính toán.

### Tính toán UCP

Sau khi tất cả các trường cần thiết đã được điền (thủ công, qua gợi ý AI, hoặc qua phân tích tài liệu), nhấn nút "Tính UCP". Nếu tính năng gợi ý hoặc upload được sử dụng, việc tính toán sẽ diễn ra tự động sau khi nhận được dữ liệu từ AI.

### Xem kết quả

Phần "Kết quả ước lượng" sẽ hiển thị:

* Total UCP
* Estimated Effort (giờ)
* Total Cost (USD)
* Technical Complexity Factor (TCF)
* Environmental Factor (EF)
* Actual Effort (nếu đã nhập)
* Difference (so với Actual Effort)
* Estimation Accuracy (%)
* Biểu đồ cột so sánh Estimated Effort và Actual Effort.

### Đa ngôn ngữ

Chọn ngôn ngữ (Tiếng Việt hoặc English) từ menu dropdown ở góc trên bên phải để thay đổi ngôn ngữ hiển thị của toàn bộ trang.

## Cấu trúc Dự án
├── app.py                    # Logic backend Flask
├── templates/
│   └── index.html            # Template HTML cho giao diện người dùng
├── static/
│   └── css/
│       └── styles.css        # (Giả định) File CSS cho styling
├── .env                      # File chứa biến môi trường (ví dụ: GEMINI_API_KEY)
├── requirements.txt          # Danh sách các thư viện Python cần thiết
└── README.md                 # Tài liệu này

## Chi tiết Kỹ thuật

### Tính toán UCP

Công thức tính toán UCP được triển khai trong route `/calculate` của `app.py`:

1.  **Unadjusted Use Case Weight (UUCW):**
    `UUCW = (simple_uc * weight_simple_uc) + (average_uc * weight_avg_uc) + (complex_uc * weight_complex_uc)`
2.  **Unadjusted Actor Weight (UAW):**
    `UAW = (simple_actor * weight_simple_actor) + (average_actor * weight_avg_actor) + (complex_actor * weight_complex_actor)`
3.  **Technical Complexity Factor (TCF):**
    `TF = sum(Ti_value * Ti_weight)` (với T1-T13 và trọng số tương ứng của chúng)
    `TCF = 0.6 + (0.01 * TF)`
4.  **Environmental Factor (EF):**
    `EF_Factor = sum(Ei_value * Ei_weight)` (với E1-E8 và trọng số tương ứng của chúng)
    `EF = 1.4 + (-0.03 * EF_Factor)`
5.  **Use Case Points (UCP):**
    `UCP = (UUCW + UAW) * TCF * EF`
6.  **Adjusted Hours per UCP:**
    Số giờ mỗi UCP (`hours_per_ucp`) được điều chỉnh dựa trên kinh nghiệm trung bình của đội ngũ:
    `avg_effort_multiplier = (junior_members * 1.42 + mid_level_members * 1.00 + senior_members * 0.71) / total_members`
    `adjusted_hours_per_ucp = hours_per_ucp * avg_effort_multiplier`
    (Hệ số 1.42, 1.00, 0.71 được lấy cảm hứng từ các hệ số PERS trong COCOMO II cho năng lực đội ngũ).
7.  **Estimated Effort:**
    `Effort = UCP * adjusted_hours_per_ucp`
8.  **Total Cost:**
    `Total_Cost = Effort * hourly_cost`

### Tích hợp Gemini API

* Ứng dụng sử dụng Gemini API (model `gemini-2.0-flash`) để phân tích mô tả hệ thống hoặc văn bản trích xuất.
* Một prompt chi tiết được gửi đến API, yêu cầu trả về kết quả dưới dạng JSON với cấu trúc cụ thể bao gồm các trường UCP, yếu tố kỹ thuật/môi trường, thông tin đội ngũ, và ghi chú phân loại.
* Hàm `call_gemini_api` trong `app.py` xử lý việc gửi request và nhận response.

### Trích xuất văn bản

* `extract_text_from_pdf(file)`: Sử dụng `PyPDF2` để đọc nội dung văn bản từ các trang của file PDF.
* `extract_text_from_image(file_path)`: Sử dụng `textract` (với Tesseract OCR) để trích xuất văn bản từ file hình ảnh. Hàm này cũng thử nhiều encoding khác nhau để đảm bảo văn bản được giải mã chính xác.
* File TXT được đọc trực tiếp và giải mã bằng UTF-8.

### Xử lý lỗi và Dự phòng

* **API Key:** Kiểm tra sự tồn tại của `GEMINI_API_KEY`.
* **File Upload:** Kiểm tra định dạng file, sự tồn tại của file.
* **Trích xuất văn bản:** Xử lý lỗi nếu không thể trích xuất văn bản.
* **Gemini API Response:**
    * Kiểm tra status code của response.
    * Cố gắng parse JSON. Nếu thất bại, sử dụng `json_repair.loads()` để thử sửa lỗi JSON.
    * Nếu việc sửa lỗi JSON cũng thất bại, ứng dụng có một cơ chế **fallback parsing** (`fallback_parse_content`). Hàm này cố gắng trích xuất thông tin cơ bản từ văn bản thô bằng cách sử dụng biểu thức chính quy (regex) để tìm các từ khóa liên quan đến use case, actor, và các yếu tố kỹ thuật/môi trường. Đây là một giải pháp dự phòng khi Gemini API trả về định dạng không mong muốn hoặc không phải JSON.
* **Giao diện người dùng:** Hiển thị thông báo lỗi cho người dùng khi có sự cố.
