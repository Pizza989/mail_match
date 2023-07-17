import getpass

from PyQt5.QtWidgets import QFrame, QPushButton, QLabel, QMainWindow, QApplication, QTextBrowser
from PyQt5 import uic
import sys
import email_handler


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/static/preview.ui", self)
        self.mail_frame: QFrame
        self.subject_label: QLabel
        self.sender_ppicture_label: QLabel
        self.sender_name_label: QLabel
        self.sending_time_label: QLabel
        self.email_body_browser: QTextBrowser
        self.sleft_button: QPushButton
        self.sright_button: QPushButton

        self.sleft_button.clicked.connect(lambda: self.swipe(left=True))
        self.sright_button.clicked.connect(lambda: self.swipe(left=False))

        self.config = None  # TODO: Pop-Up to configure
        self.left_add = None
        self.left_rm = None
        self.right_add = None
        self.right_rm = None

        self.__index = None

        self.mailbox = email_handler.MailBox({"host": "imap.strato.de", "port": 993},
                                            ("noah@simai.de", getpass.getpass()))
        self.email_gen = self.mailbox.emails()
        #print(next(self.email_gen))

        self.load_email(*next(self.email_gen))

        self.show()

    def load_email(self, email: dict, index: int):
        self.subject_label.setText(email["Subject"])
        self.sending_time_label.setText(email["Date"])
        self.sender_name_label.setText(email["From"])
        # self.email_body_browser.setText(email["Content"]) TODO: No words needed xD

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
