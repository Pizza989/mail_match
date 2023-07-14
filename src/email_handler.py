import imaplib
import ssl
import time
import json
import getpass

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
    
    def fetch_emails(self, mailbox="INBOX", parts="ALL"):
        """fetch_emails.
        Fetches all emails within the specified mailbox sorted ascendingly with their date

        :param self:
        :param mailbox: which mailbox to use
        :param parts: what parts of each mail to include lookup rfc2060 for syntax
        """
        self.select(mailbox)
        return self.fetch("1:*", parts)[1]

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
    with open("config/default.json", "r") as file:
        config = json.load(file)

    m = MailBox(config, (getpass.getpass(prompt="Email: "), getpass.getpass()))
    for mail in m.fetch_emails("INBOX", "BODY[HEADER.FIELDS (SUBJECT)]"):
        print(mail)
        time.sleep(1)

