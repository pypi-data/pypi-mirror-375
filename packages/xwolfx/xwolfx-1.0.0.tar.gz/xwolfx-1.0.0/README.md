# xwolfx

An unofficial Python API for WOLF (AKA Palringo) - Python port of wolf.js

## Installation

```bash
pip install xwolfx
```

## Quick Start

```python
from xwolfx import WOLF

client = WOLF()

@client.on('ready')
def on_ready():
    print('Bot is ready!')

@client.on('channel_message')
def on_channel_message(message):
    if message.body == '!ping':
        message.reply('Pong!')

client.login()
```

## Features

- Connect to WOLF chat platform
- Send and receive messages
- Command handling system
- Event-driven architecture
- Multi-language support
- Channel and private messaging

## License

MIT License - Python port of the original wolf.js library