#!/usr/bin/env python3
"""
Main entry point for the sevn CLI.
"""

import sys
from .commands import CommandHandler, create_parser

def main():
    """Main entry point for sevn."""
    parser = create_parser()
    args = parser.parse_args()
    
    handler = CommandHandler()
    
    # Map commands to handler methods
    command_map = {
        'unlock': handler.unlock,
        'sign': handler.sign,
        'lock': handler.lock,
        'list': handler.list,
        'purge': handler.purge,
        'init': handler.init
    }
    
    # Execute the command
    try:
        return command_map[args.command](args)
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 