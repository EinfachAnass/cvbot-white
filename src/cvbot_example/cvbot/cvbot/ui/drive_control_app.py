import sys
import asyncio
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout)
from PySide6.QtCore import QThread, Signal, QObject
from cvbot.controller.easy_drive_controller import EasyDriveController
from PySide6.QtAsyncio import QAsyncioEventLoop

class ControlWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, drive_controller: EasyDriveController):
        super().__init__()
        self.drive_controller = drive_controller
        self.method = None
        self.args = None

    async def run_controller_method(self, method_name, *args):
        self.method = method_name
        self.args = args
        try:
            controller_method = getattr(self.drive_controller, self.method)
            if asyncio.iscoroutinefunction(controller_method):
                await controller_method(*self.args)
            else:
                controller_method(*self.args)
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Fehler bei der Ausführung von {self.method}: {e}")

class DriveControlApp(QMainWindow):
    def __init__(self, drive_controller: EasyDriveController):
        super().__init__()
        self.drive_controller: EasyDriveController = drive_controller
        self.control_worker = ControlWorker(self.drive_controller)
        self.control_worker_thread = QThread()
        self.control_worker.moveToThread(self.control_worker_thread)
        self.control_worker_thread.start()
        self.initialized = False
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.initialize_button = QPushButton("Initialize")
        self.initialize_button.clicked.connect(self.initialize_robot)
        self.layout.addWidget(self.initialize_button)

        # Geschwindigkeits-Eingabefelder (werden nach der Initialisierung hinzugefügt)
        self.forward_speed_input = QLineEdit("50")
        self.side_speed_input = QLineEdit("50")
        self.rotate_speed_input = QLineEdit("30")

        # Buttons für die Steuerung (werden nach der Initialisierung hinzugefügt)
        self.forward_button = QPushButton("Forward")
        self.backward_button = QPushButton("Backward")
        self.left_button = QPushButton("Left")
        self.right_button = QPushButton("Right")
        self.forward_left_button = QPushButton("Forward Left")
        self.forward_right_button = QPushButton("Forward Right")
        self.backward_left_button = QPushButton("Backward Left")
        self.backward_right_button = QPushButton("Backward Right")
        self.rotate_left_button = QPushButton("Rotate Left")
        self.rotate_right_button = QPushButton("Rotate Right")
        self.stop_button = QPushButton("STOP")

        self.setWindowTitle("Robot Control (PySide6 + asyncio in Thread)")
        self.setGeometry(100, 100, 400, 200)

    async def initialize_robot(self):
        if not self.initialized:
            print("Initializing robot...")
            # Hier könntest du deine tatsächliche Initialisierungslogik einfügen

            # Layout für die Geschwindigkeits-Eingabe
            speed_layout = QHBoxLayout()
            speed_layout.addWidget(QLabel("Forward/Backward:"))
            speed_layout.addWidget(self.forward_speed_input)
            speed_layout.addWidget(QLabel("Sideways:"))
            speed_layout.addWidget(self.side_speed_input)
            speed_layout.addWidget(QLabel("Rotate (rad/s):"))
            speed_layout.addWidget(self.rotate_speed_input)
            self.layout.addLayout(speed_layout)

            # Layout für die Buttons
            buttons_layout1 = QHBoxLayout()
            buttons_layout1.addWidget(self.left_button)
            buttons_layout1.addWidget(self.forward_button)
            buttons_layout1.addWidget(self.right_button)
            self.layout.addLayout(buttons_layout1)

            buttons_layout2 = QHBoxLayout()
            buttons_layout2.addWidget(self.backward_left_button)
            buttons_layout2.addWidget(self.backward_button)
            buttons_layout2.addWidget(self.backward_right_button)
            self.layout.addLayout(buttons_layout2)

            buttons_layout3 = QHBoxLayout()
            buttons_layout3.addWidget(self.forward_left_button)
            buttons_layout3.addWidget(self.stop_button)
            buttons_layout3.addWidget(self.forward_right_button)
            self.layout.addLayout(buttons_layout3)

            # Verbinde Buttons mit Aktionen
            self.forward_button.clicked.connect(self.drive_forward)
            self.backward_button.clicked.connect(self.drive_backward)
            self.left_button.clicked.connect(self.drive_left)
            self.right_button.clicked.connect(self.drive_right)
            self.forward_left_button.clicked.connect(self.drive_forward_left)
            self.forward_right_button.clicked.connect(self.drive_forward_right)
            self.backward_left_button.clicked.connect(self.drive_backward_left)
            self.backward_right_button.clicked.connect(self.drive_backward_right)
            self.rotate_left_button.clicked.connect(self.rotate_left)
            self.rotate_right_button.clicked.connect(self.rotate_right)
            self.stop_button.clicked.connect(self.stop_robot)

            # Entferne den Initialize-Button
            self.initialize_button.deleteLater()
            self.initialize_button = None
            self.initialized = True

    def get_speeds(self):
        try:
            forward_speed = int(self.forward_speed_input.text())
            side_speed = int(self.side_speed_input.text())
            rotate_speed = float(self.rotate_speed_input.text())
            return forward_speed, side_speed, rotate_speed
        except ValueError:
            return 0, 0, 0

    def call_controller_method_in_thread(self, method_name, *args):
        asyncio.run(self.control_worker.run_controller_method(method_name, *args))

    def drive_forward(self):
        if self.initialized:
            forward_speed, _, _ = self.get_speeds()
            self.call_controller_method_in_thread("straight", forward_speed)

    def drive_backward(self):
        if self.initialized:
            forward_speed, _, _ = self.get_speeds()
            self.call_controller_method_in_thread("straight", -forward_speed)

    def drive_left(self):
        if self.initialized:
            _, side_speed, _ = self.get_speeds()
            self.call_controller_method_in_thread("side", -side_speed)

    def drive_right(self):
        if self.initialized:
            _, side_speed, _ = self.get_speeds()
            self.call_controller_method_in_thread("side", side_speed)

    def drive_forward_left(self):
        if self.initialized:
            forward_speed, side_speed, _ = self.get_speeds()
            self.call_controller_method_in_thread("diagonal", forward_speed, -side_speed)

    def drive_forward_right(self):
        if self.initialized:
            forward_speed, side_speed, _ = self.get_speeds()
            self.call_controller_method_in_thread("diagonal", forward_speed, side_speed)

    def drive_backward_left(self):
        if self.initialized:
            forward_speed, side_speed, _ = self.get_speeds()
            self.call_controller_method_in_thread("diagonal", -forward_speed, -side_speed)

    def drive_backward_right(self):
        if self.initialized:
            forward_speed, side_speed, _ = self.get_speeds()
            self.call_controller_method_in_thread("diagonal", -forward_speed, side_speed)

    def rotate_left(self):
        if self.initialized:
            _, _, rotate_speed = self.get_speeds()
            self.call_controller_method_in_thread("rotate", rotate_speed)

    def rotate_right(self):
        if self.initialized:
            _, _, rotate_speed = self.get_speeds()
            self.call_controller_method_in_thread("rotate", -rotate_speed)

    def stop_robot(self):
        if self.initialized:
            self.call_controller_method_in_thread("stop")

    def closeEvent(self, event):
        self.control_worker_thread.quit()
        self.control_worker_thread.wait()
        event.accept()
