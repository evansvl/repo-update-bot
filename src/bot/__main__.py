import asyncio
import json
import logging
import os
import re
from contextlib import suppress

import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
except (ValueError, TypeError):
    logging.critical("FATAL: ADMIN_ID is not a valid integer or is not set in the environment.")
    exit(1)

CONFIG_FILE = "/data/bot_configs.json"
CHECK_INTERVAL_SECONDS = 60

if not TELEGRAM_BOT_TOKEN:
    logging.critical("FATAL: TELEGRAM_BOT_TOKEN is not set in the environment.")
    exit(1)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdminFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == ADMIN_ID

class SetupForm(StatesGroup):
    waiting_for_repo = State()
    waiting_for_channel = State()

def load_configs():
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_configs(configs):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(configs, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save configs to {CONFIG_FILE}: {e}")

@dp.message(Command("start"), AdminFilter())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.reply(
        "Hi, Admin! Let's set up a new GitHub release notification.\n\n"
        "First, please send me the repository you want to monitor.\n"
        "Use the format `owner/repository` (e.g., `aiogram/aiogram`)."
    )
    await state.set_state(SetupForm.waiting_for_repo)

@dp.message(Command("cancel"), AdminFilter(), StateFilter("*"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("Setup cancelled. You can start over with /start.")

@dp.message(F.from_user.id != ADMIN_ID)
async def handle_unauthorized(message: types.Message):
    """Silently ignores any user who is not the designated admin."""
    logging.warning(f"Unauthorized access attempt by user {message.from_user.id} ({message.from_user.full_name})")
    return

@dp.message(SetupForm.waiting_for_repo, AdminFilter())
async def process_repo(message: types.Message, state: FSMContext):
    repo_pattern = r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$"
    if not re.match(repo_pattern, message.text):
        await message.reply(
            "That format seems incorrect.\n"
            "Please use the exact `owner/repository` format and try again."
        )
        return

    repo = message.text
    await state.update_data(repo=repo)
    await message.reply(
        f"Great! I'll monitor `{repo}`.\n\n"
        "Now, add this bot as an **administrator** to your Telegram channel "
        "with permission to 'Post messages'.\n\n"
        "Once done, send me the channel's username (e.g., `@yourchannel`)",
        parse_mode="Markdown"
    )
    await state.set_state(SetupForm.waiting_for_channel)

@dp.message(SetupForm.waiting_for_channel, AdminFilter())
async def process_channel(message: types.Message, state: FSMContext):
    channel_name = message.text
    try:
        chat = await bot.get_chat(channel_name)
        admins = await bot.get_chat_administrators(chat.id)
        if not any(admin.user.id == bot.id for admin in admins):
            await message.reply(
                "I don't seem to be an admin in that channel. "
                "Please make sure the bot is an administrator with 'Post messages' rights and try again."
            )
            return
    except TelegramBadRequest:
        await message.reply("I couldn't find that channel. Please check the username or link and ensure the bot has been added.")
        return
    except Exception as e:
        logging.error(f"Error validating channel {channel_name}: {e}")
        await message.reply("An unexpected error occurred. Please try again.")
        return

    user_data = await state.get_data()
    repo = user_data['repo']
    configs = load_configs()

    new_config = {
        "repo": repo,
        "channel_id": chat.id,
        "channel_title": chat.title,
        "last_release_id": None
    }
    configs.append(new_config)
    save_configs(configs)

    await message.reply(
        f"✅ Success! I will now monitor the `{repo}` repository and post new releases to the <b>{chat.title}</b> channel."
    )
    await state.clear()

async def get_latest_github_release(session: aiohttp.ClientSession, repo: str):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 404:
                logging.warning(f"Repository {repo} not found (404). It might be private or have a typo.")
                return None
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        logging.error(f"Error fetching GitHub release for {repo}: {e}")
        return None

async def scheduled_checker():
    await asyncio.sleep(15) 
    async with aiohttp.ClientSession() as session:
        while True:
            logging.info("Running scheduled check for new releases...")
            configs = load_configs()
            if not configs:
                logging.info("No configurations found. Skipping check.")
            else:
                for config in configs:
                    latest_release = await get_latest_github_release(session, config["repo"])
                    if not latest_release:
                        continue

                    latest_id = latest_release.get("id")
                    if latest_id != config.get("last_release_id"):
                        logging.info(f"New release found for {config['repo']}: {latest_release.get('name')}")
                        if config.get("last_release_id") is not None:
                            message_text = (
                                f"🎉 *New Release: {latest_release.get('name')}*\n\n"
                                f"**Repository**: `{config['repo']}`\n"
                                f"**Tag**: `{latest_release.get('tag_name')}`\n\n"
                                f"[View Release on GitHub]({latest_release.get('html_url')})"
                            )
                            try:
                                await bot.send_message(
                                    config["channel_id"],
                                    message_text,
                                    parse_mode="Markdown",
                                    disable_web_page_preview=True
                                )
                            except Exception as e:
                                logging.error(f"Failed to send message to channel {config['channel_id']}: {e}")

                        config["last_release_id"] = latest_id
                        save_configs(configs)
                    await asyncio.sleep(2)

            logging.info(f"Check finished. Waiting for {CHECK_INTERVAL_SECONDS} seconds.")
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

async def main():
    logging.info(f"Bot starting... Authorized Admin User ID is {ADMIN_ID}")
    asyncio.create_task(scheduled_checker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())