import time
import smtplib
from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from log import logger


def send_email(gmail_user, gmail_pass, msg, retry=100, retry_sleep=30, timeout=15):
    initial_retry_cnt = retry

    sent_from = gmail_user
    send_to = ['909444321@text.gsm.gateway.com']
    send_cc = ['']
    send_bcc = ['usermail@gmail.com'] 
    subject = "Sechome Alert!"

    # create message - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] =  subject
    msg['From'] = sent_from
    msg['To'] = ", ".join(send_to)
    msg['cc'] = ", ".join(send_cc)
    text = f"""Door entered! """
    mime_text = MIMEText(text, 'plain')
    msg.attach(mime_text)

    while(retry > 0):
        try:
            logger.info("Sending message: " + msg.as_string())
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, None, None, None, timeout=10)
            server.ehlo()
            server.login(gmail_user, gmail_pass)
            server.sendmail(sent_from, send_to + send_cc + send_bcc, msg.as_string())
            server.close()
            logger.info("Message sent successfully!")
        except OSError as ex:
            logger.info("Message failed to send! Reason: " + str(ex))
            retry -= 1
            logger.info("Retry " + str(initial_retry_cnt - retry) + " of " + str(initial_retry_cnt))
            time.sleep(retry_sleep)
        else:
            retry = 0
