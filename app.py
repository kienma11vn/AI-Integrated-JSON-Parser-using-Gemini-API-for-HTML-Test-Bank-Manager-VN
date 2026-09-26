import os
import json
import sys
import tempfile
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QImage, QPixmap, QKeySequence, QShortcut, QFont
from PyQt6.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, 
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QComboBox,
    QPushButton, QSplitter, QTextEdit, QVBoxLayout, QWidget, QScrollArea, QGridLayout
)
from PIL import Image
from google import genai  # Cập nhật SDK mới

# ==========================================
# LUỒNG XỬ LÝ AI DƯỚI NỀN (Tránh đơ giao diện)
# ==========================================
class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, api_key, model_name, prompt, image_paths=None, html_content=None):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.prompt = prompt
        self.image_paths = image_paths if image_paths else []
        self.html_content = html_content

    def run(self):
        try:
            if not self.api_key:
                raise ValueError("Vui lòng nhập AI API Key trong phần Cài đặt.")
            
            # Khởi tạo Client theo cú pháp của thư viện google-genai mới
            client = genai.Client(api_key=self.api_key)
            
            contents = [self.prompt]
            
            # Xử lý duyệt qua danh sách các ảnh
            for path in self.image_paths:
                img = Image.open(path)
                contents.append(img)
            
            if self.html_content:
                contents.append(f"\n--- HTML Template Mẫu ---\n{self.html_content}")

            # Khởi tạo phiên Chat và gửi tin nhắn bằng send_message theo khuyến nghị SDK
            chat = client.chats.create(model=self.model_name)
            response = chat.send_message(contents)
            self.finished.emit(response.text)
        except Exception as e:
            # Phân tách rõ ràng tên loại lỗi và nội dung chi tiết trên các dòng riêng biệt
            error_details = f"Loại lỗi: {type(e).__name__}\n\nNội dung chi tiết:\n{str(e)}"
            self.error.emit(error_details)


# ==========================================
# DIALOG CÀI ĐẶT AI
# ==========================================
class SettingsDialog(QDialog):
    def __init__(self, parent=None, api_key="", model_name="gemini-2.5-flash"):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Cài đặt AI")
        self.resize(450, 200)
        self.settings = QSettings("MyApp", "JSON_Converter_AI")
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # 1. Mục lựa chọn Preset (Tối đa 30 Preset)
        self.cmb_presets = QComboBox()
        for i in range(1, 31):
            self.cmb_presets.addItem(f"Preset {i}")
            
        self.current_preset_index = self.settings.value("selected_preset", 0, type=int)
        
        # 2. Ô nhập API Key + Nút Hiển thị / Ẩn
        self.txt_api_key = QLineEdit(api_key)
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("Nhập AI API Key...")
        
        self.btn_toggle_key = QPushButton("🔓 Hiển thị")
        self.btn_toggle_key.setCheckable(True)
        self.btn_toggle_key.clicked.connect(self.toggle_api_key_visibility)
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.txt_api_key)
        api_key_layout.addWidget(self.btn_toggle_key)
        
        # 3. Ô nhập Model Name
        self.txt_model = QLineEdit(model_name)
        self.txt_model.setPlaceholderText("VD: gemini-2.5-flash, gemini-2.5-pro")
        
        form.addRow("Chọn Preset:", self.cmb_presets)
        form.addRow("AI API KEY:", api_key_layout)
        form.addRow("AI MODEL:", self.txt_model)
        
        layout.addLayout(form)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.save_and_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        # Tải dữ liệu Preset hiện tại và kết nối sự kiện thay đổi Preset
        self.cmb_presets.setCurrentIndex(self.current_preset_index)
        self.load_preset_data(self.current_preset_index)
        self.cmb_presets.currentIndexChanged.connect(self.on_preset_changed)

    def toggle_api_key_visibility(self):
        """Bật/Tắt ẩn hiện AI API KEY"""
        if self.btn_toggle_key.isChecked():
            self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_key.setText("🔒 Ẩn")
        else:
            self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_key.setText("🔓 Hiển thị")

    def on_preset_changed(self, new_index):
        """Lưu preset cũ và tải preset mới khi chuyển đổi trên ComboBox"""
        self.save_preset_data(self.current_preset_index)
        self.current_preset_index = new_index
        self.load_preset_data(new_index)

    def load_preset_data(self, index):
        """Đọc thông tin API Key và Model từ QSettings theo từng Preset"""
        key = self.settings.value(f"preset_{index}_key", "")
        model = self.settings.value(f"preset_{index}_model", "gemini-3.6-flash")
        
        # Nếu preset trống, giữ lại giá trị mặc định truyền từ MainWindow
        if key:
            self.txt_api_key.setText(key)
        if model:
            self.txt_model.setText(model)

    def save_preset_data(self, index):
        """Lưu thông tin Preset vào QSettings"""
        self.settings.setValue(f"preset_{index}_key", self.txt_api_key.text().strip())
        self.settings.setValue(f"preset_{index}_model", self.txt_model.text().strip())

    def save_and_accept(self):
        """Lưu Preset hiện tại và đóng Dialog"""
        self.save_preset_data(self.current_preset_index)
        self.settings.setValue("selected_preset", self.current_preset_index)
        self.accept()

    def get_settings(self):
        return self.txt_api_key.text().strip(), self.txt_model.text().strip()


# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
class ImageThumbnail(QWidget):
    def __init__(self, image_path, parent=None, on_remove=None):
        super().__init__(parent)
        self.image_path = image_path
        self.on_remove = on_remove
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(150, 150)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Khung hiển thị ảnh thumbnail
        self.lbl_thumb = QLabel()
        pixmap = QPixmap(self.image_path)
        self.lbl_thumb.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.lbl_thumb.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Nút Xóa nhỏ ở góc trên bên phải
        btn_delete = QPushButton("✕")
        btn_delete.setFixedSize(22, 22)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border: none;
                border-radius: 11px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ff7875;
            }
        """)
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.on_remove:
            btn_delete.clicked.connect(lambda: self.on_remove(self))

        # Đặt đè nút xóa lên góc trên bên phải của ảnh
        layout.addWidget(self.lbl_thumb, 0, 0)
        layout.addWidget(btn_delete, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
    def enterEvent(self, event):
        # Lấy kích thước hiện tại của cửa sổ chính và tính 80% chiều cao, chiều rộng
        main_window = self.window()
        if main_window:
            max_w = int(main_window.width() * 0.8)
            max_h = int(main_window.height() * 0.8)
        else:
            max_w, max_h = 800, 600

        # Giới hạn khung hình bằng max-width và max-height trong CSS để giữ đúng tỷ lệ ảnh
        self.lbl_thumb.setToolTip(f'<img src="{self.image_path}" style="max-width: {max_w}px; max-height: {max_h}px;">')
        super().enterEvent(event)    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyApp", "JSON_Converter_AI")
        self.api_key = self.settings.value("api_key", "")
        self.model_name = self.settings.value("model_name", "gemini-2.5-flash")
        self.html_template_content = ""
        self.temp_image_paths = [] # Dùng List để lưu tối đa 5 đường dẫn ảnh

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        self.setWindowTitle("K._n? AI-Integrated JSON Parser using Gemini API for HTML Test Bank Manager")
        self.resize(1200, 750)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # ------------------------------------------
        # HEADER
        # ------------------------------------------
        top_bar = QHBoxLayout()
        
        self.txt_html_path = QLineEdit()
        self.txt_html_path.setReadOnly(True)
        self.txt_html_path.setPlaceholderText("Chưa chọn file HTML mẫu...")
        
        btn_open_html = QPushButton("📂 Chọn File HTML mẫu")
        btn_open_html.clicked.connect(self.open_html_file)
        
        btn_settings = QPushButton("⚙️ Cài đặt AI")
        btn_settings.clicked.connect(self.open_settings)
        
        top_bar.addWidget(QLabel("File HTML mẫu:"))
        top_bar.addWidget(self.txt_html_path)
        top_bar.addWidget(btn_open_html)
        top_bar.addWidget(btn_settings)
        
        main_layout.addLayout(top_bar)

        # ------------------------------------------
        # MAIN SPLITTER
        # ------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- CỘT TRÁI (2/3 chiều rộng màn hình) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 10, 0, 0)
        
        # 1. Mục Hình ảnh (Trên)
        group_image = QGroupBox("Hình ảnh câu hỏi (Tùy chọn)")
        img_layout = QHBoxLayout(group_image)
        
        # Khu vực xem trước danh sách ảnh tải lên
        self.image_preview_widget = QWidget()
        self.image_preview_layout = QHBoxLayout(self.image_preview_widget)
        self.image_preview_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.lbl_image_placeholder = QLabel("Dán ảnh (Ctrl+V) hoặc Tải ảnh lên\n(Hỗ trợ tối đa 5 ảnh)")
        self.lbl_image_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image_placeholder.setStyleSheet("border: 2px dashed #aaa; background-color: #f9f9f9; color: #333333;")
        self.lbl_image_placeholder.setMinimumSize(280, 120)
        self.image_preview_layout.addWidget(self.lbl_image_placeholder)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.image_preview_widget)
        scroll_area.setStyleSheet("border: none; background-color: #f9f9f9;")
        scroll_area.setMinimumHeight(150)
        
        btn_img_layout = QVBoxLayout()
        btn_upload_img = QPushButton("Tải ảnh lên\n🖼️")
        btn_upload_img.clicked.connect(self.upload_image)
        
        btn_clear_img = QPushButton("Xóa tất cả ảnh\n❌")
        btn_clear_img.clicked.connect(self.clear_images)
        
        btn_solve_img = QPushButton("Giải câu hỏi và chuyển đổi\nhình ảnh sang dạng Text\n➡️")
        btn_solve_img.setMinimumHeight(50)
        btn_solve_img.clicked.connect(self.solve_image_to_text)
        
        btn_img_layout.addWidget(btn_upload_img)
        btn_img_layout.addWidget(btn_clear_img)
        btn_img_layout.addStretch()
        btn_img_layout.addWidget(btn_solve_img)
        
        img_layout.addWidget(scroll_area, stretch=1)
        img_layout.addLayout(btn_img_layout)
        
        # 2. Mục Text (Dưới)
        group_text = QGroupBox("Trả lời từ AI / Câu hỏi dạng Text cần chuyển sang JSON")
        text_layout = QHBoxLayout(group_text)
        
        self.txt_question_text = QTextEdit()
        self.txt_question_text.setPlaceholderText("Nội dung text sinh ra từ ảnh hoặc nhập thủ công...")
        
        btn_convert_json = QPushButton("Chuyển đổi\n➡️")
        btn_convert_json.setMinimumHeight(60)
        btn_convert_json.clicked.connect(self.convert_text_to_json)
        
        text_layout.addWidget(self.txt_question_text)
        text_layout.addWidget(btn_convert_json)
        
        left_layout.addWidget(group_image, 1)
        left_layout.addWidget(group_text, 1)
        
        # --- CỘT PHẢI (1/3 chiều rộng màn hình) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 10, 0, 0)
        
        group_json = QGroupBox("Dữ liệu JSON được chuyển đổi")
        json_layout = QVBoxLayout(group_json)
        
        self.txt_json_result = QTextEdit()
        self.txt_json_result.setPlaceholderText("Kết quả JSON sẽ hiển thị ở đây...")
        
        btn_copy_json = QPushButton("📋 Sao chép JSON")
        btn_copy_json.clicked.connect(lambda: QApplication.clipboard().setText(self.txt_json_result.toPlainText()))
        
        json_layout.addWidget(self.txt_json_result)
        json_layout.addWidget(btn_copy_json)
        
        right_layout.addWidget(group_json)
        
        # Thêm 2 cột vào Splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 400]) # Khởi tạo tỷ lệ 2/3 và 1/3
        
        main_layout.addWidget(splitter)

    def setup_shortcuts(self):
        # Thiết lập phím tắt dán ảnh
        shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        shortcut.activated.connect(self.paste_image)

    # ==========================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN GIAO DIỆN
    # ==========================================
    def open_settings(self):
        dlg = SettingsDialog(self, self.api_key, self.model_name)
        if dlg.exec():
            self.api_key, self.model_name = dlg.get_settings()
            # Lưu cấu hình vào máy để lần sau tự động tải
            self.settings.setValue("api_key", self.api_key)
            self.settings.setValue("model_name", self.model_name)

    def open_html_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file HTML mẫu", "", "HTML Files (*.html *.htm)")
        if file_path:
            self.txt_html_path.setText(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.html_template_content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc file: {str(e)}")

    def paste_image(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasImage():
            image = clipboard.image()
            self._display_and_save_image(image)

    def upload_image(self):
        # Cho phép chọn nhiều file (QFileDialog.getOpenFileNames thay vì FileName)
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Chọn hình ảnh", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        for file_path in file_paths:
            if len(self.temp_image_paths) >= 5:
                QMessageBox.warning(self, "Giới hạn", "Chỉ được tải lên tối đa 5 ảnh!")
                break
            image = QImage(file_path)
            self._display_and_save_image(image)

    def _display_and_save_image(self, qimage):
        if len(self.temp_image_paths) >= 5:
            QMessageBox.warning(self, "Giới hạn", "Bạn đã đạt tối đa 5 ảnh!")
            return

        # Lưu ra file tạm để API có thể đọc
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"temp_question_img_{len(self.temp_image_paths)}.png")
        qimage.save(temp_path, "PNG")
        self.temp_image_paths.append(temp_path)
        
        # Cập nhật giao diện: Ẩn chữ placeholder và thêm Widget Thumbnail
        self.lbl_image_placeholder.hide()
        thumb_widget = ImageThumbnail(temp_path, on_remove=self.remove_single_image)
        self.image_preview_layout.addWidget(thumb_widget)
    
    def remove_single_image(self, thumb_widget):
        # Loại bỏ file tạm tương ứng khỏi danh sách
        if thumb_widget.image_path in self.temp_image_paths:
            self.temp_image_paths.remove(thumb_widget.image_path)
        
        # Xóa Widget khỏi giao diện
        thumb_widget.setParent(None)
        thumb_widget.deleteLater()

        # Hiện lại khung chữ hướng dẫn nếu đã xóa hết ảnh
        if not self.temp_image_paths:
            self.lbl_image_placeholder.show()
    
    def clear_images(self):
        # Xóa toàn bộ ảnh
        self.temp_image_paths.clear()
        for i in reversed(range(self.image_preview_layout.count())):
            widget = self.image_preview_layout.itemAt(i).widget()
            if widget is not None and widget != self.lbl_image_placeholder:
                widget.setParent(None)
        self.lbl_image_placeholder.show()

    # ==========================================
    # KẾT NỐI API AI
    # ==========================================
    def solve_image_to_text(self):
        if not self.temp_image_paths:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng tải ảnh lên hoặc dán (Ctrl+V) hình ảnh câu hỏi.")
            return
            
        self.txt_question_text.setEnabled(False)  # Khóa khung nhập/hiển thị text
        self.txt_question_text.setText("Đang xử lý hình ảnh, vui lòng đợi...")
        prompt = "Giải và chuyển đổi hình ảnh sang dạng text. Hãy giữ nguyên cấu trúc câu hỏi và các đáp án."
        
        # Đưa toàn bộ list ảnh vào biến image_paths
        self.worker1 = AIWorker(self.api_key, self.model_name, prompt, image_paths=self.temp_image_paths)
        self.worker1.finished.connect(self.on_image_solved)
        self.worker1.error.connect(self.on_ai_error)
        self.worker1.start()

    def on_image_solved(self, text):
        self.txt_question_text.setText(text)
        self.txt_question_text.setEnabled(True)  # Mở khóa sau khi nhận kết quả

    def convert_text_to_json(self):
        question_text = self.txt_question_text.toPlainText().strip()
        if not question_text:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng nhập hoặc tạo đoạn text câu hỏi cần chuyển đổi.")
            return
            
        if not self.html_template_content:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng chọn File HTML mẫu trước khi chuyển đổi sang JSON.")
            return
        
        self.txt_json_result.setEnabled(False)  # Khóa khung hiển thị JSON
        self.txt_json_result.setText("Đang chuyển đổi sang JSON, vui lòng đợi...")
        prompt = f"""Chuyển đổi đoạn trả lời câu hỏi sau sang dữ liệu JSON phù hợp với dạng câu hỏi của HTML ngân hàng câu hỏi này. 
