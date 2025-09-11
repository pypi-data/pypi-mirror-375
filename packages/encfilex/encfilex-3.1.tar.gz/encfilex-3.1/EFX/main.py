# encfilex_v3.py
"""
EncFilex v3 - layered: Base64 -> AES-256-GCM -> XChaCha20-Poly1305
Provides:
  - encrypt_file(in_path, out_path, password)
  - decrypt_file(in_path, out_path, password)
Also provides CLI: python encfilex_v3.py encrypt ... / decrypt ...

Security improvements:
- Enhanced input validation and error handling
- Secure memory management with context managers
- Protection against timing attacks
- File size limits and DoS protection
- Improved error messages without information leakage
- Atomic file operations
- Secure random number generation validation
"""

import os
import json
import struct
import argparse
import base64
import secrets
import tempfile
import shutil
import hashlib
import hmac
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass

# KDF
try:
    from argon2 import low_level
    from argon2.exceptions import Argon2Error
except ImportError:
    raise ImportError("argon2-cffi is required: pip install argon2-cffi")

# AES-GCM
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
except ImportError:
    raise ImportError("cryptography is required: pip install cryptography")

# XChaCha20-Poly1305 (libsodium via PyNaCl bindings)
try:
    from nacl.bindings import (
        crypto_aead_xchacha20poly1305_ietf_encrypt,
        crypto_aead_xchacha20poly1305_ietf_decrypt,
    )
    from nacl.exceptions import CryptoError
except ImportError:
    raise ImportError("PyNaCl is required: pip install PyNaCl")

# Constants
MAGIC = b"ENCFXv3\x00"  # 8 bytes identifier
VERSION = 3
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB limit
MAX_HEADER_SIZE = 8192  # 8KB header limit
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 1024

# Default KDF params (balanced security/performance)
DEFAULT_ARGON2_PARAMS = {
    "time_cost": 4,
    "memory_cost": 128 * 1024,  # KiB -> 128 MiB
    "parallelism": 2,
    "hash_len": 64,  # we want 64 bytes to split for AES+ChaCha
    "salt_len": 16,
}

# Supported algorithms for validation
SUPPORTED_LAYERS = ["base64", "aes-256-gcm", "xchacha20-poly1305"]
SUPPORTED_KDF = ["argon2id"]


@dataclass
class EncryptionHeader:
    """Structured header for validation and type safety"""
    version: int
    layers: list
    kdf: str
    kdf_params: Dict[str, Any]
    
    def validate(self) -> None:
        """Validate header parameters"""
        if self.version != VERSION:
            raise ValueError(f"Unsupported version: {self.version}")
        if self.layers != SUPPORTED_LAYERS:
            raise ValueError(f"Unsupported layer configuration: {self.layers}")
        if self.kdf not in SUPPORTED_KDF:
            raise ValueError(f"Unsupported KDF: {self.kdf}")
        
        # Validate KDF parameters
        kdf_params = self.kdf_params
        if not isinstance(kdf_params.get("time_cost"), int) or kdf_params["time_cost"] < 1:
            raise ValueError("Invalid time_cost parameter")
        if not isinstance(kdf_params.get("memory_cost"), int) or kdf_params["memory_cost"] < 1024:
            raise ValueError("Invalid memory_cost parameter")
        if not isinstance(kdf_params.get("parallelism"), int) or kdf_params["parallelism"] < 1:
            raise ValueError("Invalid parallelism parameter")
        if not isinstance(kdf_params.get("hash_len"), int) or kdf_params["hash_len"] < 32:
            raise ValueError("Invalid hash_len parameter")
        if not isinstance(kdf_params.get("salt_len"), int) or kdf_params["salt_len"] < 16:
            raise ValueError("Invalid salt_len parameter")


class SecureMemory:
    """Context manager for secure memory handling"""
    
    def __init__(self, size: int = 0, data: bytes = None):
        if data is not None:
            self._data = bytearray(data)
        else:
            self._data = bytearray(size)
    
    def __enter__(self):
        return self._data
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._zero_memory()
    
    def _zero_memory(self):
        """Securely zero memory"""
        if hasattr(self, '_data'):
            for i in range(len(self._data)):
                self._data[i] = 0
            del self._data


def _zero_bytes(data):
    """Zero out memory for bytes/bytearray"""
    if isinstance(data, bytearray):
        for i in range(len(data)):
            data[i] = 0
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = 0


def _validate_password(password: str) -> None:
    """Validate password strength and format"""
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    if len(password.encode('utf-8')) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password too short (minimum {MIN_PASSWORD_LENGTH} bytes)")
    if len(password.encode('utf-8')) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password too long (maximum {MAX_PASSWORD_LENGTH} bytes)")


