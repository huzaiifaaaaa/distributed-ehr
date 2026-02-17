from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import hashlib

def get_encryption_key(key_string):
    """Generate a valid Fernet key from a string"""
    key_bytes = key_string.encode()
    key_hash = hashlib.sha256(key_bytes).digest()
    return base64.urlsafe_b64encode(key_hash)

class Encryptor:
    def __init__(self, key_string):
        self.fernet = Fernet(get_encryption_key(key_string))
    
    def encrypt(self, plaintext):
        if plaintext is None:
            return None
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, encrypted_text):
        if encrypted_text is None:
            return None
        return self.fernet.decrypt(encrypted_text.encode()).decode()

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)
