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

## Installing

``` bash
pip install pyrogram-xydevs
```

## Quick Start

```python
from pyrogram import Client, filters

app = Client("my_account")

@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pyrogram XyDevs!")

app.run()
```

**Pyrogram** is a modern, elegant and asynchronous MTProto API framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot identity (bot API alternative) using Python.

## Requirements

- Python 3.8 or higher.
- A [Telegram API key](https://docs.pyrogram.org/intro/setup#api-keys).

## Resources

- Check out the docs at https://docs.pyrogram.org to learn more about Pyrogram, get started right away and discover more in-depth material for building your client applications.
- Join the official channel at https://t.me/pyrogram and stay tuned for news, updates and announcements.

## Changes from Original Pyrogram

This fork includes additional features and improvements maintained by XyDevs team. For detailed changelog, please check our releases.

## License

This project is licensed under the terms of the [GNU Lesser General Public License v3 or later (LGPLv3+)](COPYING.lesser).
