import getpass

from PyQt5.QtWidgets import QFrame, QPushButton, QLabel, QMainWindow, QApplication, QTextEdit
from PyQt5 import uic
import sys
import email_handler
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel
import json

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


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/static/preview.ui", self)
        self.mail_frame: QFrame
        self.subject_label: QLabel
        self.pfp_label: QLabel
        self.from_label: QLabel
        self.date_label: QLabel
        self.body_textedit: QTextEdit
        self.left_button: QPushButton
        self.right_button: QPushButton

        self.left_button.clicked.connect(lambda: self.swipe(left=True))
        self.right_button.clicked.connect(lambda: self.swipe(left=False))

        self.config = None  # TODO: Pop-Up to configure
        self.left_add = None
        self.left_rm = None
        self.right_add = None
        self.right_rm = None

        self.__index = None

        with open("src/config/default.json", "r") as file:
            self.config = json.load(file)
        credentials = (getpass.getpass("Email: "), getpass.getpass())
        if(self.config["host"] == ""):
            self.config["host"] = "imap." + credentials[0].split("@")[1]
        self.mailbox = email_handler.MailBox(self.config, credentials)
        self.email_gen = self.mailbox.emails()

        self.load_email(*next(self.email_gen))

        self.show()

    def load_email(self, email, index: int):
        self.subject_label.setText(email["Subject"])
        self.date_label.setText(email["Date"])
        self.from_label.setText(email["From"])
        create_profile_picture(email["From"])
        self.pfp_label.setPixmap(QPixmap("src/static/profile_picture.png"))

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

