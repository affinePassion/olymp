import sys
import math
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                              QVBoxLayout, QHBoxLayout, QSlider, 
                              QLabel, QPushButton)
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient

class AdvancedRadarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.scan_speed = 3
        self.max_distance = 500
        self.targets = []
        self.scan_history = []
        self.max_history = 50
        
        # Генерация случайных целей
        self.generate_targets(8)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_radar)
        self.timer.start(40)
        
    def generate_targets(self, count):
        self.targets = []
        for _ in range(count):
            distance = random.randint(50, self.max_distance - 50)
            angle = random.randint(0, 359)
            size = random.randint(1, 3)
            speed = random.uniform(0.5, 2.0)
            direction = random.choice([-1, 1])
            self.targets.append({
                'distance': distance,
                'angle': angle,
                'size': size,
                'speed': speed,
                'direction': direction
            })
    
    def update_radar(self):
        self.angle = (self.angle + self.scan_speed) % 360
        
        # Обновление позиций целей
        for target in self.targets:
            target['angle'] = (target['angle'] + target['speed'] * target['direction']) % 360
        
        # Добавление в историю сканирования
        self.scan_history.append(self.angle)
        if len(self.scan_history) > self.max_history:
            self.scan_history.pop(0)
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(center_x, center_y) - 30
        
        self.draw_radar_display(painter, center_x, center_y, radius)
        self.draw_scan_effects(painter, center_x, center_y, radius)
        self.draw_targets(painter, center_x, center_y, radius)
        self.draw_ui_elements(painter, center_x, center_y, radius)
        
    def draw_radar_display(self, painter, center_x, center_y, radius):
        # Темный фон
        painter.fillRect(self.rect(), QColor(10, 20, 10))
        
        # Основной круг радара
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, QColor(0, 80, 0, 100))
        gradient.setColorAt(1, QColor(0, 40, 0, 50))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 180, 0), 2))
        painter.drawEllipse(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2)
        
        # Сетка
        pen = QPen(QColor(0, 120, 0), 1, Qt.DotLine)
        painter.setPen(pen)
        
        for i in range(1, 5):
            circle_radius = radius * i / 5
            painter.drawEllipse(center_x - circle_radius, center_y - circle_radius,
                              circle_radius * 2, circle_radius * 2)
            
        for angle in range(0, 360, 45):
            rad_angle = math.radians(angle - 90)
            end_x = center_x + radius * math.cos(rad_angle)
            end_y = center_y + radius * math.sin(rad_angle)
            painter.drawLine(center_x, center_y, end_x, end_y)
    
    def draw_scan_effects(self, painter, center_x, center_y, radius):
        # Сканирующий сектор
        scan_gradient = QRadialGradient(center_x, center_y, radius)
        scan_gradient.setColorAt(0, QColor(0, 255, 0, 80))
        scan_gradient.setColorAt(1, QColor(0, 255, 0, 0))
        
        painter.setBrush(QBrush(scan_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawPie(center_x - radius, center_y - radius, 
                       radius * 2, radius * 2, 
                       (self.angle - 30) * 16, 60 * 16)
        
        # Линия сканирования
        end_x = center_x + radius * math.cos(math.radians(self.angle - 90))
        end_y = center_y + radius * math.sin(math.radians(self.angle - 90))
        
        pen = QPen(QColor(0, 255, 0), 2)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLine(center_x, center_y, end_x, end_y)
        
        # Эффект свечения на конце линии
        painter.setBrush(QBrush(QColor(0, 255, 0)))
        painter.drawEllipse(int(end_x) - 3, int(end_y) - 3, 6, 6)
    
    def draw_targets(self, painter, center_x, center_y, radius):
        for target in self.targets:
            distance = target['distance']
            angle = target['angle']
            size = target['size']
            
            scaled_distance = (distance / self.max_distance) * radius
            target_x = center_x + scaled_distance * math.cos(math.radians(angle - 90))
            target_y = center_y + scaled_distance * math.sin(math.radians(angle - 90))
            
            target_size = 4 + size * 2
            
            # Цвет в зависимости от размера и расстояния
            intensity = 255 - int((distance / self.max_distance) * 100)
            if size == 1:
                color = QColor(255, 255, intensity)
            elif size == 2:
                color = QColor(255, intensity, 0)
            else:
                color = QColor(255, intensity // 2, intensity // 2)
            
            # Внешний круг
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(color, 2))
            painter.drawEllipse(QPointF(target_x, target_y), target_size, target_size)
            
            # Внутренняя заливка
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(target_x, target_y), target_size - 2, target_size - 2)
    
    def draw_ui_elements(self, painter, center_x, center_y, radius):
        # Отображение угла
        painter.setPen(QPen(QColor(0, 255, 0)))
        painter.drawText(10, 20, f"Угол: {self.angle}°")
        painter.drawText(10, 40, f"Целей: {len(self.targets)}")
        
        # Крестик в центре
        cross_size = 8
        painter.drawLine(center_x - cross_size, center_y, center_x + cross_size, center_y)
        painter.drawLine(center_x, center_y - cross_size, center_x, center_y + cross_size)

class RadarControlPanel(QWidget):
    def __init__(self, radar_widget, parent=None):
        super().__init__(parent)
        self.radar_widget = radar_widget
        
        layout = QVBoxLayout()
        
        # Слайдер скорости сканирования
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Скорость:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(3)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        layout.addLayout(speed_layout)
        
        # Кнопка новых целей
        self.new_targets_btn = QPushButton("Новые цели")
        self.new_targets_btn.clicked.connect(self.generate_new_targets)
        layout.addWidget(self.new_targets_btn)
        
        self.setLayout(layout)
    
    def update_speed(self, value):
        self.radar_widget.scan_speed = value
    
    def generate_new_targets(self):
        self.radar_widget.generate_targets(8)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Продвинутый радар")
        self.setGeometry(100, 100, 700, 700)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.radar_widget = AdvancedRadarWidget()
        self.control_panel = RadarControlPanel(self.radar_widget)
        
        main_layout.addWidget(self.radar_widget, 4)
        main_layout.addWidget(self.control_panel, 1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())