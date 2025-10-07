# AutoSecurite Scraper

AutoSecurite Scraper is a Python tool to automatically check for available practical driving exam dates at Belgian driving test centers. It uses Playwright to interact with the official booking portal and can notify you via Telegram when new dates are found.

This work inspired by [Zalando Scraper](https://github.com/Dan0r/zalando-scraper).

## Features

- Scrapes available exam dates and times for a given test center.
- Supports filtering by exam language (German, French, or both).
- Sends notifications to Telegram (optional).
- Runs headless (no display required, suitable for Raspberry Pi and servers).

## Prerequisites
To use the scraper, you need an existing booking. You will receive a booking confirmation email
that includes a link to cancel or change the reservation. You need to put this link into the
 `URL` setting in `config.ini`. It has the following format:
```
https://rendezvous.permisconduire.be/public/booking/your_booking_id?token=your_token
```

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/autosecurite-scraper.git
   cd autosecurite-scraper
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   playwright install
   ```

   If running on a Raspberry Pi or headless Linux, you may need extra system libraries:
   ```sh
   sudo apt-get install -y libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libgbm1
   ```

3. **Copy and edit the configuration:**
   ```sh
   cp config.ini.sample config.ini
   ```
   Edit `config.ini` to set your preferences and (optionally) your Telegram bot credentials.

4. **Run the scraper:**
   ```sh
   python scrape.py
   ```

## Configuration

All settings are in `config.ini`. Example:

```ini
[DEFAULT]
URL = https://rendezvous.permisconduire.be/public/booking/your_booking_id?token=your_token
DATE_LANGUAGES = de,fr         ; Options: de, fr, or both (comma-separated)
HEADLESS = true                ; true = no browser window, false = show browser

[TELEGRAM]
ENABLED = false                ; true to enable Telegram notifications
TELEGRAM_BOT_TOKEN = your_bot_token_here
CHAT_ID = your_chat_id_here
FORCE_NOTIFY = false           ; true to always send notifications when new dates are found
NOTIFY_ONLY_IF_EARLIER = false ; true to only notify if a new date is earlier than your current booking
```

### Settings explained

* **URL**: The booking page URL for your test center and candidate.
* **DATE_LANGUAGES**: Which exam languages to search for (`de` for German, `fr` for French, or both).
* **HEADLESS**: Run browser in headless mode (`true` recommended for servers and Raspberry Pi).

#### Telegram section

* **ENABLED**: Set to `true` to enable Telegram notifications.
* **TELEGRAM_BOT_TOKEN**: Your Telegram bot token (get from [BotFather](https://t.me/BotFather)).
* **CHAT_ID**: The chat ID (user or group) to send notifications to.
* **FORCE_NOTIFY**: If set to `true`, a Telegram notification will be sent every time any available dates have been found. If `false`, a notification is only sent if new dates are found.
* **NOTIFY_ONLY_IF_EARLIER**: If set to `true`, you will only be notified if a newly found date is earlier than your currently scheduled exam date. If `false`, you will be notified about any new available dates.

## Sample config.ini
See [`config.ini.sample`](config.ini.sample) for a template you can safely commit.

## Telegram setup
See [How to send notifications to Telegram with Python](https://andrewkushnerov.medium.com/how-to-send-notifications-to-telegram-with-python-9ea9b8657bfb).

---

**Note:**  
- Do not commit your real Telegram bot token or chat ID to public repositories.
- For Telegram notifications, your bot must be started (for private chats) or added to the group/channel.