Chỉ trả về MỘT chuỗi JSON hợp lệ, không chứa cú pháp markdown (như ```json) hay các đoạn text giải thích thừa.

Nội dung câu hỏi:
{question_text}"""
        
        self.worker2 = AIWorker(self.api_key, self.model_name, prompt, html_content=self.html_template_content)
        self.worker2.finished.connect(self.on_json_converted)
        self.worker2.error.connect(self.on_ai_error)
        self.worker2.start()

    def on_json_converted(self, json_text):
        # Làm sạch chuỗi trả về trong trường hợp AI vẫn bọc markdown
        clean_json = json_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        try:
            # Kiểm tra xem JSON có hợp lệ không
            parsed_json = json.loads(clean_json.strip())
            formatted_json = json.dumps(parsed_json, ensure_ascii=False, indent=4)
            self.txt_json_result.setText(formatted_json)
        except json.JSONDecodeError:
            self.txt_json_result.setText(f"Dữ liệu trả về không phải là JSON hợp lệ. Chuỗi thô:\n\n{clean_json}")
        self.txt_json_result.setEnabled(True)  # Mở khóa sau khi nhận kết quả                

    def on_ai_error(self, err_msg):
        # Mở khóa lại các ô text nếu xảy ra lỗi
        self.txt_question_text.setEnabled(True)
        self.txt_json_result.setEnabled(True)
        
        # Tự động chèn xuống dòng ở các dấu phân cách thông dụng (như dấu hai chấm, gạch ngang, ngoặc nhọn)
        formatted_msg = (
            str(err_msg)
            .replace(": ", ":\n")
            .replace(" - ", "\n• ")
            .replace("{", "{\n")
            .replace("}", "\n}")
        )
        QMessageBox.critical(self, "Lỗi API", f"⚠️ Đã xảy ra lỗi trong quá trình xử lý:\n\n{formatted_msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("image.ico"))
    font = app.font()
    font.setPointSize(12)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())