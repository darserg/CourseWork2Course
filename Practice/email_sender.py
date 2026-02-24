import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passw import EMAIL_ADDRESS, EMAIL_PASSWORD

class EmailSender:
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

    def __init__(self):
        self.sender_email = EMAIL_ADDRESS
        self.sender_password = EMAIL_PASSWORD

    def send_verification_code(self, recipient_email: str, code: str) -> bool:
        try:
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = 'Код подтверждения (2FA)'

            body = f"""
Здравствуйте!

Ваш код подтверждения: {code}

Код действителен 5 минут.
Если вы не запрашивали код, проигнорируйте это письмо.

С уважением,
Ваша команда безопасности
"""
            message.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            return True
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")
            return False