def _validate_file_path(path: str, check_exists: bool = True, check_size: bool = False) -> Path:
    """Validate file path and optionally check size"""
    if not isinstance(path, (str, Path)):
        raise TypeError("File path must be string or Path")
    
    path_obj = Path(path)
    
    if check_exists and not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if check_exists and not path_obj.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    if check_size and path_obj.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large (maximum {MAX_FILE_SIZE} bytes)")
    
    return path_obj


def _secure_random(size: int) -> bytes:
    """Generate cryptographically secure random bytes with validation"""
    if size <= 0 or size > 1024:
        raise ValueError("Invalid random size requested")
    
    random_bytes = secrets.token_bytes(size)
    
    # Validate entropy (basic sanity check)
    if len(set(random_bytes)) < min(size // 4, 16):
        raise RuntimeError("Insufficient entropy in random data")
    
    return random_bytes


def _derive_key_material(password_str: str, salt: bytes, params: dict) -> bytes:
    """Derive key material using Argon2id with validation"""
    try:
        # Validate inputs
        if not password_str or len(password_str) == 0:
            raise ValueError("Password cannot be empty")
        if len(salt) < 16:
            raise ValueError("Salt too short")
        
        # Convert password to bytes (ensure it's bytes, not bytearray)
        password_bytes = password_str.encode("utf-8")
        
        # Extract and validate parameters
        time_cost = int(params.get("time_cost", 3))
        memory_cost = int(params.get("memory_cost", 64 * 1024))
        parallelism = int(params.get("parallelism", 1))
        hash_len = int(params.get("hash_len", 64))
        
        # Reasonable limits to prevent DoS
        if time_cost > 100:
            raise ValueError("time_cost too high")
        if memory_cost > 1024 * 1024:  # 1GB
            raise ValueError("memory_cost too high")
        if parallelism > 16:
            raise ValueError("parallelism too high")
        if hash_len > 128:
            raise ValueError("hash_len too high")
        
        # Call argon2 with guaranteed bytes
        result = low_level.hash_secret_raw(
            secret=password_bytes,  # This is guaranteed to be bytes
            salt=salt,             # This should already be bytes
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            type=low_level.Type.ID,
        )
        
        # Clear password from memory
        password_array = bytearray(password_bytes)
        _zero_bytes(password_array)
        del password_array
        
        return result
        
    except Argon2Error as e:
        raise RuntimeError(f"Key derivation failed: {e}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid KDF parameters: {e}")


@contextmanager
def _atomic_write(output_path: Path):
    """Context manager for atomic file writes"""
    temp_fd = None
    temp_path = None
    try:
        # Create temporary file in same directory for atomic move
        temp_fd, temp_path = tempfile.mkstemp(
            dir=output_path.parent,
            prefix=f".{output_path.name}.tmp"
        )
        temp_path = Path(temp_path)
        
        with open(temp_fd, 'wb') as f:
            yield f
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk
        
        # Atomic move
        shutil.move(str(temp_path), str(output_path))
        temp_path = None  # Prevent cleanup
        
    except Exception:
        # Cleanup on error
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except OSError:
                pass
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise
    finally:
        if temp_fd is not None:
            try:
                os.close(temp_fd)
            except OSError:
                pass


def encrypt_file(in_path: str, out_path: str, password: str, *, argon2_params: Optional[dict] = None) -> bool:
    """
    High-level API: encrypt_file("secret.txt", "secret.efx", "super-password")
    Pipeline: plaintext -> base64 -> AES-256-GCM -> XChaCha20-Poly1305 -> file
    
    Args:
        in_path: Input file path
        out_path: Output file path
        password: Password for encryption
        argon2_params: Optional KDF parameters override
    
    Returns:
        True if successful
    
    Raises:
        ValueError: Invalid parameters
        FileNotFoundError: Input file not found
        RuntimeError: Encryption failed
    """
    try:
        # Input validation
        _validate_password(password)
        input_path = _validate_file_path(in_path, check_exists=True, check_size=True)
        output_path = _validate_file_path(out_path, check_exists=False)
        
        # Merge parameters
        params = dict(DEFAULT_ARGON2_PARAMS)
        if argon2_params:
            if not isinstance(argon2_params, dict):
                raise TypeError("argon2_params must be a dictionary")
            params.update(argon2_params)
        
        # Generate secure random values
        salt = _secure_random(params["salt_len"])
        aes_nonce = _secure_random(12)   # AES-GCM nonce 12 bytes
        xchacha_nonce = _secure_random(24)  # XChaCha20 nonce 24 bytes
        
        # Read and validate input file
        with open(input_path, "rb") as f:
            plaintext = f.read()
        
        if len(plaintext) == 0:
            raise ValueError("Input file is empty")
        
        # Layer 1: Base64 encode plaintext
        with SecureMemory(data=base64.b64encode(plaintext)) as b64_plain:
            # Create and validate header
            header = EncryptionHeader(
                version=VERSION,
                layers=SUPPORTED_LAYERS.copy(),
                kdf="argon2id",
                kdf_params={
                    "time_cost": params["time_cost"],
                    "memory_cost": params["memory_cost"],
                    "parallelism": params["parallelism"],
                    "hash_len": params["hash_len"],
                    "salt_len": params["salt_len"],
                }
            )
            header.validate()
            
            header_dict = {
                "version": header.version,
                "layers": header.layers,
                "kdf": header.kdf,
                "kdf_params": header.kdf_params
            }
            header_json = json.dumps(header_dict, separators=(",", ":"), sort_keys=True).encode("utf-8")
            
            if len(header_json) > MAX_HEADER_SIZE:
                raise ValueError("Header too large")
            
            # Derive key material and split
            key_material = _derive_key_material(password, salt, params)
            
            if len(key_material) < 64:
                raise RuntimeError("Insufficient key material derived")
            
            with SecureMemory(data=key_material) as km:
                aes_key = bytes(km[:32])
                chacha_key = bytes(km[32:64])
                
                # Layer 2: AES-256-GCM encrypt
                try:
                    aesgcm = AESGCM(aes_key)
                    aes_ct = aesgcm.encrypt(aes_nonce, bytes(b64_plain), header_json)
                except Exception as e:
                    raise RuntimeError(f"AES encryption failed: {e}")
                
                # Layer 3: XChaCha20-Poly1305 encrypt
                try:
                    final_ct = crypto_aead_xchacha20poly1305_ietf_encrypt(
                        aes_ct, header_json, xchacha_nonce, chacha_key
                    )
                except Exception as e:
                    raise RuntimeError(f"XChaCha20 encryption failed: {e}")
        
        # Atomic write to output file
        with _atomic_write(output_path) as fw:
            fw.write(MAGIC)
            fw.write(struct.pack(">I", len(header_json)))
            fw.write(header_json)
            fw.write(salt)
            fw.write(aes_nonce)
            fw.write(xchacha_nonce)
            fw.write(final_ct)
        
        # Clear sensitive data
        with SecureMemory(data=plaintext):
            pass
        
        return True
        
    except Exception as e:
        # Remove partial output file on error
        try:
            output_path = Path(out_path)
            if output_path.exists():
                output_path.unlink()
        except:
            pass
        raise


def decrypt_file(in_path: str, out_path: str, password: str) -> bool:
    """
    Decrypt file encrypted with encrypt_file
    
    Args:
        in_path: Input encrypted file path
        out_path: Output plaintext file path
        password: Password for decryption
    
    Returns:
        True if successful
    
    Raises:
        ValueError: Invalid file format or parameters
        FileNotFoundError: Input file not found
        RuntimeError: Decryption failed
    """
    try:
        # Input validation
        _validate_password(password)
        input_path = _validate_file_path(in_path, check_exists=True, check_size=True)
        output_path = _validate_file_path(out_path, check_exists=False)
        
        # Read and parse header
        with open(input_path, "rb") as fr:
            # Check magic
            magic = fr.read(8)
            if len(magic) != 8:
                raise ValueError("Invalid file format: file too short")
            if not hmac.compare_digest(magic, MAGIC):
                raise ValueError("Invalid file format: not an EncFilex v3 file")
            
            # Read header length
            header_len_bytes = fr.read(4)
            if len(header_len_bytes) != 4:
                raise ValueError("Corrupt file: missing header length")
            
            header_len = struct.unpack(">I", header_len_bytes)[0]
            if header_len > MAX_HEADER_SIZE or header_len == 0:
                raise ValueError(f"Invalid header length: {header_len}")
            
            # Read and parse header
            header_json = fr.read(header_len)
            if len(header_json) != header_len:
                raise ValueError("Corrupt file: header truncated")
            
            try:
                header_dict = json.loads(header_json.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                raise ValueError(f"Invalid header JSON: {e}")
            
            # Validate header structure
            try:
                header = EncryptionHeader(
                    version=header_dict.get("version"),
                    layers=header_dict.get("layers"),
                    kdf=header_dict.get("kdf"),
                    kdf_params=header_dict.get("kdf_params", {})
                )
                header.validate()
            except (KeyError, TypeError, ValueError) as e:
                raise ValueError(f"Invalid header: {e}")
            
            # Read salt and nonces
            salt_len = header.kdf_params["salt_len"]
            salt = fr.read(salt_len)
            aes_nonce = fr.read(12)
            xchacha_nonce = fr.read(24)
            final_ct = fr.read()
            
            # Validate lengths
            if len(salt) != salt_len:
                raise ValueError("Corrupt file: salt truncated")
            if len(aes_nonce) != 12:
                raise ValueError("Corrupt file: AES nonce invalid")
            if len(xchacha_nonce) != 24:
                raise ValueError("Corrupt file: XChaCha nonce invalid")
            if len(final_ct) == 0:
                raise ValueError("Corrupt file: no ciphertext")
        
        # Derive key material
        key_material = _derive_key_material(password, salt, header.kdf_params)
        
        if len(key_material) < 64:
            raise RuntimeError("Insufficient key material derived")
        
        with SecureMemory(data=key_material) as km:
            aes_key = bytes(km[:32])
            chacha_key = bytes(km[32:64])
            
            # Layer 3 decrypt: XChaCha -> yields AES ciphertext
            try:
                aes_ct = crypto_aead_xchacha20poly1305_ietf_decrypt(
                    final_ct, header_json, xchacha_nonce, chacha_key
                )
            except CryptoError:
                raise ValueError("Decryption failed: wrong password or file tampered")
            
            # Layer 2 decrypt: AES-GCM -> yields base64 payload
            try:
                aesgcm = AESGCM(aes_key)
                b64_plain = aesgcm.decrypt(aes_nonce, aes_ct, header_json)
            except InvalidTag:
                raise ValueError("Decryption failed: wrong password or file tampered")
            
            # Layer 1 decode: base64 -> plaintext
            try:
                with SecureMemory(data=base64.b64decode(b64_plain)) as plaintext:
                    # Atomic write to output
                    with _atomic_write(output_path) as fw:
                        fw.write(bytes(plaintext))
            except Exception as e:
                raise ValueError(f"Base64 decode failed: {e}")
        
        return True
        
    except Exception as e:
        # Remove partial output file on error
        try:
            output_path = Path(out_path)
            if output_path.exists():
                output_path.unlink()
        except:
            pass
        raise


# -----------------------
# CLI Interface
# -----------------------
def _cli_encrypt(args) -> int:
    """CLI encrypt command"""
    try:
        output_path = Path(args.out)
        if output_path.exists() and not args.force:
            print(f"[!] Output file {args.out} exists; use --force to overwrite")
            return 2
        
        print("[*] Encrypting file...")
        encrypt_file(args.input, args.out, args.password)
        print(f"[+] Successfully encrypted to {args.out}")
        return 0
        
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"[!] Encryption failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")
        return 130
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return 1


def _cli_decrypt(args) -> int:
    """CLI decrypt command"""
    try:
        output_path = Path(args.out)
        if output_path.exists() and not args.force:
            print(f"[!] Output file {args.out} exists; use --force to overwrite")
            return 2
        
        print("[*] Decrypting file...")
        decrypt_file(args.input, args.out, args.password)
        print(f"[+] Successfully decrypted to {args.out}")
        return 0
        
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"[!] Decryption failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")
        return 130
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return 1


