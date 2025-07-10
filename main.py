# ---- Regular Imports ---- #
import sys, os, json, math

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


# ---- PyQt5 Imports ---- #
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QTextEdit, QSlider, QLabel, QFileDialog, QWidget, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QRegularExpressionValidator, QPixmap, QMovie, QCloseEvent, QIcon
from PyQt5.QtCore import Qt, QRegularExpression, QSize, QTimer

# ---- Globals ---- #
num = 1
draggable = True
data = {}
settings_path = "settings.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.operation = "/"
        self.setFocusPolicy(Qt.StrongFocus)

        self.setGeometry(700, 300, 1080, 700)
        self.setStyleSheet("background-color: #242424")

        self.setFixedSize(self.width(), self.height())

        self.setWindowTitle("IMORA")
        self.setWindowIcon(QIcon(resource_path("assets/Logo_Window.png")))

        # ---- Taskbar Setup ---- #
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("assets/Logo_Bar.png")))

        tray_menu = QMenu(self)

        tray_menu.setStyleSheet("""
        QMenu {font-size: 16px; background: #2B2B2B; font-family: "Segoe UI"; color: white; border: 1px solid white;}
        QMenu::item {background: transparent; padding: 6px 20px;}
        QMenu::item:selected {background: #444444; color: #FFFFFF;}
        """)

        self.tray_icon.setToolTip("Imora")
        show_action = QAction("Open", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(exit_app)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

        #* Title *#
        self.title = self.create_label("", 55, 20, 960, 110)
        self.title.setScaledContents(True)
        pixmap = QPixmap(resource_path("assets/Title.png"))
        self.title.setPixmap(pixmap)

        self.title_gif = self.create_label("", 471, -175, 500, 500)
        logo = QMovie(resource_path("assets/Logo.gif"))
        logo.setScaledSize(QSize(115, 115))
        self.title_gif.setMovie(logo)
        logo.start()

        #* Open Button *#
        self.open_button = self.create_button("Open", 50, 210, 130, 60)
        self.open_button.clicked.connect(self.open_button_click)

        #* Load Button *#
        self.load_button = self.create_button("Load", 50, 285, 130, 60)
        self.load_button.clicked.connect(self.operation_confirm)
        self.load_button.clicked.connect(self.load_button_click)
        
        #* Save Button *#
        self.save_button = self.create_button("Save", 50, 360, 130, 60)
        self.save_button.clicked.connect(self.save_pos_and_exit)
        
        #* Clear Button *#
        self.clear_button = self.create_button("Clear", 50, 625, 100, 50)
        self.clear_button.clicked.connect(self.clear_console)

        #* Settings Button *#
        self.settings_button = self.create_button("⚙", 960, 625, 50, 50)
        self.settings_button.clicked.connect(self.setting_click)

        #* Console Dsiplay *#
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setGeometry(200, 150, 300, 450)
        self.console.setStyleSheet("""font-size: 18px; font-family: "Segoe UI"; background: #1E1E1E; color: #FFFFFF; border: 2px solid #FFFFFF;""")

        #* Scale Slider *#
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(200, 625, 400, 50)
        self.slider.setValue(10)    # Since we are dividing by 10, 10/10 = 1
        self.slider.setMinimum(10)
        self.slider.setMaximum(120)

        self.slider.setStyleSheet("""
            QSlider {border: 2px solid #FFFFFF; border-radius: 23px;}
            QSlider::groove:horizontal {background: #1E1E1E; height: 46px; border-radius: 23px;}
            QSlider::handle:horizontal {background: #FFFFFF; width: 46px; border-radius: 23px;}
            QSlider::handle:horizontal:hover {background: #818181;}
            QSlider::handle:horizontal:pressed {background: #747474;}
        """)
        self.slider.valueChanged.connect(self.scale_output)

        #* / Label *#
        self.division_button = self.create_label("/", 615, 625, 50, 50)

        #* Scale Label *#
        self.scale_label = self.create_label("1 - 12", 640, 625, 75, 50)
        self.scale_label.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; background: #1E1E1E; color: #A9A9A9; border: 2px solid #FFFFFF; border-radius: 8px;""")
        self.scale_label.setAlignment(Qt.AlignCenter)
        
        #* F1 Controls *#
        self.controls = self.create_label("F1 = Close Image", 735, 625, 185, 50)
        self.controls.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; background: #1E1E1E; color: #00FF00; border: 2px solid #FFFFFF; border-radius: 8px;""")
        self.controls.hide()

        #* Image Preview Label *#
        self.image_preview = self.create_label("", 510, 150, 500, 450)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""background: #1E1E1E; border: 2px solid #FFFFFF;""")
 
        #* Image Preview Text Overlay *#
        self.text_overlay = self.create_label("", 515, 155, 90, 36)
        self.text_overlay.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; background: transparent; color: #FFFFFF; border: none;""") 

        #* Position Label *#
        self.position_label = self.create_textbox("Position:", 60, 470, 130, 25)

        #* X Y Label *#
        self.x_position_text = self.create_textbox("X: ", 60, 500, 130, 25)
        self.y_position_text = self.create_textbox("Y: ", 60, 530, 130, 25)

        #* Unlock Button *#
        self.unlock_button = self.create_button("🔓", 510, 550, 50, 50)
        self.unlock_button.setStyleSheet("""QPushButton {font-size: 22px; background: transparent; border-radius: 8px;}""")
        self.unlock_button.clicked.connect(self.operation_click)
        self.unlock_button.raise_()

        #* Lock Button *#
        self.lock_button = self.create_button("🔒", 510, 550, 50, 50)
        self.lock_button.setStyleSheet("""QPushButton {font-size: 22px; background: transparent; border-radius: 8px;}""")
        self.lock_button.clicked.connect(self.operation_click)
        self.lock_button.hide()
        self.lock_button.raise_()

    # ---- Function to create a Button ---- #
    def create_button(self, text, x, y, width, height):
        button = QPushButton(text, self)
        button.setGeometry(x, y, width, height)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
        QPushButton {font-size: 22px; font-family: "Segoe UI"; background: #1E1E1E; color: #FFFFFF; border: 2px solid #FFFFFF; border-radius: 8px; padding-left: 3px;}
        QPushButton:hover {background-color: #444444;}
        """)
        return button
    
    # ---- Function to create a Label ---- #
    def create_label(self, text, x, y, width, height):
        label = QLabel(text, self)
        label.setGeometry(x, y, width, height)
        label.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; background: transparent; color: #FFFFFF;""")
        return label
    
    # ---- Function to create a Line_Edit ---- #
    def create_textbox(self, text, x, y, width, height):
        line_edit = QLineEdit(text, self)
        line_edit.setReadOnly(True)
        line_edit.setGeometry(x, y, width, height)
        line_edit.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; color: #FFFFFF; border: none;""")
        line_edit.setContextMenuPolicy(Qt.NoContextMenu)
        return line_edit
    
    # ---- Open Button Click Logic  ---- #
    def open_button_click(self):
        global draggable 

        draggable = True
        self.lock_button.hide()
        self.unlock_button.show()

        if hasattr(self, "overlay_window"):
            self.overlay_window.close()

        sources_folder = os.path.join(os.getcwd(), "sources")
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            sources_folder,  # Start in the sources folder
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if self.file_path:
            # Reset any old image_display so Load uses new image
            if hasattr(self, "image_display"):
                del self.image_display

            pixmap = QPixmap(self.file_path)
            self.image_preview.setGeometry(510, 150, 500, 450)
            self.image_preview.setStyleSheet("border: 2px solid #FFFFFF; background: #1E1E1E;")
            scaled_pixmap = pixmap.scaled(self.image_preview.size(), aspectRatioMode=1)  # Keep aspect ratio
            self.image_preview.setPixmap(scaled_pixmap)
            self.image_preview.setGeometry(510, 150, scaled_pixmap.width(), scaled_pixmap.height())

            self.text_overlay.setText(" Preview")
            self.text_overlay.setAlignment(Qt.AlignLeft)
            self.text_overlay.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; background: rgba(0, 0, 0, 128); color: #FFFFFF; border: none; border-radius: 10px;""")
            self.filename = os.path.basename(self.file_path)
        else:   # Removes preview box if you close the open folder
            self.scale_label.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; background: #1E1E1E; color: #A9A9A9; border: 2px solid #FFFFFF; border-radius: 8px;""")
            self.scale_label.setText("1 - 12")
            self.text_overlay.setStyleSheet("background: transparent;")
            self.text_overlay.clear()
            self.image_preview.setGeometry(510, 150, 500, 450)
            self.image_preview.clear()
            self.x_position_text.setText("X: ")
            self.y_position_text.setText("Y: ")

    # ---- Scale Slider Logic ---- #
    def scale_output(self, value):
        global num
        num = math.floor(value / 10)
        self.scale_label.setStyleSheet("""font-size: 22px; font-family: "Segoe UI"; background: #1E1E1E; color: #FFFFFF; border: 2px solid #FFFFFF; border-radius: 8px;""")
        self.scale_label.setText(f"{num:.0f}")

    # ---- Scale Logic ---- #
    def operation_confirm(self):
        global num
        if not hasattr(self, "file_path") or not self.file_path:
            return

        self.image_display = QMovie(self.file_path)
        self.image_display.start()
        self.image_display.stop()

        self.original_size = self.image_display.currentPixmap().size()

        scaled_width = int(self.original_size.width() / num)
        scaled_height = int(self.original_size.height() / num)

        self.image_display.setScaledSize(QSize(scaled_width, scaled_height))

        self.new_message = (f"🟢 {self.filename} Scaled by {num:.0f}")
        last_line = self.console.toPlainText().split('\n')[-1]
        if not last_line.endswith(f'{self.filename} Scaled by {num:.0f}'):
            self.console.append(self.new_message)

    # ---- Load Button Click Logic  ---- #
    def load_button_click(self):
        global data
        if not hasattr(self, "file_path") or not self.file_path:
            self.new_message = ('<span style="color: #FF0000;">🔴 No File to Load</span>')
            last_line = self.console.toPlainText().split('\n')[-1]
            if not last_line.endswith(f'No File to Load'):
                self.console.append(self.new_message)
            return  # No file selected

        self.overlay_window = QWidget()
        self.overlay_window.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.overlay_window.setAttribute(Qt.WA_TranslucentBackground)

        self.controls.show()

        # Load Settings
        try:
            if os.path.exists(settings_path):
                with open("settings.json", "r") as f:
                    data = json.load(f)
            
            if self.file_path in data and str(self.size_num) in data[self.file_path]:
                pos = data[self.file_path][str(self.size_num)]
                self.overlay_window.move(pos["x"], pos["y"])
                self.display_position()
        except:
            self.overlay_window.move(1500, 500)

        # Reuse pre-scaled image if available
        if hasattr(self, "image_display"):
            gif = self.image_display
        else:
            gif = QMovie(self.file_path)

        label = QLabel(self.overlay_window)
        label.setStyleSheet("background: transparent; border: none;")
        label.setMovie(gif)

        gif.start()

        label.resize(gif.scaledSize() or gif.currentPixmap().size())
        self.overlay_window.resize(label.size())
        self.overlay_window.show()

        self.overlay_window.mousePressEvent = self.overlay_mouse_press
        self.overlay_window.mouseMoveEvent = self.overlay_mouse_move
        self.overlay_window.keyPressEvent = self.overlay_controls

    # ---- Displays Text Position ---- #
    def display_position(self):
        self.x_position_text.setText(f"X: {self.overlay_window.x()}")
        self.y_position_text.setText(f"Y: {self.overlay_window.y()}")

    # ---- Selects the Image  ---- #
    def overlay_mouse_press(self, event):
        self.drag_offset = event.pos()

    # ---- Makes the Image Draggable  ---- #
    def overlay_mouse_move(self, event):
        if draggable and hasattr(self, 'drag_offset'):
            self.overlay_window.move(self.overlay_window.pos() + event.pos() - self.drag_offset)
            self.display_position()

    # ---- Save Settings  ---- #
    def save_pos_and_exit(self, event=None):
        if not hasattr(self, "file_path") or not self.file_path:
            self.new_message = (f'<span style="color: #FF0000;">🔴 No Position to Save</span>')
            last_line = self.console.toPlainText().split('\n')[-1]
            if not last_line.endswith(f'No Position to Save'):
                self.console.append(self.new_message)
            return

        # Get valid size_num
        try:
            self.size_num = num
        except ValueError:
            self.size_num = 1  # fallback if empty

        if self.file_path not in data:
            data[self.file_path] = {}

        data[self.file_path][str(self.size_num)] = {
            "x": self.overlay_window.x(),
            "y": self.overlay_window.y()
        }
        self.new_message = (f"🟢 Position Saved at: \n⭕ X: {self.overlay_window.x()} \n⭕ Y: {self.overlay_window.y()}")
        console_lines = self.console.toPlainText().split('\n')
        message_lines = self.new_message.split('\n')

        if console_lines[-len(message_lines):] != message_lines:
            self.console.append(self.new_message)

        with open("settings.json", "w") as f:
            json.dump(data, f, indent=4)

        if isinstance(event, QCloseEvent):
            event.accept()

    # ---- Function to Clear the Console  ---- #
    def clear_console(self):
        self.console.setText("🟢 Console Cleared")
        QTimer.singleShot(750, self.console.clear)

    # ---- Lock or Unlock ---- #
    def operation_click(self):
        if not hasattr(self, "file_path") or not self.file_path:
            return
        
        sender = self.sender()
        global draggable

        if sender == self.lock_button:
            self.lock_button.hide()
            self.unlock_button.show()
            self.console.append(f"🔓 {self.filename} Position Unlocked")
            draggable = True
        elif sender == self.unlock_button:
            self.unlock_button.hide()
            self.lock_button.show()
            self.console.append(f"🔒 {self.filename} Position Locked")
            draggable = False

    # ---- Function to Open settings.json  ---- #
    def setting_click(self):
        settings_path = os.path.join(app_dir(), "settings.json")
        if not os.path.exists(settings_path):
            last_line = self.console.toPlainText().split('\n')[-1]
            if "Settings.json does not exist" not in last_line:
                error_message = '<span style="color: #FF0000;">🔴 Settings.json does not exist</span>'
                self.console.append(error_message)
            return

        # Open the file only if it exists
        os.startfile(settings_path)

    # ---- Keybinds for the Image  ---- #
    def overlay_controls(self, event):
        # global draggable
        # if event.key() == Qt.Key_F2:
        #     self.lock_button.hide()
        #     self.unlock_button.show()
        #     draggable = not draggable
        if event.key() == Qt.Key_F1:
            self.x_position_text.setText("X: ")
            self.y_position_text.setText("Y: ")
            self.overlay_window.close()
            self.controls.hide()

    # # ---- Taskbar Setup ---- #
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Left click
            self.showNormal()
            self.raise_()
            self.activateWindow()

# ---- Helper to get app directory ---- #
def app_dir():
    if getattr(sys, 'frozen', False):
        # Running as .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as .py
        return os.path.dirname(os.path.abspath(__file__))
    
def exit_app():
    QApplication.quit()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()