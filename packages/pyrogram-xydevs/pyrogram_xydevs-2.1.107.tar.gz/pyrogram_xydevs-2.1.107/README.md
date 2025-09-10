# Pyrogram XyDevs Fork

[![PyPI - Version](https://img.shields.io/pypi/v/pyrogram-xydevs)](https://pypi.org/project/pyrogram-xydevs/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyrogram-xydevs)](https://pypi.org/project/pyrogram-xydevs/)

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

This is a fork of the original [Pyrogram](https://github.com/pyrogram/pyrogram) library, maintained by XyDevs with additional features and improvements.

## Key Features

- **Ready**: Install Pyrogram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pyrogram/tgcrypto), a high-performance cryptography library written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

## Installation

### For End Users

```bash
pip install pyrogram-xydevs
```

### For Development

Follow the development setup guide below to contribute to this project.

## Quick Start

```python
from pyrogram import Client, filters

app = Client("my_account")

@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pyrogram XyDevs!")

app.run()
```

## Development Setup

This section is for contributors who want to modify the source code and contribute to the project.

### Prerequisites

- Python 3.8 or higher
- Git
- A [Telegram API key](https://docs.pyrogram.org/intro/setup#api-keys) (for testing)

### 1. Clone the Repository

```bash
git clone https://github.com/xydevs/pyrogram-fork.git
cd pyrogram-fork
```

### 2. Set Up Virtual Environment

#### On Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Verify activation (should show venv path)
echo $env:VIRTUAL_ENV
```

#### On Linux/macOS:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation
echo $VIRTUAL_ENV
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install build tools
pip install build twine

# Install the package in development mode
pip install -e .

# Install additional dependencies
pip install PySocks
```

### 4. Verify Installation

Create a test file to verify everything works:

```python
# test.py
import pyrogram
print("Pyrogram location:", pyrogram.__file__)
print("Import successful!")
```

Run the test:
```bash
python test.py
```

You should see output pointing to your local development directory.

### 5. Making Changes

#### Project Structure
```
pyrogram-fork/
├── main/pyrogram/          # Main source code
│   ├── __init__.py
│   ├── client.py
│   ├── types/
│   ├── methods/
│   ├── handlers/
│   └── ...
├── pyproject.toml          # Package configuration
├── README.md
└── test.py
```

#### Code Editing
1. Make your changes in the `main/pyrogram/` directory
2. Test your changes:
   ```bash
   python test.py
   # or run your own test scripts
   ```

### 6. Building and Publishing

#### Step 1: Update Version
Edit `pyproject.toml` and increment the version number:

```toml
[project]
name = "pyrogram-xydevs"
version = "2.1.107"  # Increment this number
description = "Fork of Pyrogram maintained by xydevs"
# ... rest of config
```

#### Step 2: Clean Previous Builds
```bash
# Remove old build files
Remove-Item -Recurse -Force dist/     # Windows PowerShell
# rm -rf dist/                        # Linux/macOS
```

#### Step 3: Build Package
```bash
python -m build
```

This creates:
- `dist/pyrogram_xydevs-x.x.x-py3-none-any.whl`
- `dist/pyrogram_xydevs-x.x.x.tar.gz`

#### Step 4: Validate Package
```bash
python -m twine check dist/*
```

Should output: `PASSED` for all files.

#### Step 5: Upload to PyPI

**⚠️ Important**: Always test on TestPyPI first!

##### Test Upload (TestPyPI):
```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pyrogram-xydevs
```

##### Production Upload (PyPI):
```bash
# Upload to PyPI (only after TestPyPI works)
python -m twine upload dist/*
```

### 7. PyPI Credentials Setup

#### Method 1: API Tokens (Recommended)
1. Create accounts on:
   - https://pypi.org/account/register/
   - https://test.pypi.org/account/register/

2. Generate API tokens in account settings

3. Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your_real_api_token_here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your_test_api_token_here
```

#### Method 2: Environment Variables
```bash
# Set environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your_api_token_here
```

### 8. Release Workflow

1. **Make changes** in `main/pyrogram/`
2. **Test locally**: `python test.py`
3. **Update version** in `pyproject.toml`
4. **Build package**: `python -m build`
5. **Validate**: `python -m twine check dist/*`
6. **Test upload**: `python -m twine upload --repository testpypi dist/*`
7. **Test install**: `pip install --index-url https://test.pypi.org/simple/ pyrogram-xydevs`
8. **Production upload**: `python -m twine upload dist/*`
9. **Tag release**: `git tag v2.1.x && git push --tags`

### 9. Common Commands Reference

```bash
# Development workflow
& "venv\Scripts\Activate.ps1"           # Activate venv (Windows)
source venv/bin/activate                # Activate venv (Linux/macOS)
python test.py                          # Test changes
python -m build                         # Build package
python -m twine check dist/*            # Validate package
python -m twine upload --repository testpypi dist/*  # Test upload
python -m twine upload dist/*           # Production upload

# Package management
pip install -e .                        # Install in development mode
pip list                                # List installed packages
pip uninstall pyrogram-xydevs          # Uninstall package
```

### 10. Troubleshooting

#### Virtual Environment Issues
```bash
# If venv activation fails
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser  # Windows

# If wrong Python version
python --version
which python  # Should point to venv
```

#### Import Issues
```bash
# Reinstall in development mode
pip uninstall pyrogram-xydevs
pip install -e .
```

#### Upload Issues
```bash
# Version already exists error
# Solution: Increment version in pyproject.toml

# Authentication error
# Solution: Check API tokens and .pypirc file
```

## Requirements

- Python 3.8 or higher.
- A [Telegram API key](https://docs.pyrogram.org/intro/setup#api-keys).

## Resources

- Check out the docs at https://docs.pyrogram.org to learn more about Pyrogram, get started right away and discover more in-depth material for building your client applications.
- Join the official channel at https://t.me/pyrogram and stay tuned for news, updates and announcements.

## Changes from Original Pyrogram

This fork includes additional features and improvements maintained by XyDevs team. For detailed changelog, please check our releases.

## Contributing

We welcome contributions! Please follow the development setup guide above to get started.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the terms of the [GNU Lesser General Public License v3 or later (LGPLv3+)](COPYING.lesser).
