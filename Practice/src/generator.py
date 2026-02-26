import secrets
from datetime import datetime, timedelta


# noinspection PyArgumentList
class CodeGenerator:
    CODE_LENGTH = 6
    EXPIRY_MINUTES = 5

    def generate(self) -> str:
        return secrets.token_hex(3).upper()

    def get_expiry_time(self) -> datetime:
        return datetime.now() + timedelta(minutes=self.EXPIRY_MINUTES)

    def generate_with_expiry(self) -> tuple[str, datetime]:
        code = self.generate()
        expiry = self.get_expiry_time()
        return code, expiry