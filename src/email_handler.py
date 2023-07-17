import email.utils
import email.message
import imaplib
import ssl
import email.parser
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
    
    def emails(self, mailbox: str = "INBOX"):  # TODO: figure this out
        """emails. will return a dict containing all the neccessary data in the future

        :param self:
        :param mailbox:
        :type mailbox: str
        :param parts:
        :type parts: str
        """

        try:
            _, args = self.select(mailbox)
            length = int(args[0].decode())
            for i in range(length, 1, -1):
                _, payload = self.fetch(str(i), "(BODY.PEEK[HEADER] BODY.PEEK[TEXT])")
                print(payload)
                for response_part in payload:
                    if isinstance(response_part, tuple):
                        yield email.message_from_bytes(response_part[1]), i
                        break

        except imaplib.IMAP4_SSL.error as error:
            raise error


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
    for mail, index in m.emails("INBOX"):
        print(mail)
        exit()

