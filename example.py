import os
import re
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from chatpack import (
    Form,
    TextInput,
    SelectMenu,
    BroadcastSender,
    JoinChecker,
    RatingStars,
    NestedMenu,
    ChunkSender,
)
from chatpack.utils.listener import listener_manager
from chatpack.components.confirm import ConfirmDialog

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "chatpack_production_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
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
    chat_id = callback_query.message.chat.id
    if listener_manager.resolve(chat_id, callback_query):
        await callback_query.answer()
        callback_query.stop_propagation()


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    guide_text = (
        "🤖 **Welcome to ChatPack Framework Demo Bot!**\n\n"
        "Here is the available list of interactive components:\n"
        "📝 /survey - Multi-step stateful interactive form\n"
        "❌ /delete_account - Standalone binary confirmation dialog\n"
        "🔒 /lock - Channel membership verification gate\n"
        "⭐️ /rate - Live interactive star rating dashboard\n"
        "📂 /menu - Multi-level tree navigation nested menu\n"
        "🚀 /broadcast - Admin tool to safely broadcast any media type\n"
        "📝 /logs - Chunk sender utility for massive raw log text data\n\n"
        "💡 You can send `/cancel` at any point during any active flow."
    )
    await message.reply(guide_text)


@app.on_message(filters.command("survey") & filters.private)
async def survey_handler(client: Client, message: Message):
    form = Form(
        [
            TextInput(key="name", prompt="What is your name?"),
            SelectMenu(
                key="gender",
                prompt="Please select your gender:",
                options={
                    "male": "🙋‍♂️ Male",
                    "female": "🙋‍♀️ Female",
                    "other": "Prefer not to say",
                },
            ),
            SelectMenu(
                key="os",
                prompt="What is your favorite operating system?",
                options=["Ubuntu/Linux", "macOS", "Windows"],
            ),
        ],
        timeout_per_field=60,
        cleanup=True,
    )

    data = await form.run(client, message.chat.id)

    if data is None:
        await client.send_message(
            message.chat.id, "❌ Survey cancelled or timed out."
        )
        return

    summary = (
        "📊 **Survey Results:**\n\n"
        f"👤 Name: {data['name']}\n"
        f"⚥ Gender: {data['gender']}\n"
        f"💻 OS: {data['os']}"
    )
    await client.send_message(message.chat.id, summary)


@app.on_message(filters.command("delete_account") & filters.private)
async def delete_handler(client: Client, message: Message):
    dialog = ConfirmDialog(
        "Are you absolutely sure you want to delete your account?"
    )
    confirmed = await dialog.ask_value(client, message.chat.id, timeout=30)

    if confirmed:
        await message.reply("Your account has been deleted.")
    else:
        await message.reply("Action cancelled.")


@app.on_message(filters.command("lock") & filters.private)
async def lock_handler(client: Client, message: Message):
    checker = JoinChecker(
        key="force_join",
        prompt="🔒 **Access Restricted**\n\nTo unlock the premium features of this bot, you must first join our channels:",
        channels=["@backpack_dev"],
        mode="all",
        button_text="Verify Membership 🔄",
        channel_button_format="Join Channel {i} 📢",
        success_message_format="{prompt}\n\n✅ Membership verified successfully! Access granted.",
        not_joined_alert="🛑 Verification failed! Please join all listed channels first and click verify again.",
        timeout_message="⏱ Session expired. Please try unlocking again using /lock.",
    )

    is_allowed = await checker.ask_value(client, message.chat.id, timeout=180)

    if is_allowed:
        await client.send_message(
            message.chat.id,
            "🎉 Welcome back! All premium features have been completely unlocked for you.",
        )


@app.on_message(filters.command("rate") & filters.private)
async def rate_handler(client: Client, message: Message):
    rating_component = RatingStars(
        key="support_rating",
        prompt="⭐️ **Support Quality Survey**\n\nPlease tap the stars below to rate your interaction experience with our support team:",
        max_stars=5,
        submit_button_text="Submit Rating 📤",
        success_message_format="✨ **Rating Submitted!**\n\nThank you for your valuable feedback. You gave: {stars} Stars",
        timeout_message="⏱ Rating session timed out due to inactivity.",
    )

    stars_given = await rating_component.ask_value(
        client, message.chat.id, timeout=60
    )

    if stars_given is not None:
        print(f"User submitted rating: {stars_given} stars.")


@app.on_message(filters.command("menu") & filters.private)
async def menu_handler(client: Client, message: Message):
    course_catalog = {
        "💻 Software Engineering": {
            "🐍 Python Stack": {
                "FastAPI (Backend)": "course_fastapi",
                "Django (Fullstack)": "course_django",
                "Pyrogram (Automation)": "course_pyrogram",
            },
            "🌐 Frontend Web": {"React": "course_react", "Vue.js": "course_vue"},
        },
        "🔒 Cybersecurity": {
            "Offensive Security (Red Teaming)": "course_redteam",
            "Web Security (OWASP)": "course_owasp",
        },
        "🐧 Linux & DevOps": "course_linux",
    }

    menu_component = NestedMenu(
        key="catalog_selection",
        prompt="📂 **Course Catalog Hub**\n\nExplore our structured learning tracks using the tree navigation buttons below:",
        menu_data=course_catalog,
        back_button_text="🔙 Back",
        main_menu_button_text="🏠 Main Menu",
        success_message_format="📥 **Selection Confirmed!**\n\nYou have successfully locked in your seat for: *{selection}*",
    )

    selected_course_id, _ = await menu_component.ask(
        client, message.chat.id, timeout=120
    )

    if selected_course_id:
        print(f"User locked database course ID target: {selected_course_id}")


@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client: Client, message: Message):
    target_users = [message.chat.id]

    sender = BroadcastSender(
        user_ids=target_users,
        prompt="🚀 **Admin Panel: Broadcast Distribution**\n\nSend or forward the exact payload item (text message, media asset, file document) you want to replicate to all users:",
    )

    stats, _ = await sender.ask(client, message.chat.id, timeout=300)

    if stats:
        print(f"Broadcast transaction finalized. Report: {stats}")


@app.on_message(filters.command("logs") & filters.private)
async def logs_handler(client: Client, message: Message):
    very_long_text = "📝 Raw transaction log record file line...\n" * 300

    await message.reply_text(
        "⏳ Compiling and dispatching structural logs in secure byte chunks..."
    )

    await ChunkSender.send(
        client=client,
        chat_id=message.chat.id,
        text=very_long_text,
        max_chars=4000,
        delay=0.2,
    )


if __name__ == "__main__":
    print(
        "🤖 ChatPack production test bot is active... Send /start in private chat."
    )
    app.run()