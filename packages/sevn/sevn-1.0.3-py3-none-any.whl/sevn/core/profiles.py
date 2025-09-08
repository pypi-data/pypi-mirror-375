"""
Profile management for environment variables.
Handles the storage and retrieval of environment variable profiles.
"""

import os
import sys
import json
import tempfile
import subprocess
from typing import Dict, List, Optional
from .crypto import CryptoManager

class ProfileManager:
    def __init__(self, vault_dir: str = "~/.apivault"):
        """Initialize the profile manager."""
        self.crypto = CryptoManager(vault_dir)

    def create_profile(self, profile_name: str, env_vars: Dict[str, str]) -> bool:
        """
        Create or update a profile with the given environment variables.
        
        Args:
            profile_name: Name of the profile
            env_vars: Dictionary of environment variables
            
        Returns:
            bool: True if profile was created/updated successfully
        """
        return self.crypto.encrypt_profile(profile_name, env_vars)

    def load_profile(self, profile_name: str) -> Optional[str]:
        """
        Load environment variables from a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Optional[str]: Environment variables as shell export commands
        """
        return self.crypto.decrypt_profile(profile_name)

    def set_variable(self, profile_name: str, key: str, value: str) -> bool:
        """
        Set a single environment variable in a profile.
        
        Args:
            profile_name: Name of the profile
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            bool: True if variable was set successfully
        """
        # Load existing variables
        content = self.load_profile(profile_name)
        env_vars = {}
        
        if content:
            # Parse existing variables
            for line in content.splitlines():
                if line.startswith('export '):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        var_name = parts[0].replace('export ', '').strip()
                        var_value = parts[1].strip().strip('"')
                        env_vars[var_name] = var_value
        
        # Update/add the new variable
        env_vars[key] = value
        
        # Save the updated profile
        try:
            result = self.create_profile(profile_name, env_vars)
            if not result:
                print(f"Failed to create profile {profile_name}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"Exception in create_profile: {str(e)}", file=sys.stderr)
            return False

    def delete_variable(self, profile_name: str, key: str) -> bool:
        """
        Delete an environment variable from a profile.
        
        Args:
            profile_name: Name of the profile
            key: Environment variable name to delete
            
        Returns:
            bool: True if variable was deleted successfully
        """
        content = self.load_profile(profile_name)
        if not content:
            return False
            
        env_vars = {}
        for line in content.splitlines():
            if line.startswith('export '):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].replace('export ', '').strip()
                    if var_name != key:  # Skip the variable to delete
                        var_value = parts[1].strip().strip('"')
                        env_vars[var_name] = var_value
        
        return self.create_profile(profile_name, env_vars)

    def list_profiles(self) -> List[str]:
        """
        List all available profiles.
        
        Returns:
            List[str]: List of profile names
        """
        return self.crypto.list_profiles()

    def delete_profile(self, profile_name: str) -> bool:
        """
        Delete a profile.
        
        Args:
            profile_name: Name of the profile to delete
            
        Returns:
            bool: True if profile was deleted successfully
        """
        return self.crypto.delete_profile(profile_name)

    def spawn_shell_with_profile(self, profile_name: str) -> subprocess.Popen:
        """
        Spawn a new shell with the profile's environment variables.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            subprocess.Popen: Process object for the spawned shell
        """
        content = self.load_profile(profile_name)
        if not content:
            raise ValueError(f"Profile {profile_name} not found or cannot be decrypted")
            
        # Create a temporary RC file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
            
        try:
            # Secure the temporary file
            os.chmod(temp_path, 0o600)
            
            # Spawn a new shell with the RC file
            shell = os.environ.get('SHELL', '/bin/bash')
            process = subprocess.Popen([
                shell,
                '--rcfile', temp_path
            ])
            
            return process
        finally:
            # Clean up is handled by the caller after shell exits
            pass  # Keep the temp file for the shell to use 