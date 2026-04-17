# envchain-cli

A CLI tool to manage and encrypt project-level environment variables with git-friendly storage.

## Installation

```bash
pip install envchain-cli
```

## Usage

Initialize envchain in your project directory:

```bash
envchain init
```

Add and encrypt an environment variable:

```bash
envchain set API_KEY "your-secret-value"
```

Load variables into your shell session:

```bash
eval $(envchain load)
```

List all tracked variables (keys only, values stay encrypted):

```bash
envchain list
```

Run a command with your decrypted environment variables injected:

```bash
envchain run -- python app.py
```

Encrypted values are stored in `.envchain.enc` and a `.envchain.keys` manifest is committed to version control — keeping secrets out of your repo while making key names visible to your team.

## Configuration

| File | Purpose | Commit to git? |
|------|---------|----------------|
| `.envchain.enc` | Encrypted secrets | ✅ Yes |
| `.envchain.keys` | Key names manifest | ✅ Yes |
| `.envchain.secret` | Master key | ❌ No (add to `.gitignore`) |

## Requirements

- Python 3.8+
- [cryptography](https://pypi.org/project/cryptography/) >= 38.0

## License

This project is licensed under the [MIT License](LICENSE).