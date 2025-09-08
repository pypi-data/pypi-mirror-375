"""
CLI commands implementation for sevn - the secure environment variable manager.
"""

import os
import sys
import argparse
import signal
import tempfile
import subprocess
from typing import List, Optional
from ..core.profiles import ProfileManager
import random

SEVEN_SINS = [
    "PRIDE='I am the best developer'",
    "GREED='Give me all the API keys'",
    "LUST='I love writing code'",
    "ENVY='Why does their .env have more secrets?'",
    "GLUTTONY='I need more environment variables'",
    "WRATH='Who committed the .env file?!'",
    "SLOTH='I’ll rotate these keys later...'"
]

EXAMPLES = """
Examples:
  # Lock (encrypt) a secret in a profile
  sevn lock STRIPE_KEY=sk_test_123 --profile myproject
  
  # List all profiles
  sevn list
  
  # Unlock (load) secrets into current shell
  eval "$(sevn unlock myproject)"
  
  # Sign into a new shell with loaded secrets
  sevn sign myproject
  
  # Remove a secret from a profile
  sevn purge myproject --key STRIPE_KEY
  
  # Remove an entire profile
  sevn purge myproject

Shell Integration:
  For easier usage, add this function to your .bashrc or .zshrc:
  
  load_secrets() {
      eval "$(sevn unlock ${1:-default})"
  }
  
  Then you can simply use: load_secrets myproject

The Seven Principles:
  🔒 Secure   – secrets stay local and encrypted
  🎯 Simple   – install and go, no setup hell
  🎭 Scoped   – use profiles, isolate secrets
  🔧 Script   – CLI-first, shell-native
  📦 Share    – encrypted blob = portable
  ⚡ Speed    – decrypt only what you need
  🌐 State    – no server, no risk surface
"""

class CommandHandler:
    def __init__(self):
        self.profile_manager = ProfileManager()

    def unlock(self, args: argparse.Namespace) -> int:
        """
        Unlock (decrypt) environment variables from a profile.
        Prints export commands to stdout for eval.
        """
        profile_name = args.profile
        
        # Get the decrypted content
        content = self.profile_manager.load_profile(profile_name)
        if content is None:
            print(f"Error: Profile '{profile_name}' not found or cannot be decrypted",
                  file=sys.stderr)
            return 1
        
        # Print directly to stdout for eval
        print(content.rstrip())  # Remove trailing newlines
        return 0

    def sign(self, args: argparse.Namespace) -> int:
        """
        Sign into a new shell with the profile's environment variables.
        """
        profile_name = args.profile
        
        # Get the decrypted content
        content = self.profile_manager.load_profile(profile_name)
        if content is None:
            print(f"Error: Profile '{profile_name}' not found or cannot be decrypted",
                  file=sys.stderr)
            return 1
        
        # Create a secure temporary file for the shell
        with tempfile.NamedTemporaryFile(mode='w', prefix='sevn_', suffix='.sh', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)
        
        try:
            # Secure the temporary file
            os.chmod(temp_path, 0o600)
            
            # Spawn a new shell with the profile
            shell = os.environ.get('SHELL', '/bin/bash')
            process = subprocess.Popen([
                shell,
                '--rcfile', temp_path
            ])
            
            # Handle Ctrl+C gracefully
            def signal_handler(sig, frame):
                process.terminate()
                sys.exit(0)
                
            signal.signal(signal.SIGINT, signal_handler)
            
            # Wait for the shell to exit
            process.wait()
            return process.returncode
        finally:
            # Always clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def lock(self, args: argparse.Namespace) -> int:
        """Lock (encrypt) an environment variable in a profile."""
        profile_name = args.profile
        key, value = args.key_value.split('=', 1)
        
        try:
            if self.profile_manager.set_variable(profile_name, key, value):
                print(f"🔒 Secret locked in profile \"{profile_name}\"")
                return 0
            else:
                print(f"Error: Failed to lock secret in profile '{profile_name}'",
                      file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1

    def list(self, args: argparse.Namespace) -> int:
        """List all available profiles."""
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            print("No profiles found.")
            return 0
            
        print("Available profiles:")
        for profile in profiles:
            print(f"  🔐 {profile}")
        return 0

    def purge(self, args: argparse.Namespace) -> int:
        """Purge a profile or a variable from a profile."""
        profile_name = args.profile
        
        if args.key:
            # Delete a specific variable
            if self.profile_manager.delete_variable(profile_name, args.key):
                print(f"🗑️  Secret '{args.key}' purged from profile \"{profile_name}\"")
                return 0
            else:
                print(f"Error: Failed to purge secret from profile '{profile_name}'",
                      file=sys.stderr)
                return 1
        else:
            # Delete entire profile
            if self.profile_manager.delete_profile(profile_name):
                print(f"🗑️  Profile \"{profile_name}\" purged")
                return 0
            else:
                print(f"Error: Failed to purge profile '{profile_name}'",
                      file=sys.stderr)
                return 1

    def init(self, args: argparse.Namespace) -> int:
        """Initialize a new profile."""
        if args.sin:
            print("🔥 Initializing with the seven deadly sins...")
            env_content = "\n".join(SEVEN_SINS)
            print(env_content)
            if args.write:
                with open(".env", "w") as f:
                    f.write(env_content + "\n")
                print("😈 .env created with deadly sins")
            return 0
            
        # Normal initialization logic here
        return 0

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="sevn - Secure environment variable manager built on 7 principles",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Lock command
    lock_parser = subparsers.add_parser('lock', help='Lock (encrypt) a secret in a profile')
    lock_parser.add_argument('key_value', help='Key-value pair in the format KEY=VALUE')
    lock_parser.add_argument('--profile', '-p', default='default', help='Profile name (default: default)')
    
    # Unlock command
    unlock_parser = subparsers.add_parser('unlock', help='Unlock (decrypt) secrets from a profile')
    unlock_parser.add_argument('profile', help='Profile name')
    
    # Sign command
    sign_parser = subparsers.add_parser('sign', help='Sign into a new shell with loaded secrets')
    sign_parser.add_argument('profile', help='Profile name')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all available profiles')
    
    # Purge command
    purge_parser = subparsers.add_parser('purge', help='Remove secrets or profiles')
    purge_parser.add_argument('profile', help='Profile name')
    purge_parser.add_argument('--key', '-k', help='Specific secret key to remove')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new profile')
    init_parser.add_argument('--sin', action='store_true', help='Initialize with the seven deadly sins')
    init_parser.add_argument('--write', action='store_true', help='Write sins to .env file')
    
    return parser 