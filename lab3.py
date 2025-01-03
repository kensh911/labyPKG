import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QComboBox, QSlider, QSpinBox, QGridLayout, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import imutils
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4))
        self.figure.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.ax.set_facecolor('#2b2b2b')
        self.figure.patch.set_facecolor('#2b2b2b')
        self.ax.grid(True, color='gray', alpha=0.3)
        self.ax.tick_params(colors='white')

    def update_histogram(self, image):
        self.ax.clear()
        if len(image.shape) == 3:
            colors = ('b', 'g', 'r')
            labels = ('Blue', 'Green', 'Red')
            for i, (color, label) in enumerate(zip(colors, labels)):
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                self.ax.plot(hist, color=color, label=label, linewidth=2)
            self.ax.legend()
        else:
            hist = cv2.calcHist([image], [0], None, [256], [0, 256])
            self.ax.plot(hist, color='white', linewidth=2)

        self.ax.set_xlim([0, 256])
        self.ax.set_ylim(bottom=0)  # Начинаем с нуля
        self.ax.grid(True, color='gray', alpha=0.3)
        self.ax.tick_params(colors='white')
        self.canvas.draw()


class ImageProcessor:
    @staticmethod
    def linear_contrast(image, alpha, beta):
        """Линейное контрастирование"""
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    @staticmethod
    def apply_brightness_contrast(image, brightness=0, contrast=0):
        """Поэлементная операция изменения контраста и яркости"""
        new_image = np.clip(image * (contrast / 127 + 1) - contrast + brightness, 0, 255)
        return new_image.astype(np.uint8)


class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing Application")
        self.setStyleSheet(""" 
            QMainWindow, QWidget {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QComboBox {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
                min-width: 200px;
            }
            QSpinBox, QSlider {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
            }
            QGroupBox {
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        self.original_image = None
        self.processed_image = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)

        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, stretch=3)

        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=1)

        self.update_controls()
        self.resize(1600, 900)

    def create_left_panel(self):
        group_box = QGroupBox("Controls")
        layout = QVBoxLayout()

        load_btn = QPushButton("Load Image")
        load_btn.clicked.connect(self.load_image)
        layout.addWidget(load_btn)

        layout.addWidget(QLabel("Processing Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Linear Contrast",
            "Apply Brightness and Contrast"
        ])
        self.method_combo.currentIndexChanged.connect(self.update_controls)
        layout.addWidget(self.method_combo)

        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout(self.params_widget)
        layout.addWidget(self.params_widget)

        process_btn = QPushButton("Process Image")
        process_btn.clicked.connect(self.process_image)
        layout.addWidget(process_btn)

        layout.addStretch()
        group_box.setLayout(layout)
        return group_box

    def create_center_panel(self):
        group_box = QGroupBox("Images")
        layout = QGridLayout()

        original_container = QWidget()
        original_layout = QVBoxLayout(original_container)
        original_layout.addWidget(QLabel("Original Image:"))
        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        original_layout.addWidget(self.original_label)
        layout.addWidget(original_container, 0, 0)

        processed_container = QWidget()
        processed_layout = QVBoxLayout(processed_container)
        processed_layout.addWidget(QLabel("Processed Image:"))
        self.processed_label = QLabel()
        self.processed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        processed_layout.addWidget(self.processed_label)
        layout.addWidget(processed_container, 0, 1)

        group_box.setLayout(layout)
        return group_box

    def create_right_panel(self):
        group_box = QGroupBox("Histograms")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Original Histogram:"))
        self.original_histogram = HistogramWidget()
        layout.addWidget(self.original_histogram)

        layout.addWidget(QLabel("Processed Histogram:"))
        self.processed_histogram = HistogramWidget()
        layout.addWidget(self.processed_histogram)

        group_box.setLayout(layout)
        return group_box

    def update_controls(self):
        for i in reversed(range(self.params_layout.count())):
            self.params_layout.itemAt(i).widget().setParent(None)

        method = self.method_combo.currentText()

        if method == "Linear Contrast":
            alpha_container = QWidget()
            alpha_layout = QVBoxLayout(alpha_container)
            self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
            self.alpha_slider.setRange(10, 30)
            self.alpha_slider.setValue(10)
            alpha_layout.addWidget(QLabel("Contrast (alpha):"))
            alpha_layout.addWidget(self.alpha_slider)
            self.params_layout.addWidget(alpha_container)

            # Beta slider
            beta_container = QWidget()
            beta_layout = QVBoxLayout(beta_container)
            self.beta_slider = QSlider(Qt.Orientation.Horizontal)
            self.beta_slider.setRange(-50, 50)
            self.beta_slider.setValue(0)
            beta_layout.addWidget(QLabel("Brightness (beta):"))
            beta_layout.addWidget(self.beta_slider)
            self.params_layout.addWidget(beta_container)

        elif method == "Apply Brightness and Contrast":
            brightness_container = QWidget()
            brightness_layout = QVBoxLayout(brightness_container)
            self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
            self.brightness_slider.setRange(-100, 100)
            self.brightness_slider.setValue(0)
            brightness_layout.addWidget(QLabel("Brightness:"))
            brightness_layout.addWidget(self.brightness_slider)
            self.params_layout.addWidget(brightness_container)

            contrast_container = QWidget()
            contrast_layout = QVBoxLayout(contrast_container)
            self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
            self.contrast_slider.setRange(-100, 100)
            self.contrast_slider.setValue(0)
            contrast_layout.addWidget(QLabel("Contrast:"))
            contrast_layout.addWidget(self.contrast_slider)
            self.params_layout.addWidget(contrast_container)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if file_name:
            self.original_image = cv2.imread(file_name)
            self.display_image(self.original_image, self.original_label)
            self.original_histogram.update_histogram(self.original_image)
            self.processed_image = None
            self.processed_label.clear()
            self.processed_histogram.ax.clear()
            self.processed_histogram.canvas.draw()

    def process_image(self):
        if self.original_image is None:
            return

        method = self.method_combo.currentText()

        if method == "Linear Contrast":
            alpha = self.alpha_slider.value() / 10.0
            beta = self.beta_slider.value()
            self.processed_image = ImageProcessor.linear_contrast(self.original_image, alpha, beta)

        elif method == "Apply Brightness and Contrast":
            brightness = self.brightness_slider.value()
            contrast = self.contrast_slider.value()
            self.processed_image = ImageProcessor.apply_brightness_contrast(self.original_image, brightness, contrast)

        if self.processed_image is not None:
            self.display_image(self.processed_image, self.processed_label)
            self.processed_histogram.update_histogram(self.processed_image)

    def display_image(self, image, label):
        image = imutils.resize(image, width=500)
        height, width = image.shape[:2]

        if len(image.shape) == 3:
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line,
                           QImage.Format.Format_RGB888).rgbSwapped()
        else:
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line,
                           QImage.Format.Format_Grayscale8)

        pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.original_image is not None:
            self.display_image(self.original_image, self.original_label)
        if self.processed_image is not None:
            self.display_image(self.processed_image, self.processed_label)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    plt.style.use('dark_background')

    window = ImageProcessingApp()
    window.show()
    sys.exit(app.exec())
