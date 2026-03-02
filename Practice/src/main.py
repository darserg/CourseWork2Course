from infrastructure.user_store import UserStore
from src.TwoFactorAuth import TwoFactorAuth


def main():
    # Инициализируем хранилище и систему 2FA
    user_store = UserStore("../users.json")
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