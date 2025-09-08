"""
Cryptographic operations for secure environment variable storage.
Uses GPG for encryption/decryption of profile data.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, List

class CryptoManager:
    def __init__(self, vault_dir: str = "~/.apivault"):
        """Initialize the crypto manager with the vault directory."""
        self.vault_dir = os.path.expanduser(vault_dir)
        self.profiles_dir = os.path.join(self.vault_dir, "profiles")
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure vault and profiles directories exist."""
        os.makedirs(self.profiles_dir, exist_ok=True)
        # Secure the directories
        os.chmod(self.vault_dir, 0o700)
        os.chmod(self.profiles_dir, 0o700)

    def encrypt_profile(self, profile_name: str, env_vars: Dict[str, str]) -> bool:
        """
        Encrypt environment variables for a profile using GPG.
        
        Args:
            profile_name: Name of the profile
            env_vars: Dictionary of environment variables
            
        Returns:
            bool: True if encryption was successful
        """
        profile_path = os.path.join(self.profiles_dir, f"{profile_name}.env.gpg")
        
        # Create temporary file with environment variables
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            for key, value in env_vars.items():
                temp_file.write(f'export {key}="{value}"\n')
            temp_path = temp_file.name

        try:
            # Secure the temporary file
            os.chmod(temp_path, 0o600)
            
            # Encrypt the file using GPG with symmetric encryption
            # Use --batch mode with passphrase from stdin
            result = subprocess.run([
                'gpg',
                '--batch',
                '--symmetric',  # Use symmetric encryption
                '--cipher-algo', 'AES256',  # Use AES256 encryption
                '--yes',        # Answer yes to any questions
                '--passphrase', 'sevn_default_passphrase',  # Use a default passphrase
                '--output', profile_path,
                temp_path
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                print(f"GPG encryption failed: {result.stderr}", file=sys.stderr)
            return result.returncode == 0
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def decrypt_profile(self, profile_name: str) -> Optional[str]:
        """
        Decrypt a profile's environment variables.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Optional[str]: Decrypted environment variables or None if decryption fails
        """
        profile_path = os.path.join(self.profiles_dir, f"{profile_name}.env.gpg")
        
        if not os.path.exists(profile_path):
            return None
            
        try:
            # Decrypt the file directly to stdout
            result = subprocess.run([
                'gpg',
                '--batch',
                '--decrypt',
                '--quiet',  # Reduce noise in output
                '--passphrase', 'sevn_default_passphrase',  # Use the same default passphrase
                profile_path
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                return None
                
            return result.stdout
        except subprocess.SubprocessError:
            return None

    def list_profiles(self) -> List[str]:
        """List all available profiles."""
        profiles = []
        for file in os.listdir(self.profiles_dir):
            if file.endswith('.env.gpg'):
                profiles.append(file[:-8])  # Remove .env.gpg extension
        return sorted(profiles)

    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile's encrypted file."""
        profile_path = os.path.join(self.profiles_dir, f"{profile_name}.env.gpg")
        try:
            os.unlink(profile_path)
            return True
        except OSError:
            return False 