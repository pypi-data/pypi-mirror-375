# sevn 🔐

A secure environment variable manager built on 7 core principles.

## The Seven Principles

- 🔒 **Secure** – secrets stay local and encrypted
- 🎯 **Simple** – install and go, no setup hell
- 🎭 **Scoped** – use profiles, isolate secrets
- 🔧 **Script** – CLI-first, shell-native
- 📦 **Share** – encrypted blob = portable
- ⚡ **Speed** – decrypt only what you need
- 🌐 **State** – no server, no risk surface

## Installation

### From PyPI (Recommended)
```bash
pip install sevn
sevn --help
```

### From GitHub Release
```bash
# Download from: https://github.com/thoerner/sevn/releases
pip install sevn-1.0.2-py3-none-any.whl
sevn --help
```

### From Source
```bash
git clone https://github.com/thoerner/sevn.git
cd sevn
chmod +x sevn
./sevn --help
```

### Development Installation
```bash
git clone https://github.com/thoerner/sevn.git
cd sevn
python3 -m pip install .
sevn --help
```

Requires Python 3.9 or higher and GPG.

## Quick Start

1. Lock a secret in a profile:
```bash
./sevn lock STRIPE_KEY=sk_test_123 --profile myproject
```

2. List all profiles:
```bash
./sevn list
```

3. Load secrets into your current shell:
```bash
eval "$(./sevn unlock myproject)"
```

4. Or sign into a new shell with loaded secrets:
```bash
./sevn sign myproject
```

## Commands

### `lock` - Encrypt a secret
```bash
./sevn lock KEY=VALUE --profile PROFILE_NAME
```

### `unlock` - Decrypt and load secrets
```bash
eval "$(./sevn unlock PROFILE_NAME)"
```

### `sign` - Start a new shell with secrets
```bash
./sevn sign PROFILE_NAME
```

### `list` - Show all profiles
```bash
./sevn list
```

### `purge` - Remove secrets or profiles
```bash
# Remove a specific secret
./sevn purge PROFILE_NAME --key SECRET_KEY

# Remove entire profile
./sevn purge PROFILE_NAME
```

### `init` - Initialize new profile
```bash
# Normal initialization
./sevn init

# Fun mode: Initialize with the seven deadly sins
./sevn init --sin
./sevn init --sin --write  # Creates .env file
```

## Shell Integration

Add this to your `.bashrc` or `.zshrc` for easier usage:

```bash
load_secrets() {
    eval "$(./sevn unlock ${1:-default})"
}
```

Then you can simply use:
```bash
load_secrets myproject
```

## Security

- All secrets are encrypted locally using strong cryptography
- No external servers or cloud storage
- Each profile is isolated and separately encrypted
- Temporary files are securely cleaned up
- Secrets never touch disk in plaintext

## Requirements

- Python >=3.9
- cryptography >=41.0.0
- pyyaml >=6.0.1
- python-dotenv >=1.0.0

## License

MIT License