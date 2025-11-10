"""
Security utilities for KeenAI-Quant Backend
API key validation, encryption, and security helpers
"""

import hashlib
import secrets
from typing import Optional
from cryptography.fernet import Fernet
import base64


class SecurityManager:
    """Manages security operations"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize security manager
        
        Args:
            encryption_key: Encryption key for sensitive data
        """
        if encryption_key:
            # Ensure key is proper length for Fernet
            key = hashlib.sha256(encryption_key.encode()).digest()
            self.cipher = Fernet(base64.urlsafe_b64encode(key))
        else:
            self.cipher = None
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as string
        """
        if not self.cipher:
            return data
        
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data as string
        """
        if not self.cipher:
            return encrypted_data
        
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key
        
        Returns:
            Random API key string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            hashed: Hashed password
            
        Returns:
            True if password matches
        """
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate API key format
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid format
        """
        if not api_key:
            return False
        
        # Check minimum length
        if len(api_key) < 20:
            return False
        
        return True


# Global security manager
security_manager = SecurityManager()
