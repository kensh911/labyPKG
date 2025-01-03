import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QProgressBar, 
    QSplitter, QHeaderView, QComboBox, QStyle
)
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PIL import Image
import piexif
import hashlib
import time

class ImageAnalyzerThread(QThread):
    update_progress = pyqtSignal(int)
    update_table = pyqtSignal(list)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        total_files = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            self.analyze_image(file_path)
            self.update_progress.emit(int((i + 1) / total_files * 100))

    def analyze_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                filename = os.path.basename(file_path)
                size = f"{img.width}x{img.height}"
                format = img.format
                mode = img.mode

                dpi = img.info.get('dpi', (72, 72))
                resolution = f"{dpi[0]}x{dpi[1]} dpi"

                color_depth = self.get_color_depth(mode)
                compression = img.info.get('compression', 'No info')
                file_size = os.path.getsize(file_path)
                file_size_mb = round(file_size / (1024 * 1024), 2)
                file_hash = self.get_file_hash(file_path)
                
                creation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file_path)))
                modification_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
                access_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getatime(file_path)))
                
                additional_info = self.get_additional_info(img, format)

                self.update_table.emit([filename, size, resolution, color_depth, str(compression), format, 
                                        additional_info, file_size_mb, file_hash, 
                                        creation_time, modification_time, access_time, file_path])
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    @staticmethod
    def get_color_depth(mode):
        mode_depths = {'1': "1 bit (B&W)", 'L': "8 bit (Grayscale)", 'RGB': "24 bit", 'RGBA': "32 bit"}
        return mode_depths.get(mode, "Unknown")

    @staticmethod
    def get_file_hash(file_path):
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    @staticmethod
    def get_additional_info(img, format):
        if format == 'JPEG':
            try:
                exif_dict = piexif.load(img.info["exif"])
                return f"EXIF data: {len(exif_dict['0th'])} fields"
            except:
                return "No EXIF data"
        elif format == 'GIF':
            return f"Palette colors: {len(img.getcolors())}"
        elif format == 'PNG':
            return f"Colors: {len(img.getcolors()) if img.getcolors() else 'More than 256'}"
        return ""

class ImageAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Analyzer")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon.fromTheme("image-x-generic"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_themes()
        self.create_ui()
        self.set_theme("Light")
        self.file_paths = {}

    def create_ui(self):
        top_panel = QHBoxLayout()

        self.select_folder_button = QPushButton("Выбрать папку")
        self.select_folder_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.select_folder_button.clicked.connect(self.select_folder)

        self.select_file_button = QPushButton("Выбрать файлы")
        self.select_file_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.select_file_button.clicked.connect(self.select_files)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(self.themes.keys())
        self.theme_selector.currentTextChanged.connect(self.set_theme)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_panel.addWidget(self.select_folder_button)
        top_panel.addWidget(self.select_file_button)
        top_panel.addStretch()
        top_panel.addWidget(QLabel("Тема:"))
        top_panel.addWidget(self.theme_selector)
        top_panel.addWidget(self.progress_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Filename", "Dimensions", "Resolution", "Color Depth", "Compression", 
            "Format", "Additional Info", "File Size (MB)", "MD5 Hash", 
            "Creation Time", "Modification Time", "Last Access Time"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.show_image)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #f0f0f0;")

        preview_panel = QVBoxLayout()
        self.image_label = QLabel("Предпросмотр изображения")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_label.setWordWrap(True)
        preview_panel.addWidget(self.image_label)
        preview_panel.addWidget(self.info_label)

        preview_widget = QWidget()
        preview_widget.setLayout(preview_panel)

        splitter.addWidget(self.table)
        splitter.addWidget(preview_widget)
        splitter.setSizes([800, 600])

        self.layout.addLayout(top_panel)
        self.layout.addWidget(splitter)

    def create_themes(self):
        self.themes = {
            "Hacker": {
                "bg": "#1e1e1e",
                "fg": "#00ff00",
                "accent": "#006400",
                "font": "Courier New",
                "font_size": "12px",
                "border": "1px solid #00ff00",
                "border_radius": "4px",
            },
            "Dark": {
                "bg": "#2e2e2e",
                "fg": "#ffffff",
                "accent": "#007acc",
                "font": "Segoe UI",
                "font_size": "14px",
                "border": "1px solid #ffffff",
                "border_radius": "4px",
            },
            "Light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "accent": "#007acc",
                "font": "Segoe UI",
                "font_size": "14px",
                "border": "1px solid #cccccc",
                "border_radius": "4px",
            }
        }

    def set_theme(self, theme_name):
        theme = self.themes[theme_name]
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['bg']};
                color: {theme['fg']};
                font-family: {theme['font']};
                font-size: {theme['font_size']};
            }}
            QTableWidget {{
                gridline-color: {theme['fg']};
                border: {theme['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {theme['accent']};
                color: #ffffff;
            }}
            QHeaderView::section {{
                background-color: {theme['accent']};
                color: #ffffff;
                padding: 4px;
                border: {theme['border']};
            }}
            QPushButton {{
                background-color: {theme['bg']};
                color: {theme['fg']};
                border: {theme['border']};
                padding: 8px 12px;
                border-radius: {theme['border_radius']};
            }}
            QPushButton:hover {{
                background-color: {theme['accent']};
                color: #ffffff;
            }}
            QComboBox {{
                background-color: {theme['bg']};
                color: {theme['fg']};
                border: {theme['border']};
                padding: 4px;
                border-radius: {theme['border_radius']};
            }}
            QComboBox::drop-down {{
                border-left: 1px solid {theme['fg']};
            }}
            QProgressBar {{
                border: 1px solid {theme['fg']};
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {theme['accent']};
                width: 20px;
            }}
        """)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выбрать папку")
        if folder:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.table.setRowCount(0)
            self.file_paths.clear()
            supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.pcx')
            file_list = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(supported_extensions)]
            self.thread = ImageAnalyzerThread(file_list)
            self.thread.update_progress.connect(self.update_progress)
            self.thread.update_table.connect(self.update_table)
            self.thread.finished.connect(lambda: self.progress_bar.setVisible(False))
            self.thread.start()

    def select_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "Выбрать файлы", 
            "", 
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.pcx)"
        )
        if file_paths:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.table.setRowCount(0)
            self.thread = ImageAnalyzerThread(file_paths)
            self.thread.update_progress.connect(self.update_progress)
            self.thread.update_table.connect(self.update_table)
            self.thread.finished.connect(lambda: self.progress_bar.setVisible(False))
            self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_table(self, data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for i, value in enumerate(data[:-1]):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, i, item)
        self.file_paths[row] = data[-1]

    def show_image(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            file_path = self.file_paths.get(row, "")
            if file_path:
                try:
                    pixmap = QPixmap(file_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            self.image_label.size(), 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                    else:
                        self.image_label.setText("Не удалось загрузить изображение")

                    info = "Отчет по анализу файла:\n\n"
                    headers = [
                        "Filename", "Dimensions", "Resolution", "Color Depth", "Compression", 
                        "Format", "Additional Info", "File Size (MB)", "MD5 Hash", 
                        "Creation Time", "Modification Time", "Last Access Time"
                    ]
                    for i, header in enumerate(headers):
                        value = self.table.item(row, i).text()
                        info += f"{header}: {value}\n"
                    self.info_label.setText(info)
                except Exception as e:
                    print(f"Error displaying image: {e}")
                    self.image_label.setText("Ошибка при отображении изображения")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_preview()

    def update_image_preview(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            file_path = self.file_paths.get(row, "")
            if file_path:
                try:
                    pixmap = QPixmap(file_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            self.image_label.size(), 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                except Exception as e:
                    print(f"Error resizing image: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ImageAnalyzer()
    window.show()
    sys.exit(app.exec())
