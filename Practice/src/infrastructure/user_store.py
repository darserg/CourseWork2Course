import json
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


# noinspection PyArgumentList
class UserStore:
    """Простое файловое хранилище пользователей (заглушка для БД)"""
    
    def __init__(self, db_file: str = "src/infrastructure/users.json"):
        self.db_path = Path(db_file)
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Создаёт файл БД, если он не существует"""
        if not self.db_path.exists():
            self._save_data({"users": {}})

    def _load_data(self) -> Dict:
        """Загружает данные из JSON-файла"""
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self, data: Dict):
        """Сохраняет данные в JSON-файл"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

    @staticmethod
    def _generate_salt() -> str:
        """Генерирует случайную соль"""
        return secrets.token_hex(16)

    def register_user(self, email: str, password: str) -> Dict[str, any]:
        """
        Регистрирует нового пользователя.
        Returns: {'success': bool, 'message': str}
        """
        email = email.lower().strip()
        data = self._load_data()

        if email in data["users"]:
            return {"success": False, "message": "Пользователь уже существует"}

        if len(password) < 6:
            return {"success": False, "message": "Пароль слишком короткий"}

        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)

        data["users"][email] = {
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
            "is_verified": False  # Для 2FA
        }

        self._save_data(data)
        return {"success": True, "message": "Пользователь зарегистрирован"}

    def verify_user(self, email: str, password: str) -> bool:
        """Проверяет логин и пароль"""
        email = email.lower().strip()
        data = self._load_data()

        if email not in data["users"]:
            return False

        user = data["users"][email]
        password_hash = self._hash_password(password, user["salt"])
        
        # Безопасное сравнение хешей
        return secrets.compare_digest(password_hash, user["password_hash"])

    def get_user(self, email: str) -> Optional[Dict]:
        """Получает данные пользователя (без пароля)"""
        email = email.lower().strip()
        data = self._load_data()
        user = data["users"].get(email)
        
        if user:
            return {
                "email": email,
                "created_at": user["created_at"],
                "is_verified": user.get("is_verified", False)
            }
        return None

    def set_verified(self, email: str, verified: bool = True):
        """Отмечает пользователя как прошедшего 2FA"""
        email = email.lower().strip()
        data = self._load_data()
        
        if email in data["users"]:
            data["users"][email]["is_verified"] = verified
            self._save_data(data)

    def list_users(self) -> List[str]:
        """Возвращает список всех email'ов (для отладки)"""
        data = self._load_data()
        return list(data["users"].keys())

    def delete_user(self, email: str) -> bool:
        """Удаляет пользователя"""
        email = email.lower().strip()
        data = self._load_data()
        
        if email in data["users"]:
            del data["users"][email]
            self._save_data(data)
            return True
        return False