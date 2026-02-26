from src.services.generator import CodeGenerator
from src.services.email_sender import EmailSender
from src.infrastructure.user_store import UserStore
from datetime import datetime
from typing import Dict
import secrets

class TwoFactorAuth:
    def __init__(self, user_store: UserStore):
        self.generator = CodeGenerator()
        self.email_sender = EmailSender()
        self.user_store = user_store
        self.codes: Dict[str, Dict] = {}
        self.max_attempts = 3

    def login(self, email: str, password: str) -> bool:
        """Первый этап: проверка логина и пароля"""
        return self.user_store.verify_user(email, password)

    def request_code(self, user_email: str) -> bool:
        """Второй этап: отправка кода 2FA"""
        # Проверяем, что пользователь существует
        if not self.user_store.get_user(user_email):
            return False
            
        code, expiry = self.generator.generate_with_expiry()
        self.codes[user_email] = {
            'code': code,
            'expiry': expiry,
            'attempts': 0
        }
        print(f"📧 Отправка кода на {user_email}...")
        return self.email_sender.send_verification_code(user_email, code)

    def verify_code(self, user_email: str, user_code: str) -> bool:
        """Третий этап: проверка кода 2FA"""
        if user_email not in self.codes:
            return False

        data = self.codes[user_email]

        if datetime.now() > data['expiry']:
            del self.codes[user_email]
            print("Код истёк.")
            return False

        if data['attempts'] >= self.max_attempts:
            del self.codes[user_email]
            print("Превышено количество попыток.")
            return False

        if secrets.compare_digest(data['code'], user_code.upper()):
            del self.codes[user_email]
            self.user_store.set_verified(user_email, True)  # ✅ Помечаем как верифицированного
            return True

        data['attempts'] += 1
        print(f"Неверный код. Осталось попыток: {self.max_attempts - data['attempts']}")
        return False

def main():
    # Инициализируем хранилище и систему 2FA
    user_store = UserStore("users.json")
    auth = TwoFactorAuth(user_store)
    
    print("Система двухфакторной аутентификации")
    print("1 — Войти\n2 — Зарегистрироваться\n")
    choice = input("Выберите действие: ").strip()

    email = input("Email: ").strip()
    
    if choice == "2":
        password = input("🔑 Придумайте пароль (мин. 6 символов): ").strip()
        result = user_store.register_user(email, password)
        print(f"{'✅' if result['success'] else '❌'} {result['message']}")
        if not result['success']:
            return

    elif choice == "1":
        if not user_store.get_user(email):
            print("Пользователь не найден. Сначала зарегистрируйтесь.")
            return
    else:
        print("Неверный выбор")
        return

    # Проверка пароля
    password = input("Введите пароль: ").strip()
    if not auth.login(email, password):
        print("Неверный пароль")
        return

    print("Пароль верен. Требуется подтверждение по email.")
    
    # Отправка и проверка кода 2FA
    if not auth.request_code(email):
        print("Не удалось отправить код.")
        return

    for attempt in range(3):
        code = input(f"Введите код ({3 - attempt} попыток осталось): ").strip()
        if auth.verify_code(email, code):
            print("Успешная аутентификация! Добро пожаловать.")
            return

    print("Доступ заблокирован.")

if __name__ == "__main__":
    main()