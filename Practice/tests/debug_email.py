import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.passw import EMAIL_ADDRESS, EMAIL_PASSWORD

def test_email():
    print("Диагностика отправки email...")
    print(f"Отправитель: {EMAIL_ADDRESS}")
    print(f"Получатель: {EMAIL_ADDRESS}")
    
    try:
        # Создаём сообщение с правильной кодировкой
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Тест 2FA'
        message['From'] = EMAIL_ADDRESS
        message['To'] = EMAIL_ADDRESS

        # Текст с кириллицей
        text = """Это тестовое письмо от вашего скрипта 2FA.
Если вы это читаете — всё работает! 🎉"""
        
        # Ключевой момент: указываем charset='utf-8'
        part = MIMEText(text, 'plain', 'utf-8')
        message.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(0)  # Отключаем логи для чистоты
        server.starttls()
        
        print("\nАвторизация...")
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("Вход выполнен!")
        
        print("\n Отправка письма...")
        #  send_message() корректно обрабатывает UTF-8
        server.send_message(message)
        print("Письмо отправлено!")
        
        server.quit()
        print("\nПроверьте почту (и папку Спам)!")
        
    except UnicodeEncodeError as e:
        print(f"\nОшибка кодировки: {e}")
        print("Убедитесь, что MIMEText создан с charset='utf-8'")
    except smtplib.SMTPAuthenticationError as e:
        print(f"\nОшибка авторизации: {e}")
    except Exception as e:
        print(f"\nОшибка: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_email()