# xwolfx

An unofficial Python API for WOLF (AKA Palringo) - Python port of wolf.js

[![PyPI version](https://badge.fury.io/py/xwolfx.svg)](https://badge.fury.io/py/xwolfx)
[![Python Version](https://img.shields.io/pypi/pyversions/xwolfx.svg)](https://pypi.org/project/xwolfx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## التثبيت | Installation

```bash
pip install xwolfx
```

## الاستخدام السريع | Quick Start

### مثال بسيط | Basic Example

```python
import asyncio
from xwolfx import WOLF

async def main():
    client = WOLF()
    
    @client.on('ready')
    def on_ready():
        print('🤖 Bot is ready!')
    
    @client.on('channel_message')
    async def on_channel_message(message):
        if message.body == '!ping':
            await message.reply('Pong!')
        elif message.body == '!hello':
            await message.reply('مرحباً! Hello from xwolfx Python bot!')
    
    @client.on('private_message')
    async def on_private_message(message):
        await message.reply('Thanks for the private message!')
    
    # تسجيل الدخول | Login
    await client.login('your_email@example.com', 'your_password')
    
    # إبقاء البوت يعمل | Keep bot running
    await asyncio.sleep(3600)  # Run for 1 hour

if __name__ == "__main__":
    asyncio.run(main())
```

### نظام الأوامر | Command System

```python
from xwolfx import WOLF, Command

client = WOLF()

# إنشاء أوامر مخصصة | Create custom commands
def help_command(context):
    help_text = """
    🤖 Available Commands:
    !help - Show this help message
    !ping - Test command
    !info - Bot information
    """
    return context.reply(help_text)

def info_command(context):
    return context.reply("🐍 Python WOLF Bot using xwolfx library!")

# تسجيل الأوامر | Register commands
client.command_handler.register([
    Command('bot_command_help', {'both': help_command}),
    Command('bot_command_info', {'both': info_command})
])
```

### إعدادات متقدمة | Advanced Configuration

```python
from xwolfx import WOLF
from xwolfx.constants import OnlineState, LoginType

client = WOLF()

# تخصيص الإعدادات | Custom configuration
client.config['keyword'] = 'mybot'
client.config['framework']['login']['onlineState'] = OnlineState.ONLINE

# تسجيل دخول متقدم | Advanced login
await client.login(
    email='bot@example.com',
    password='secure_password',
    online_state=OnlineState.ONLINE,
    login_type=LoginType.EMAIL
)
```

## المميزات | Features

- 🔌 اتصال بمنصة WOLF للدردشة | Connect to WOLF chat platform
- 💬 إرسال واستقبال الرسائل | Send and receive messages  
- 🎮 نظام معالجة الأوامر | Command handling system
- 📡 معمارية قائمة على الأحداث | Event-driven architecture
- 🌍 دعم متعدد اللغات | Multi-language support
- 👥 رسائل القنوات والخاصة | Channel and private messaging
- 🔧 سهل الاستخدام والتخصيص | Easy to use and customize

## الثوابت المتاحة | Available Constants

### حالات الاتصال | Online States
```python
from xwolfx.constants import OnlineState

OnlineState.OFFLINE    # غير متصل | Offline
OnlineState.ONLINE     # متصل | Online  
OnlineState.AWAY       # بعيد | Away
OnlineState.BUSY       # مشغول | Busy
OnlineState.INVISIBLE  # مخفي | Invisible
```

### أنواع تسجيل الدخول | Login Types
```python
from xwolfx.constants import LoginType

LoginType.EMAIL     # البريد الإلكتروني | Email
LoginType.GOOGLE    # جوجل | Google
LoginType.FACEBOOK  # فيسبوك | Facebook
LoginType.APPLE     # أبل | Apple
```

## أمثلة متقدمة | Advanced Examples

### بوت ذكي للردود التلقائية | Smart Auto-Reply Bot

```python
import asyncio
from xwolfx import WOLF

async def smart_bot():
    client = WOLF()
    
    # قاموس الردود الذكية | Smart replies dictionary
    responses = {
        'hello': 'مرحباً! كيف يمكنني مساعدتك؟',
        'help': 'أنا بوت Python مصنوع بـ xwolfx!',
        'time': lambda: f'الوقت الحالي: {datetime.now()}',
        'ping': 'Pong! 🏓'
    }
    
    @client.on('channel_message')
    async def smart_reply(message):
        text = message.body.lower()
        for keyword, response in responses.items():
            if keyword in text:
                reply = response() if callable(response) else response
                await message.reply(reply)
                break
    
    await client.login()

asyncio.run(smart_bot())
```

## اختبار المكتبة | Testing the Library

```bash
cd xwolfx
python test_xwolfx.py
```

## المساهمة | Contributing

نرحب بالمساهمات! يرجى إنشاء Pull Request أو Issue على GitHub.

## الرخصة | License

MIT License - منقول من مكتبة wolf.js الأصلية

## روابط مفيدة | Useful Links

- 📦 [PyPI Package](https://pypi.org/project/xwolfx/)
- 🐺 [Original wolf.js](https://github.com/dawalters1/wolf.js)
- 📚 [WOLF Platform](https://wolf.live/)

## الدعم | Support

للحصول على الدعم، يرجى إنشاء Issue على GitHub أو الانضمام إلى مجتمع WOLF.