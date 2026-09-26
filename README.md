# 📚 AI-Integrated JSON Parser using Gemini API for HTML Test Bank Manager 🤖

**AI-Integrated JSON Parser using Gemini API for HTML Test Bank Manager** là ứng dụng desktop dựa trên giao diện đồ họa PyQt6 và tích hợp Google GenAI (Gemini API), giúp chuyển đổi hình ảnh câu hỏi trắc nghiệm hoặc văn bản thô thành định dạng JSON chuẩn hóa theo template HTML của hệ thống ngân hàng câu hỏi.

* **Ứng dụng này hỗ trợ cho dự án:** [HTML Test Bank Manager](https://github.com/kienma11vn/HTML-Test-Bank-Manager-VN)

---

## 🌟 Tính năng chính

* **OCR & Giải bài tập bằng AI**: Tải lên tối đa **5 ảnh** câu hỏi (bằng cách chọn file hoặc bấm `Ctrl+V` để dán trực tiếp từ clipboard) và tự động nhận diện, giải câu hỏi sang dạng text.
* **Xem trước ảnh thông minh**: Quản lý danh sách thumbnail trực quan, hỗ trợ tự động phóng to tối đa 80% kích thước màn hình khi di chuột qua ảnh (hover).
* **Chuyển đổi Text sang JSON**: Dựa vào file HTML mẫu được tải lên, AI sẽ phân tích cú pháp câu hỏi và phản hồi đúng chuẩn cấu trúc JSON.
* **Quản lý Cấu hình (Presets)**: Hỗ trợ lưu trữ lên đến **30 Presets** cài đặt bao gồm API Key và mô hình Gemini (ví dụ: `gemini-2.5-flash`, `gemini-2.5-pro`).
* **Xử lý bất đồng bộ (Multi-threading)**: Đảm bảo giao diện người dùng (GUI) luôn mượt mà, không bị treo/đơ trong quá trình chờ AI phản hồi.

---

## 🛠️ Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống

* Python 3.9 trở lên.

### 2. Cài đặt các thư viện phụ thuộc

Mở *Terminal* hoặc *Command Prompt* tại thư mục dự án và chạy lệnh:

```bash
pip install -r requirements.txt
```

---

## 🚀 Hướng dẫn sử dụng

### Khởi chạy ứng dụng:

```bash
python app.py
```

### Cấu hình Gemini API Key:

- Bấm vào nút **⚙️ Cài đặt AI** ở góc trên bên phải.

- Chọn *Preset* phù hợp, nhập `AI API KEY` và `AI MODEL` (ví dụ: gemini-3.6-flash), sau đó nhấn **OK**.

- Chọn *File HTML Mẫu*: Bấm nút **📂 Chọn File HTML mẫu** để tải template chứa cấu trúc câu hỏi mong muốn.

- Trích xuất dữ liệu từ hình ảnh:

	- Tải ảnh lên hoặc nhấn Ctrl+V để dán ảnh chụp màn hình.

	- Bấm **Giải câu hỏi và chuyển đổi hình ảnh sang dạng Text ➡️**.

- Xuất dữ liệu JSON:

	- Kiểm tra/chỉnh sửa đoạn văn bản câu hỏi thu được.

	- Bấm **Chuyển đổi ➡️** tại mục *Text*.

	- Dữ liệu JSON chuẩn hóa sẽ xuất hiện ở cột bên phải. Nhấn **📋 Sao chép JSON** để sử dụng.

---

## 📂 Cấu trúc thư mục

```plaintext
.
├── app.py              # Mã nguồn chính của ứng dụng
├── requirements.txt    # Danh sách thư viện cần thiết
├── image.ico           # Biểu tượng icon ứng dụng
└── README.md           # Tài liệu hướng dẫn dự án
```

## 📦 Đóng gói ứng dụng thành file thực thi (.EXE)

Bạn có thể đóng gói ứng dụng thành file `.exe` chạy độc lập bằng **PyInstaller**:

1. Cài đặt PyInstaller:
```bash
pip install pyinstaller
```

2. Chạy lệnh đóng gói (kèm file icon `image.ico`):
```bash
pyinstaller --noconfirm --onefile --windowed --icon=image.ico app.py
```

3. File thực thi sẽ nằm trong thư mục `dist/`.

```text
dist/
└── app.exe    # File thực thi có thể chia sẻ và chạy trực tiếp
```

---

## 📝 Giấy phép (License)
Dự án này được phân phối dưới giấy phép **MIT License** dưới dạng mã nguồn tự do, phục vụ mục đích giáo dục và học tập.
