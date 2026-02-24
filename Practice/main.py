from generator import CodeGenerator
from email_sender import EmailSender
from datetime import datetime
from typing import Dict, Optional
import secrets

class TwoFactorAuth:
    def __init__(self):
        self.generator = CodeGenerator()
        self.email_sender = EmailSender()
        self.codes: Dict[str, Dict] = {}
        self.max_attempts = 3

    def request_code(self, user_email: str) -> bool:
        code, expiry = self.generator.generate_with_expiry()
        self.codes[user_email] = {
            'code': code,
            'expiry': expiry,
            'attempts': 0
        }
        print(f"📧 Отправка кода на {user_email}...")
        return self.email_sender.send_verification_code(user_email, code)

    def verify_code(self, user_email: str, user_code: str) -> bool:
        if user_email not in self.codes:
            return False

        data = self.codes[user_email]

        if datetime.now() > data['expiry']:
            del self.codes[user_email]
            print("⏰ Код истёк.")
            return False

        if data['attempts'] >= self.max_attempts:
            del self.codes[user_email]
            print("🔒 Превышено количество попыток.")
            return False

        if secrets.compare_digest(data['code'], user_code.upper()):
            del self.codes[user_email]
            return True

        data['attempts'] += 1
        print(f"❌ Неверный код. Осталось попыток: {self.max_attempts - data['attempts']}")
        return False

def main():
    auth = TwoFactorAuth()
    user_email = input("Введите ваш email: ").strip()

    if not auth.request_code(user_email):
        print("❌ Не удалось отправить код.")
        return

    for attempt in range(3):
        code = input(f"Введите код ({3 - attempt} попыток осталось): ").strip()
        if auth.verify_code(user_email, code):
            print("✅ Успешная аутентификация!")
            return

    print("🔒 Доступ заблокирован.")

if __name__ == "__main__":
    main()