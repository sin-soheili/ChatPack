<p align="center">
  <img src="./assets/banner.jpg" alt="ChatPack Banner" width="100%" style="border-radius: 10px;" />
</p>

##

<table align="center" style="border-width: 0px; border-style: none; border-collapse: collapse;">
  <tr>
    <td align="center" valign="middle" style="border: none; padding: 20px;">
      <img src="./assets/logo.png" width="140" alt="ChatPack Logo" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);"/>
    </td>
    <td align="left" valign="middle" style="border: none; padding: 20px;">
      <h1 style="margin: 0 0 5px 0; border-bottom: none; font-size: 2.5em;">ChatPack 📦</h1>
      <p style="margin: 0 0 10px 0; font-size: 1.1em; color: #586069;">
        <b>An advanced, production-ready, asynchronous UI component toolkit built on top of Pyrogram.</b>
      </p>
      <p style="margin: 0 0 15px 0; font-style: italic; color: #6a737d;">
        Transforms linear, event-driven Telegram bot development into an elegant, sequential, and stateful dialog runtime.
      </p>
      <div style="margin-top: 10px;">
        <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
        <img src="https://img.shields.io/badge/Framework-Pyrogram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Pyrogram Framework" />
        <img src="https://img.shields.io/pypi/v/chatpack?style=for-the-badge&color=blue" alt="PyPI Version" />
      </div>
    </td>
  </tr>
</table>

<p align="center" style="margin-top: 15px;">
  <a href="https://t.me/backpack_dev">
    <img src="https://img.shields.io/badge/Telegram-Channel-26A5E4?style=flat-square&logo=telegram&logoColor=white" alt="Telegram Channel">
  </a>
  &nbsp;
  <a href="https://t.me/thenewbiebackpack">
    <img src="https://img.shields.io/badge/Telegram-Developer-26A5E4?style=flat-square&logo=telegram&logoColor=white" alt="Telegram Developer">
  </a>
</p>
---

## 🛠 Why ChatPack?

Stop wrestling with complex global state machines, messy database tables, or chaotic callback query routing when building multi-step forms, star ratings, nested menus, or channel verification gates. 


```

┌────────────────────────────────────────────────────────┐
│               THE OLD WAY (CALLBACK CHAOS)             │
│ State (DB) ──> Handler ──> Edit UI ──> Next State (DB) │
└───────────────────────────┬────────────────────────────┘
                  Transform │ with ChatPack
                            ▼ 
┌────────────────────────────────────────────────────────┐
│               THE CHATPACK WAY (NATIVE)                │
│       data = await Form([Step1, Step2]).run()          │
└────────────────────────────────────────────────────────┘

```

### ✨ Key Features

* **⚡ Sequential Execution Runtime:** Write complex multi-step interactive flows using clean, native `await` syntax without manually tracking user state histories.
* **💡 Dual Invocation APIs:** Use standard Form-level tracking via `ask()` or pull pure scalar values directly using the modern standalone `ask_value()` method.
* **🧩 Rich Interactive UI Suite:** Out-of-the-box components for text fields, choice menus, channel subscription walls, star ratings, nested menus, and confirmation dialogs.
* **🧹 Automated UI Cleanup:** Optional engine routines to automatically flush intermediate prompt and response messages upon completion, keeping the user's chat history immaculate.
* **⚙️ Zero Configuration Boilerplate:** 100% granular control over localization, layouts, button labels, emojis, and custom input validation.

---

## 🚀 Installation

Install the stable release directly from **PyPI**:

```bash
pip install chatpack-ui

```

> ⚠️ **Note:** Requires Python 3.8+ and an active Pyrogram environment.

---

## 💡 Architecture: `ask()` vs `ask_value()`

Every interactive component within ChatPack extends the `BaseField` core class and provides two flexible invocation patterns designed for distinct execution flows:

### 1. `await component.ask(client, chat_id)`

* **Returns:** A Python tuple containing `(validated_value, tracked_message_ids)`.
* **Best For:** Inside the sequential `Form` context where tracking message IDs is required for automatic bulk UI wiping and history cleanup routines.

### 2. `await component.ask_value(client, chat_id)`

* **Returns:** The raw, extracted scalar data type directly (`bool`, `int`, `str`, etc.).
* **Best For:** Isolated, one-off standalone actions anywhere in your existing Pyrogram command handlers (e.g., verifying membership or checking a deletion prompt) without unpacking tuple wrappers manually.

---

## ⚡ Quick Start

Here is how easily you can implement a sequential multi-step profile survey with built-in environment configurations and automated UI cleanup:

