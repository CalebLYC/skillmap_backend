import random
import string
from passlib.context import CryptContext


class SecurityUtils:
    _instance = None
    _pwd_context = None

    # Singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityUtils, cls).__new__(cls)
            cls._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return cls._instance

    @staticmethod
    def hash_password(password: str) -> str:
        # S'assurer que le singleton est instancié
        if SecurityUtils._pwd_context is None:
            SecurityUtils()
        # Hash le mot de passe passé en paramètre
        return SecurityUtils._pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        # S'assurer que le singleton est instancié
        if SecurityUtils._pwd_context is None:
            SecurityUtils()
        return SecurityUtils._pwd_context.verify(plain, hashed)

    def generate_random_password(length: int = 12) -> str:
        """
        Génère un mot de passe aléatoire.
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(characters) for _ in range(length))
