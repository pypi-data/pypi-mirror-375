# Password Generator

A simple Python package for generating secure random passwords.

## Installation

```bash
pip install password-generator
```

## Usage

```python
from password_generator import generate_password

password = generate_password(length=16, use_uppercase=True, use_digits=True, use_special=True)
print(password)  # Example: 'A1b2C3d4E5f6G7h8!'
```

## Parameters

- `length` (int): Length of the password (default: 12)
- `use_uppercase` (bool): Include uppercase letters (default: True)
- `use_digits` (bool): Include digits (default: True)
- `use_special` (bool): Include special characters (default: True)

## License

MIT License
