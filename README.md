Máy Tính Use Case Points (UCP)
Mô tả dự án
Máy Tính Use Case Points (UCP) là một ứng dụng web được xây dựng để hỗ trợ ước lượng công sức phát triển phần mềm dựa trên phương pháp Use Case Points. Ứng dụng cho phép người dùng nhập mô tả hệ thống, upload tài liệu (PDF, TXT, hoặc hình ảnh), và tự động phân tích để đưa ra các thông số UCP như số lượng use cases, actors, yếu tố kỹ thuật, yếu tố môi trường, và đội ngũ phát triển. Kết quả bao gồm công sức ước lượng, chi phí, và độ chính xác so với công sức thực tế.
Ứng dụng sử dụng Flask làm backend, tích hợp API Gemini để phân tích văn bản tự nhiên, và giao diện người dùng được xây dựng với HTML, CSS, JavaScript, cùng với các thư viện Chart.js và i18next để hỗ trợ biểu đồ và đa ngôn ngữ (Tiếng Việt và Tiếng Anh).
Tính năng chính

Nhập mô tả hệ thống: Người dùng có thể nhập mô tả hệ thống và nhận gợi ý về các thông số UCP thông qua API Gemini.
Upload tài liệu: Hỗ trợ upload file PDF, TXT, hoặc hình ảnh (PNG, JPG, JPEG) để trích xuất và phân tích nội dung tự động.
Tính toán UCP: Tính toán điểm UCP, công sức ước lượng (giờ), chi phí (USD), và độ chính xác dựa trên công sức thực tế.
Tùy chỉnh trọng số: Cho phép tùy chỉnh trọng số cho use cases, actors, và số giờ mỗi UCP.
Hỗ trợ đa ngôn ngữ: Giao diện hỗ trợ Tiếng Việt và Tiếng Anh với i18next.
Trực quan hóa kết quả: Hiển thị kết quả dưới dạng biểu đồ cột sử dụng Chart.js.
Lưu trữ dữ liệu: Lưu trữ dữ liệu form vào localStorage để khôi phục khi tải lại trang.

Yêu cầu hệ thống

Python: 3.8 trở lên
Trình duyệt web: Chrome, Firefox, hoặc Edge (phiên bản mới nhất)
Kết nối internet: Yêu cầu để gọi API Gemini
Hệ điều hành: Windows, macOS, hoặc Linux

Cài đặt
1. Cài đặt môi trường

Clone repository:
git clone <repository-url>
cd ucp-calculator


Cài đặt Python và pip:Đảm bảo Python 3.8+ và pip đã được cài đặt. Kiểm tra phiên bản:
python --version
pip --version


Tạo môi trường ảo:
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows


Cài đặt các thư viện cần thiết:
pip install flask requests PyPDF2 textract python-dotenv json-repair

Lưu ý: Để sử dụng textract cho trích xuất văn bản từ hình ảnh, bạn cần cài đặt Tesseract OCR:

Windows: Tải và cài đặt Tesseract từ đây. Thêm Tesseract vào biến môi trường PATH.
Linux: sudo apt-get install tesseract-ocr


macOS:brew install tesseract




Cấu hình API Gemini:

Tạo tệp .env trong thư mục gốc của dự án.
Thêm API key của Gemini:GEMINI_API_KEY=your_api_key_here


Để lấy API key, đăng ký tại Google Cloud Console và kích hoạt Gemini API.



2. Cấu trúc thư mục
ucp-calculator/
├── static/
│   ├── css/
│   │   └── styles.css      # CSS cho giao diện
├── templates/
│   └── index.html          # Giao diện chính
├── app.py                  # Backend Flask
├── .env                    # Biến môi trường (API key)
├── README.md               # Tài liệu hướng dẫn
└── requirements.txt        # Danh sách thư viện Python

3. Chạy ứng dụng

Đảm bảo môi trường ảo đã được kích hoạt.
Chạy server Flask:python app.py


Mở trình duyệt và truy cập: http://localhost:5000

Sử dụng

Nhập mô tả hệ thống:

Nhập mô tả ngắn gọn về hệ thống vào ô "Mô tả hệ thống".
Nhấn nút "Gợi ý" để nhận các thông số UCP được phân tích tự động.


Upload tài liệu:

Chọn tệp PDF, TXT, hoặc hình ảnh (PNG, JPG, JPEG).
Nhấn "指標
Nhấn nút "Upload & Phân tích" để trích xuất và phân tích nội dung.


Tùy chỉnh thông số:

Điều chỉnh số lượng use cases, actors, yếu tố kỹ thuật/môi trường, trọng số, và thông tin đội ngũ theo nhu cầu.
Nhập công sức thực tế (giờ) để so sánh với ước lượng.


Tính toán UCP:

Nhấn nút "Tính UCP" để nhận kết quả ước lượng, bao gồm UCP, công sức, chi phí, và độ chính xác.
Kết quả sẽ được hiển thị dưới dạng biểu đồ và số liệu.


Reset:

Nhấn nút "Reset" để xóa toàn bộ dữ liệu và đặt lại các giá trị mặc định.



API
Ứng dụng sử dụng Gemini API để phân tích văn bản. Đảm bảo rằng tệp .env chứa GEMINI_API_KEY hợp lệ. API được gọi trong các endpoint /suggest và /upload để phân tích mô tả hệ thống hoặc nội dung tài liệu.
Góp phần phát triển

Fork repository và tạo branch cho tính năng mới:git checkout -b feature-name


Commit thay đổi và tạo pull request:git commit -m "Mô tả thay đổi"
git push origin feature-name


Liên hệ với maintainer để xem xét pull request.

Giấy phép
Dự án được phát hành theo Giấy phép MIT.
Liên hệ
Nếu có thắc mắc hoặc cần hỗ trợ, liên hệ qua email: [your-email@example.com] hoặc tạo issue trên GitHub.
Tác giả

[Tên của bạn] - [Liên kết GitHub hoặc email]


Ngày cập nhật cuối: 19/05/2025
