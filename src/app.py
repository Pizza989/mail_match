import getpass
import os

from PyQt5.QtWidgets import QCheckBox, QDialog, QFrame, QLineEdit, QMessageBox, QPushButton, QLabel, QMainWindow, QApplication, QTextEdit
from PyQt5 import uic
import sys
import src.email_handler
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel
import json

IMAP_CONFIG_PATH = "src/config/imap.json"
APP_CONFIG_PATH = "src/config/app.json"

def get_contrast_color(color):
    luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"

def create_profile_picture(email_from: str):
    size = 50
    color = (random.randint(0, 123), random.randint(0, 123), random.randint(0, 123))
    image = Image.new('RGB', (size, size), color=color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", size // 2)
    draw.text((size/2, size/2), email_from.capitalize()[0] , font=font, anchor="mm", color=get_contrast_color(color))
    image.save('src/static/profile_picture.png')

class ConfigDialog(QDialog):
    def __init__(self, parent) -> None:
       super().__init__(parent)
       self.config = {}
       self.setModal(True)

    def write_config(self):
        raise NotImplementedError()
    
    def get_config(self):
        raise NotImplementedError()

    def reject(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Cannot Reject")
        msg_box.setText("Please click the 'Save' button to close the dialog.")
        msg_box.exec_()


# TODO: Refactor to subclasses
class ImapConfig(ConfigDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        uic.loadUi("src/static/imap_config.ui", self)
        self.host_label: QLabel
        self.port_label: QLabel
        self.email_addr_label: QLabel
        self.password_label: QLabel
        self.host_lineedit: QLineEdit
        self.port_lineedit: QLineEdit
        self.email_addr_lineedit: QLineEdit
        self.password_lineedit: QLineEdit
        self.save_checkbox: QCheckBox
 
        self.accepted.connect(self.write_config)
    
    def write_config(self):
        self.config["host"] = self.host_lineedit.text()
        self.config["port"] = int(self.port_lineedit.text())
        self.config["email_address"] = self.email_addr_lineedit.text()
        self.config["password"] = self.password_lineedit.text()

    def get_config(self):
        self.exec_()
        if self.save_checkbox.isChecked():
            with open(IMAP_CONFIG_PATH, "w") as file:
                json.dump(self.config, file)
        return self.config


class AppConfig(ConfigDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        uic.loadUi("src/static/app_config.ui", self)
        self.lsa_label: QLabel
        self.lsr_label: QLabel
        self.rsa_label: QLabel
        self.rsr_label: QLabel
        self.lsa_lineedit: QLineEdit
        self.lsr_lineedit: QLineEdit
        self.rsa_lineedit: QLineEdit
        self.rsr_lineedit: QLineEdit
        self.save_checkbox: QCheckBox

        self.accepted.connect(self.write_config)

    def write_config(self):
        self.config["lsa"] = self.lsa_lineedit.text().split()
        self.config["lsr"] = self.lsr_lineedit.text().split()
        self.config["rsa"] = self.rsa_lineedit.text().split()
        self.config["rsr"] = self.rsr_lineedit.text().split()

    def get_config(self):
        self.exec_()
        if self.save_checkbox.isChecked():
            with open(APP_CONFIG_PATH, "w") as file:
                json.dump(self.config, file)
        return self.config


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/static/preview.ui", self)
        self.mail_frame: QFrame
        self.subject_label: QLabel
        self.pfp_label: QLabel
        self.from_label: QLabel
        self.to_label: QLabel
        self.date_label: QLabel
        self.body_textedit: QTextEdit
        self.left_button: QPushButton
        self.right_button: QPushButton

        self.left_button.clicked.connect(lambda: self.swipe(left=True))
        self.right_button.clicked.connect(lambda: self.swipe(left=False))
       
        self.imap_config = None
        self.app_config = None

        self.left_add = None
        self.left_rm = None
        self.right_add = None
        self.right_rm = None

        self.mailbox = None
        self.email_gen = None

        self.__index = None
        
        # Load Config
        if os.path.exists(IMAP_CONFIG_PATH):
            with open(IMAP_CONFIG_PATH, "r") as file:
                self.imap_config = json.load(file)
        else:
            popup = ImapConfig(self)
            self.imap_config = popup.get_config()  
         
        # Load App Config
        if os.path.exists(APP_CONFIG_PATH):
            with open(APP_CONFIG_PATH, "r") as file:
                self.app_config = json.load(file)
        else:
            popup = AppConfig(self)
            self.app_config = popup.get_config()

        # Connect to MailBox
        self.mailbox = src.email_handler.MailBox(self.imap_config, (self.imap_config["email_address"], self.imap_config["password"]))
        self.email_gen = self.mailbox.emails()
        self.load_email(*next(self.email_gen))

        self.show()

    def load_email(self, email, index: int):
        self.subject_label.setText(email["Subject"])
        self.date_label.setText(email["Date"])
        self.from_label.setText(email["From"])
        self.to_label.setText(email["To"])
        create_profile_picture(email["From"])
        self.pfp_label.setPixmap(QPixmap("src/static/profile_picture.png"))
        for part in email.walk():
            match part.get_content_type():
                case "text/plain":
                    self.body_textedit.setPlainText(part.get_payload())
                case "text/html":
                    self.body_textedit.setHtml(part.get_payload())
                case _:
                    continue

        self.__index = index

    def swipe(self, left: bool):
        if left:
            add_list = self.left_add
            rm_list = self.left_rm

        else:
            add_list = self.right_add
            rm_list = self.right_rm

        self.mailbox.modify_flags(str(self.__index), add_list, rm_list)
        self.load_email(*next(self.email_gen))



app = QApplication(sys.argv)
window = UI()
app.exec_()

