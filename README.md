<div align="center" markdown="1">
<h1>🤖 GitHub Release Monitor Bot</h1>
<p>A simple, self-hosted Telegram bot to get notifications about new GitHub releases.</p>
<p>
<a href="##-one-command-installation--updates">Installation & Updates</a> •
<a href="##-bot-management">Management</a> •
<a href="##-contributing">Contributing</a>
</p>


![GitHub License](https://img.shields.io/github/license/evansvl/repo-update-bot)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/evansvl/repo-update-bot)
![GitHub Stars](https://img.shields.io/github/stars/evansvl/repo-update-bot?style=flat)

</div>


*GitHub Release Monitor Bot* is a lightweight, easy-to-deploy solution that monitors GitHub repositories for new releases and instantly sends notifications to your Telegram channel. Built with aiogram 3 and Docker, it's designed for simple setup and reliable, long-term operation.

## 🚀 Key Features

- **Automated Monitoring:** Set it up once and get timely notifications for any new release.
- **Admin-Only Access:** The bot only responds to you. All setup and management commands are restricted to the admin's Telegram ID.
- **Interactive Setup:** No need to edit config files. Just chat with your bot on Telegram to add new repositories to monitor.
- **Dockerized & Persistent:** Runs in a clean Docker environment, and your configurations are safely stored in a persistent volume.
- **One-Command Install & Update:** A single, smart script handles both the initial installation and all future updates.

## ⚠️ Requirements

A Linux server (Ubuntu or Debian are recommended).

`sudo` (root) access on the server.

`curl or wget` installed on your server (most systems have this by default).

## 🛠️ One-Command Installation & Updates

This script automates everything: it installs dependencies like Docker, clones the repository, asks for your secrets (only on the first run), and launches the bot.

**The same command works for both initial installation and for updating the bot later!**

**1. Connect to your server via SSH.**

**2. Execute this command:**

```bash
curl -sSL https://raw.githubusercontent.com/evansvl/repo-update-bot/main/install.sh | sudo bash
```

**3. Follow the on-screen instructions:**

- **First Run:** The script will detect that this is a new installation. It will ask you for your **Telegram Bot Token** and your numeric **Admin User ID**.
- **Updating:** If you run the script again in the future, it will detect the existing setup, skip the questions, pull the latest code from GitHub, and restart the bot with the new version.

## ⚙️ Initial Bot Setup

Once the installer finishes, your bot is running. Now you just need to tell it what to monitor.

1. **Find your bot on Telegram** and send the `/start` command. Since you are the admin, it will respond.
2. **Provide the Repository:** The bot will ask for the GitHub repository you want to monitor. Send it in the format `owner/repository` (e.g., `evansvl/vless-shopbot`).
3. **Add Bot to Channel:** Add your bot to the Telegram channel where you want to receive notifications. You must make it an Administrator with the permission to "Post messages".
4. **Provide Channel Info:** Send the bot your channel's username (e.g., @yourchannel) or a public link.
5. **Done!** The bot will confirm the setup and will begin checking for new releases. Repeat these steps to monitor more repositories.

## 💡 Bot Management

All management commands must be run from the project directory (~/repo-update-bot) on your server.

**View live logs (useful for troubleshooting):**

```bash
sudo docker-compose logs -f
```

**Stop the bot:**

```bash
sudo docker-compose down
```

**Start the bot after it has been stopped:**

```bash
sudo docker-compose up -d
```

## 🙌 Contributing & Bug Reports

If you find a bug or have a feature request, please open an Issue. Pull Requests are also welcome!

## 💎 Support project

**СБП/Карта РФ:** https://yookassa.ru/my/i/aJRiTyq5D3VB/l

**CryptoBot:** https://t.me/send?start=IVftnggXmRv8

**TON:** `UQAtdMEig3Wl_D3FNx4RU3RhxnoJI3IizGxrrNj3O8Q-fDpK`

**USDT (TRC20):** `TBW9TFUh93U1G5eTT1VTsZw51L669khCiz`