```python
import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from chatpack import Form, TextInput, SelectMenu
from chatpack.utils.listener import listener_manager

load_dotenv()

app = Client(
    "chatpack_production_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN"),
)


@app.on_message(filters.private, group=-1)
async def chatpack_message_interceptor(client: Client, message: Message):
    if message.text == "/cancel":
        future = listener_manager._listeners.get(message.chat.id)
        if future and not future.done():
            future.set_result(message)
            message.stop_propagation()
            return
    if listener_manager.resolve(message.chat.id, message):
        message.stop_propagation()


@app.on_callback_query(group=-1)
async def chatpack_callback_interceptor(
    client: Client, callback_query: CallbackQuery
):
    if listener_manager.resolve(callback_query.message.chat.id, callback_query):
        await callback_query.answer()
        callback_query.stop_propagation()


@app.on_message(filters.command("survey") & filters.private)
async def survey_handler(client: Client, message: Message):
    form = Form(
        [
            TextInput(key="name", prompt="What is your name?"),
            SelectMenu(
                key="gender",
                prompt="Please select your gender:",
                options={"male": "🙋‍♂️ Male", "female": "🙋‍♀️ Female"},
            ),
        ],
        timeout_per_field=60,
        cleanup=True,
    )

    data = await form.run(client, message.chat.id)

    if data:
        await message.reply(
            f"✅ Thank you! Your profile has been updated, {data['name']}."
        )


if __name__ == "__main__":
    app.run()

```

---

## 🧩 Built-in Core Components

### 1. Action Confirmation (`ConfirmDialog`)

Perfect for verifying high-risk actions (like deleting accounts or flushing data) using native boolean checks via `ask_value()`:

```python
from chatpack.components.confirm import ConfirmDialog

dialog = ConfirmDialog("Are you sure you want to permanently delete your data?")
confirmed = await dialog.ask_value(client, message.chat.id, timeout=30)

if confirmed:
    await message.reply("Data successfully wiped.")

```

### 2. Mandatory Membership Gate (`JoinChecker`)

Restrict bot access until the user joins specific sponsor channels. Features dynamic API validation and customizable popup alerts:

```python
from chatpack import JoinChecker

checker = JoinChecker(
    key="force_join",
    prompt="🔒 **Access Restricted**\n\nPlease join our channel to unlock features:",
    channels=["@backpack_dev"],
    mode="all",
    button_text="Verify Membership 🔄",
    not_joined_alert="🛑 Verification failed! Please join the channel first.",
)
is_allowed = await checker.ask_value(client, message.chat.id, timeout=180)

```

### 3. Interactive Star Ratings (`RatingStars`)

Collect customer satisfaction scores or performance metrics directly on a single message layout with live UI state updates:

```python
from chatpack import RatingStars

rating = RatingStars(
    key="feedback",
    prompt="⭐️ **Rate Our Service**\n\nHow would you rate your experience?",
    max_stars=5,
    submit_button_text="Submit Rating 📤",
    success_message_format="✨ **Recorded!** Thanks for rating us {stars} Stars",
)
score = await rating.ask_value(client, message.chat.id, timeout=60)

```

### 4. Dynamic Nested Menus (`NestedMenu`)

Build deep, multi-tiered interactive navigation catalogs inside a single message using simple python nested dictionaries:

```python
from chatpack import NestedMenu

catalog = {
    "💻 Development": {
        "🐍 Python": {"FastAPI": "f_api", "Django": "dj_web"}
    },
    "🐧 DevOps": "linux_core"
}

menu = NestedMenu(
    key="catalog",
    prompt="📂 **Explore Catalog**\n\nSelect a path:",
    menu_data=catalog,
)
selected_node = await menu.ask_value(client, message.chat.id)

```

### 5. Media & Content Broadcast (`BroadcastSender`)

An administrative engine that safely intercepts any update message type (text, photos, video logs, files) and replicates it across a list of target users sequentially:

```python
from chatpack import BroadcastSender

sender = BroadcastSender(
    user_ids=[12345678, 87654321],
    prompt="🚀 Forward or send the message you want to broadcast to everyone:",
)
stats = await sender.ask_value(client, message.chat.id, timeout=300)

```

### 6. Anti-Flood Bulk Writer (`ChunkSender`)

Transmit massive telemetry outputs, server metrics, or text structures exceeding Telegram's 4,096-character limit safely without breaking line words:

```python
from chatpack import ChunkSender

await ChunkSender.send(
    client=client,
    chat_id=message.chat.id,
    text="Your huge application log context data...",
    max_chars=4000,
    delay=0.2,
)

```

---

## 👥 Support & Community

For queries, feature requests, or custom engineering integrations, connect via official channels:

```
┌───────────────────────────┬──────────────────────────────────────┐
│ TYPE                      │ LOCATION                             │
├───────────────────────────┼──────────────────────────────────────┤
│ 📢 Telegram Channel       │ https://t.me/backpack_dev            │
│ 👨‍💻 Personal Developer     │ https://t.me/thenewbiebackpack       │
└───────────────────────────┴──────────────────────────────────────┘

```

---

## ⚖️ License

Distributed under the **MIT License**. Feel free to use, modify, and build scalable automation ecosystems with it.