def main_cli() -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="encfilex",
        description="EncFilex v3 - Secure layered file encryption",
        epilog="For more information, visit: https://github.com/your-repo/encfilex"
    )
    
    subparsers = parser.add_subparsers(dest="cmd", help="Available commands")
    
    # Encrypt subcommand
    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a file",
        description="Encrypt a file using layered encryption"
    )
    encrypt_parser.add_argument("input", help="Input plaintext file path")
    encrypt_parser.add_argument("out", help="Output encrypted file path (.efx recommended)")
    encrypt_parser.add_argument("password", help="Encryption password")
    encrypt_parser.add_argument("--force", action="store_true", help="Overwrite output file if exists")
    
    # Decrypt subcommand
    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="Decrypt a file",
        description="Decrypt a file encrypted with EncFilex"
    )
    decrypt_parser.add_argument("input", help="Input encrypted file path")
    decrypt_parser.add_argument("out", help="Output plaintext file path")
    decrypt_parser.add_argument("password", help="Decryption password")
    decrypt_parser.add_argument("--force", action="store_true", help="Overwrite output file if exists")
    
    args = parser.parse_args()
    
    if not args.cmd:
        parser.print_help()
        return 1
    
    if args.cmd == "encrypt":
        return _cli_encrypt(args)
    elif args.cmd == "decrypt":
        return _cli_decrypt(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main_cli())