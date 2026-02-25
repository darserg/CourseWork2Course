# email_sender.py
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
            print(f"Подготовка письма для {recipient_email}...")
            
            message = MIMEMultipart('alternative')
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = 'Код подтверждения (2FA)'

            # Текст письма с кириллицей
            body = f"""Здравствуйте!

Ваш код подтверждения: {code}

Код действителен 5 минут.
Если вы не запрашивали код, проигнорируйте это письмо.

С уважением,
Ваша команда безопасности 🛡️"""

            part = MIMEText(body, 'plain', 'utf-8')
            message.attach(part)

            print("Подключение к SMTP...")
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                print("Авторизация...")
                server.login(self.sender_email, self.sender_password)
                print("Отправка...")

                server.send_message(message)
                
            print("Письмо успешно отправлено!")
            return True
            
        except UnicodeEncodeError as e:
            print(f"Ошибка кодировки: {e}")
            print("Проверьте, что MIMEText создан с charset='utf-8'")
            return False
        except smtplib.SMTPAuthenticationError as e:
            print(f"Ошибка авторизации: {e}")
            return False
        except Exception as e:
            print(f"Ошибка: {type(e).__name__}: {e}")
            return False