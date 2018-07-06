from smtplib import SMTP
from itertools import chain
from errno import ECONNREFUSED
from mimetypes import guess_type
from subprocess import Popen, PIPE
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from socket import error as SocketError
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from os.path import abspath, basename
from logger_mod import Logger

class Mailer(object):

    def __init__(self, to, subject, text, **params):
        self.to = to
        self.subject = subject
        self.text = text
        self.cc = params.get("cc", [])
        self.bcc = params.get("bcc", [])
        self.files = params.get("files", [])
        self.sender = params.get("sender", "krishnachandra.sharma@visiblealpha.com")


    def get_mimetype(self, filename):
        """Returns the MIME type of the given file.

        :param filename: A valid path to a file
        :type filename: str

        :returns: The file's MIME type
        :rtype: tuple
        """

        content_type, encoding = guess_type(filename)
        if content_type is None or encoding is not None:
            content_type = "application/octet-stream"
        return content_type.split("/", 1)


    def mimify_file(self, filename):
        """Returns an appropriate MIME object for the given file.

        :param filename: A valid path to a file
        :type filename: str

        :returns: A MIME object for the givne file
        :rtype: instance of MIMEBase
        """

        # filename = abspath(expanduser(filename))
        basefilename = basename(filename)

        msg = MIMEBase(*self.get_mimetype(filename))
        msg.set_payload(open(filename, "rb").read())
        msg.add_header("Content-Disposition", "attachment", filename=basefilename)

        encode_base64(msg)

        Logger.logger.info("Attaching filename {0}.".format(filename))

        return msg


    def send_email(self):
        """Send an outgoing email with the given parameters.

        This function assumes your system has a valid MTA (Mail Transfer Agent)
        or local SMTP server. This function will first try a local SMTP server
        and then the system's MTA (/usr/sbin/sendmail) connection refused.

        :param to: A list of recipient email addresses.
        :type to: list

        :param subject: The subject of the email.
        :type subject: str

        :param test: The text of the email.
        :type text: str

        :param params: An optional set of parameters. (See below)
        :type params; dict

        Optional Parameters:
        :cc: A list of Cc email addresses.
        :bcc: A list of Cc email addresses.
        :files: A list of files to attach.
        :sender: A custom sender (From:).
        """

        recipients = list(chain(self.to, self.cc, self.bcc))

        # Prepare Message
        msg = MIMEMultipart()
        msg.preamble = self.subject
        msg.add_header("From", self.sender)
        msg.add_header("Subject", self.subject)
        msg.add_header("To", ", ".join(self.to))
        self.cc and msg.add_header("Cc", ", ".join(self.cc))

        # Attach the main text
        msg.attach(MIMEText(self.text))

        # Attach any files
        [msg.attach(self.mimify_file(filename)) for filename in self.files]

        # Contact local SMTP server and send Message
        try:
            smtp = SMTP()
            smtp.connect()
            smtp.sendmail(self.sender, recipients, msg.as_string())
            Logger.logger.info("Email sent to {0} from {1}.".format(", ".join(recipients), self.sender))
            smtp.quit()
        except SocketError as e:
            if e.args[0] == ECONNREFUSED:
                p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
                p.communicate(msg.as_string())
                Logger.logger.debug("Sending email with Unix's sendmail, smtp feature failed with SockerError")
            else:
                Logger.logger.error("Failed to send email.")
                raise

    def test(self):
        self.send_email()


if __name__ == "__main__":
    mailer = Mailer(["krishnachandra.sharma@visiblealpha.com"], "Test", "Test Lol", files=["/tmp/rofl.log"], cc=[], bcc=[], sender="krishnachandra.sharma@visiblealpha.com")
    mailer.test()