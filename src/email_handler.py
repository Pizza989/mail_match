import imaplib
import ssl
import time
import json
import getpass

class MailBox(imaplib.IMAP4_SSL):
    def __init__(self, config: dict, creds: tuple):
        """__init__.

        :param self:
        :param config: Must include 'host' and 'port'. Can also define 'keyfile', 'certfile', 'timeout'
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
    
    def fetch_emails(self, mailbox="INBOX"):
        self.select(mailbox)
        for mail in self.fetch("0:*", "ALL")[1]:
            yield mail

if __name__ == "__main__":
    with open("config/default.json", "r") as file:
        config = json.load(file)

    m = MailBox(config, (getpass.getpass(prompt="Email: "), getpass.getpass()))
    for mail in m.fetch_emails():
        print(mail)
        time.sleep(1)

