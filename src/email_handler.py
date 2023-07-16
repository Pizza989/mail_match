from email.policy import default
import email.utils
import imaplib
import ssl
import os
import random
import email.parser
import getpass

def parse(email_b, storage_path='./attachments'):
    # email_b = binary email (b'...'), storage_path = relative or absolute path to store attachments
    email_message = email.message_from_bytes(email_b)  # converts raw email to email object

    parsed_dict = {
        'from': email.utils.parseaddr(email_message['From']),
        'to': email_message['to'],
        'subject': email_message['Subject'],
        'body_plain': '',
        'body_html': '',
        'attachments': []
    }

    for part in email_message.walk():  # iterates trough all parts of the email
        filename = part.get_filename()

        if bool(filename):  # if the part is actually an attachment, it will be True
            path = os.path.join(storage_path, filename)
            while os.path.isfile(path):  # while filename is already in use, try adding a random digit
                filesplit = filename.split('.')
                filename = filesplit[0] + '_' + str(random.randint(0, 99)) + '.' + filesplit[1]
                path = os.path.join(storage_path, filename)

            fp = open(path, 'wb')  # open/create attachment file
            parsed_dict['attachments'].append(filename)
            fp.write(part.get_payload(decode=True))
            fp.close()

        else:
            if part.get_content_type() == 'text/plain':  # save plain text email body
                parsed_dict['body_plain'] = part.get_payload(decode=True).decode('utf-8')
            elif part.get_content_type() == 'text/html':  # save html email body
                parsed_dict['body_html'] = part.get_payload(decode=True).decode('utf-8')

    return parsed_dict


class MailBox(imaplib.IMAP4_SSL):
    def __init__(self, config: dict, creds: tuple):
        """__init__.

        :param self:
        :param config: Must include 'host':str and 'port':int. Can also define 'keyfile':str, 'certfile':str, 'timeout':str
        :type config: dict
        :param creds: (username|email, password)
        :type creds: tuple
        """
        assert "host" in config, "port" in config
        host, port = config["host"], config["port"]
        
        probe_val = lambda x: config[x] if x in config else None
        keyfile = probe_val("keyfile")
        certfile = probe_val("certfile")
        timeout = probe_val("timeout")
        super().__init__(host, port, keyfile, certfile, ssl.create_default_context(), timeout)
        self.login(*creds)
    
    def emails(self, mailbox: str = "INBOX", parts: str = "ALL"):  # TODO: figure this out
        """emails. will return a dict containing all the neccessary data in the future

        :param self:
        :param mailbox:
        :type mailbox: str
        :param parts:
        :type parts: str
        """
        
        _, args = self.select(mailbox)
        length = int(args[0].decode())  # TODO: proper error handling

        for i in range(length, 1, -1):
            payload = self.fetch(str(i), parts)[1][0]
            yield parse(payload), int(payload.decode().split()[0])  # TODO: erros lmao, as if. last is index


    def modify_flags(self, message_set: str, add_flags: list[str] | None = None, remove_flags: list[str] | None = None, mailbox: str = "INBOX"):
        """modify_flags.

        :param self:
        :param message_set: defined in rfc2060
        :type message_set: str
        :param add_flags: wich flags to add
        :type add_flags: list[str] | None
        :param remove_flags: which flags to remove
        :type remove_flags: list[str] | None
        :param mailbox: what mailbox to use
        :type mailbox: str
        """
        self.select(mailbox)
        if add_flags:
            self.store(message_set, "+FLAGS.SILENT", " ".join(add_flags))
        if remove_flags:
            self.store(message_set, "-FLAGS.SILENT", " ".join(remove_flags))

    def get_flags(self, message_set: str, mailbox: str = "INBOX"):
        """get_flags.

        :param self:
        :param message_set: defined in rfc2060
        :type message_set: str
        :param mailbox: which mailbox to use
        :type mailbox: str
        """
        self.select(mailbox)
        return self.fetch(message_set, "FLAGS")[1]


if __name__ == "__main__":
    m = MailBox({"host": "imap.strato.de", "port": 993}, ("noah@simai.de", getpass.getpass()))
    for mail in m.emails("INBOX"):
        print(mail)

