"""
Secure storage utilities for device binding tokens.

Handles platform-specific secure storage of sensitive data.
Falls back gracefully when secure storage is not available.
"""

import os
import sys
import json
from typing import Optional, Dict, Any

class SecureStorage:
    """Platform-specific secure storage handler"""
    
    def __init__(self, app_name: str = "CorrectPQC"):
        self.app_name = app_name
        self.storage_backend = self._detect_backend()
    
    def _detect_backend(self) -> str:
        """Detect best available storage backend"""
        if sys.platform == "win32":
            try:
                import win32crypt
                return "dpapi"
            except ImportError:
                pass
        
        elif sys.platform == "darwin":
            # macOS - check for keychain availability
            if os.path.exists("/usr/bin/security"):
                return "keychain"
        
        elif sys.platform.startswith("linux"):
            try:
                import secretstorage
                return "libsecret"
            except ImportError:
                pass
        
        # Fallback to encrypted file
        return "encrypted_file"
    
    def store(self, key: str, data: Dict[str, Any]) -> bool:
        """Store data securely"""
        try:
            if self.storage_backend == "dpapi":
                return self._store_dpapi(key, data)
            elif self.storage_backend == "keychain":
                return self._store_keychain(key, data)
            elif self.storage_backend == "libsecret":
                return self._store_libsecret(key, data)
            else:
                return self._store_encrypted_file(key, data)
        except Exception as e:
            print(f"[secure_storage] Store failed: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data securely"""
        try:
            if self.storage_backend == "dpapi":
                return self._retrieve_dpapi(key)
            elif self.storage_backend == "keychain":
                return self._retrieve_keychain(key)
            elif self.storage_backend == "libsecret":
                return self._retrieve_libsecret(key)
            else:
                return self._retrieve_encrypted_file(key)
        except Exception as e:
            print(f"[secure_storage] Retrieve failed: {e}")
            return None
    
    def _store_dpapi(self, key: str, data: Dict[str, Any]) -> bool:
        """Store using Windows DPAPI"""
        try:
            import win32crypt
            import winreg
            
            json_data = json.dumps(data).encode()
            encrypted = win32crypt.CryptProtectData(json_data, f"{self.app_name}_{key}")
            
            # Store in registry
            reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                     f"Software\\{self.app_name}")
            winreg.SetValueEx(reg_key, key, 0, winreg.REG_BINARY, encrypted)
            winreg.CloseKey(reg_key)
            return True
            
        except Exception as e:
            print(f"[secure_storage] DPAPI store failed: {e}")
            return False
    
    def _retrieve_dpapi(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve using Windows DPAPI"""
        try:
            import win32crypt
            import winreg
            
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   f"Software\\{self.app_name}")
            encrypted, _ = winreg.QueryValueEx(reg_key, key)
            winreg.CloseKey(reg_key)
            
            decrypted = win32crypt.CryptUnprotectData(encrypted)[1]
            return json.loads(decrypted.decode())
            
        except Exception:
            return None
    
    def _store_keychain(self, key: str, data: Dict[str, Any]) -> bool:
        """Store using macOS Keychain"""
        try:
            import subprocess
            json_data = json.dumps(data)
            
            # Use security command line tool
            cmd = [
                'security', 'add-generic-password',
                '-a', self.app_name,
                '-s', key,
                '-w', json_data,
                '-U'  # Update if exists
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"[secure_storage] Keychain store failed: {e}")
            return False
    
    def _retrieve_keychain(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve using macOS Keychain"""
        try:
            import subprocess
            
            cmd = [
                'security', 'find-generic-password',
                '-a', self.app_name,
                '-s', key,
                '-w'  # Output password only
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            return None
            
        except Exception:
            return None
    
    def _store_libsecret(self, key: str, data: Dict[str, Any]) -> bool:
        """Store using Linux libsecret"""
        try:
            import secretstorage
            
            connection = secretstorage.dbus_init()
            collection = secretstorage.get_default_collection(connection)
            
            json_data = json.dumps(data)
            collection.create_item(
                f"{self.app_name}_{key}",
                {'application': self.app_name, 'key': key},
                json_data
            )
            return True
            
        except Exception as e:
            print(f"[secure_storage] libsecret store failed: {e}")
            return False
    
    def _retrieve_libsecret(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve using Linux libsecret"""
        try:
            import secretstorage
            
            connection = secretstorage.dbus_init()
            collection = secretstorage.get_default_collection(connection)
            
            items = collection.search_items({'application': self.app_name, 'key': key})
            if items:
                return json.loads(items[0].get_secret().decode())
            return None
            
        except Exception:
            return None
    
    def _store_encrypted_file(self, key: str, data: Dict[str, Any]) -> bool:
        """Fallback: store in encrypted file"""
        try:
            from .crypto import get_crypto_manager
            
            # Create app data directory
            if sys.platform == "win32":
                app_dir = os.path.join(os.environ.get('APPDATA', ''), self.app_name)
            else:
                app_dir = os.path.join(os.path.expanduser('~'), f'.{self.app_name.lower()}')
            
            os.makedirs(app_dir, exist_ok=True)
            
            # Encrypt the data
            json_data = json.dumps(data)
            crypto = get_crypto_manager()
            encrypted = crypto.obfuscate(json_data)
            
            # Store in file with restrictive permissions
            file_path = os.path.join(app_dir, f"{key}.dat")
            with open(file_path, 'w') as f:
                f.write(encrypted)
            
            # Set file permissions (Unix only)
            if hasattr(os, 'chmod'):
                os.chmod(file_path, 0o600)
            
            return True
            
        except Exception as e:
            print(f"[secure_storage] File store failed: {e}")
            return False
    
    def _retrieve_encrypted_file(self, key: str) -> Optional[Dict[str, Any]]:
        """Fallback: retrieve from encrypted file"""
        try:
            from .crypto import get_crypto_manager
            
            # Find the file
            if sys.platform == "win32":
                app_dir = os.path.join(os.environ.get('APPDATA', ''), self.app_name)
            else:
                app_dir = os.path.join(os.path.expanduser('~'), f'.{self.app_name.lower()}')
            
            file_path = os.path.join(app_dir, f"{key}.dat")
            if not os.path.exists(file_path):
                return None
            
            # Read and decrypt
            with open(file_path, 'r') as f:
                encrypted = f.read()
            
            crypto = get_crypto_manager()
            json_data = crypto.deobfuscate(encrypted)
            
            if json_data:
                return json.loads(json_data)
            return None
            
        except Exception:
            return None

# Global instance
_secure_storage = None

def get_secure_storage() -> SecureStorage:
    """Get or create global secure storage instance"""
    global _secure_storage
    if _secure_storage is None:
        _secure_storage = SecureStorage()
    return _secure_storage
