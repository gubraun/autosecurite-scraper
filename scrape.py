import asyncio
from playwright.async_api import async_playwright
import configparser
import json
import os
import re
from datetime import datetime
import telegram

CONFIG_PATH = "config.ini"
LAST_DATES_PATH = "last_dates.json"

MONTHS = {
    # German
    "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,
    # French
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12
}

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

def load_last_dates():
    if os.path.exists(LAST_DATES_PATH):
        with open(LAST_DATES_PATH, "r") as f:
            # Parse ISO strings back to datetime objects
            return set(datetime.fromisoformat(dtstr) for dtstr in json.load(f))
    return set()

def save_current_dates(dates):
    # Convert datetime objects to ISO strings for JSON serialization
    with open(LAST_DATES_PATH, "w") as f:
        json.dump([dt.isoformat() for dt in dates], f)

def should_send_telegram(current_dates, config, scheduled_date=None):
    # If always flag is set, send regardless of dates
    always = config.getboolean("TELEGRAM", "ALWAYS_SEND", fallback=False)
    if always:
        print("Always send flag is set. Sending message regardless of dates.")
        return True  # Always send if the flag is set

    # Otherwise only send if there are new dates that are earlier than the currently scheduled date

    # Check for new dates since last run
    last_dates = load_last_dates()
    new_dates = set(current_dates) - last_dates
    if new_dates:
        save_current_dates(current_dates)

    # If at least one new dates if earlier than the scheduled date, send a message
    if scheduled_date:
        earlier_dates = [dt for dt in new_dates if dt < scheduled_date]
        if earlier_dates:
            return True
    else:
        return True  # If no scheduled date, send if there are any new dates
        
    return False

async def send_telegram_message(token, chat_id, message):
    bot = telegram.Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.constants.ParseMode.HTML)
    except Exception as e:
        print(f"Telegram error: {e}")

async def main():
    # Read config
    config = configparser.ConfigParser()
    config.read("config.ini")
    url = config["DEFAULT"].get("URL")
    date_languages = config["DEFAULT"].get("DATE_LANGUAGES", "de").lower().replace(" ", "").split(",")

    # Build flag selectors based on config
    flag_selectors = []
    if "de" in date_languages:
        flag_selectors.append("span.flag-icon-de")
    if "fr" in date_languages:
        flag_selectors.append("span.flag-icon-fr")
    flag_selector = ", ".join(flag_selectors)

    headless = config["DEFAULT"].get("HEADLESS", "true").lower() == "true"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            locale="de-DE",
            extra_http_headers={
                "Accept-Language": "de-DE,de;q=0.9"
            }
        )
        page = await context.new_page()
        await page.goto(url)
        print(f"Opened {url}")

        # Accept cookie banner
        try:
            await page.wait_for_selector("cuip-cookies-consent-banner button", timeout=5000)
            await page.click("cuip-cookies-consent-banner button")
            print("Cookie banner accepted.")
        except Exception as e:
            print(f"No cookie banner found or error accepting cookies: {e}")

        # Extract currently scheduled date
        scheduled_date = await extract_scheduled_date(page)
        if scheduled_date:
            print(f"Currently scheduled date: {scheduled_date}")

        # Click the button to change the reservation
        try:
            await page.wait_for_selector("button:has-text('Verändern'), button:has-text('Change')", timeout=5000)
            await page.click("button:has-text('Verändern'), button:has-text('Change')")
            print("Clicked the button to change the reservation.")
        except Exception as e:
            print(f"Could not find or click the change reservation button: {e}")

        # Click "Verändern" next to the "Termin" part on the second page
        try:
            await page.wait_for_selector("h5:text('Termin')", timeout=5000)
            section = await page.query_selector("app-section:has(h5:text('Termin'))")
            veraendern_button = await section.query_selector("button:has-text('Verändern')")
            if veraendern_button:
                await veraendern_button.click()
                print("Clicked 'Verändern' next to 'Termin'.")
            else:
                print("Could not find 'Verändern' button next to 'Termin'.")
        except Exception as e:
            print(f"Could not find or click 'Verändern' next to 'Termin': {e}")

        # Click "Wählen Sie eine andere Verfügbarkeit aus" button on the next page
        try:
            await page.wait_for_selector("button:has-text('Wählen Sie eine andere Verfügbarkeit aus')", timeout=5000)
            await page.click("button:has-text('Wählen Sie eine andere Verfügbarkeit aus')")
            print("Clicked 'Wählen Sie eine andere Verfügbarkeit aus' button.")
        except Exception as e:
            print(f"Could not find or click 'Wählen Sie eine andere Verfügbarkeit aus' button: {e}")

        # Enter "4731" in the "Ort, Postleitzahl, Führerscheinzentrum" field
        try:
            await page.wait_for_selector("div.ng-placeholder:text('Ort, Postleitzahl, Führerscheinzentrum')", timeout=5000)
            input_box = await page.query_selector("app-site-selector input[type='text']")
            if input_box:
                await input_box.click()
                await input_box.fill("4731")
                print("Entered '4731' in the 'Ort, Postleitzahl, Führerscheinzentrum' field.")
            else:
                print("Could not find the input box for 'Ort, Postleitzahl, Führerscheinzentrum'.")
        except Exception as e:
            print(f"Could not interact with the 'Ort, Postleitzahl, Führerscheinzentrum' field: {e}")

        # Select "Führerscheinzentrum Eupen (1029)" from the dropdown
        try:
            await page.wait_for_selector("div.ng-option .site-text:text('Führerscheinzentrum Eupen (1029)')", timeout=5000)
            await page.click("div.ng-option .site-text:text('Führerscheinzentrum Eupen (1029)')")
            print("Selected 'Führerscheinzentrum Eupen (1029)'.")
        except Exception as e:
            print(f"Could not select 'Führerscheinzentrum Eupen (1029)': {e}")

        # Print currently scheduled date
        if scheduled_date:
            print("Scheduled date:")
            print("  -", scheduled_date.strftime("%A, %d.%m.%Y %H:%M"))
        else:
            print("Warning: no currently scheduled date found.")

        # Find available test dates
        available_dates = await find_test_dates(page, flag_selector)
        if available_dates:
            print("Available dates:")
            for dt in available_dates:
                print("  -", dt.strftime("%A, %d.%m.%Y %H:%M"))
        else:
            print("No available dates found.")

        # Read Telegram config
        telegram_enabled = config["TELEGRAM"].get("ENABLED", "false").lower() == "true"
        telegram_token = config["TELEGRAM"].get("TELEGRAM_BOT_TOKEN", "")
        telegram_chat_id = config["TELEGRAM"].get("CHAT_ID", "")

        if available_dates:
            msg_lines = [dt.strftime("%A, %d.%m.%Y %H:%M") for dt in available_dates]
            termin_link = f'<a href="{url}">Termin ändern</a>'
            # Add scheduled date to the message if available
            if scheduled_date:
                scheduled_date_string = scheduled_date.strftime("%A, %d.%m.%Y %H:%M")
                message = (
                    f"<b>Aktuell gebuchter Termin:</b>\n{scheduled_date_string}\n\n"
                    f"<b>Verfügbare Prüfungstermine:</b>\n" + "\n".join(msg_lines) + f"\n\n{termin_link}"
                )
            else:
                message = "<b>Verfügbare Prüfungstermine:</b>\n" + "\n".join(msg_lines) + f"\n\n{termin_link}"

            if telegram_enabled and telegram_token and telegram_chat_id:
                if should_send_telegram(available_dates, config, scheduled_date):
                    await send_telegram_message(telegram_token, telegram_chat_id, message)
                else:
                    print("No new/earlier dates. Telegram message not sent.")
        else:
            print("No available dates found.")
            # Optionally, you could clear last_dates.json here if you want to reset on no dates

        # Abort the process by clicking "Änderung abbrechen"
        try:
            await page.wait_for_selector("button.cuip-button-empty-danger span.cuip-button-content:text('Änderung abbrechen')", timeout=5000)
            await page.click("button.cuip-button-empty-danger span.cuip-button-content:text('Änderung abbrechen')")
            print('Clicked "Änderung abbrechen" to abort the process.')
        except Exception as e:
            print(f'Could not find or click "Änderung abbrechen": {e}')

        if not headless:
            # Keep browser open for manual inspection
            await page.wait_for_timeout(10000)
            
        await browser.close()

async def find_test_dates(page, flag_selector):
    available_dates = []
    try:
        # Wait for the date navigator to appear
        date_nav = await page.wait_for_selector("app-date-navigator", timeout=10000)

        for i in range(3):  # Loop through the next 3 months
            # Extract the month name from the date navigator
            month_name_elem = await date_nav.query_selector(".ngb-dp-month-name")
            month_name = (await month_name_elem.inner_text()).strip().lower() if month_name_elem else "?"
            # Try to extract year from the month name (e.g. "november 2025")
            match = re.search(r"([a-zäöüéèêûôîç]+)\s+(\d{4})", month_name)
            if match:
                month_str = match.group(1)
                year = int(match.group(2))
            else:
                # fallback: use current year
                month_str = month_name.split()[0]
                year = datetime.now().year
            month = MONTHS.get(month_str, 0)

            # Only select days that are NOT inside a .text-muted parent and have an available-offer-bubble
            day_cells = await date_nav.query_selector_all(
                "div.ngb-dp-day:not(.disabled) .day:not(.text-muted) .simple-day"
            )
            for day in day_cells:
                # Check if this day has a following sibling span.available-offer-bubble
                has_offer = await day.evaluate(
                    "el => el.parentElement.querySelector('.available-offer-bubble') !== null"
                )
                if not has_offer or not month:
                    continue
                day_number = (await day.inner_text()).strip()
                await day.click()
                # Wait for offers to load
                await page.wait_for_selector(".sites-offers", timeout=5000)
                # Find all offer buttons for the selected languages and extract their times
                offer_buttons = await page.query_selector_all(f"app-offer-button {flag_selector}")
                for offer_btn in offer_buttons:
                    # Get the time from the parent .cuip-button-content
                    time_text = await offer_btn.evaluate("""
                        el => {
                            let parent = el.closest('.cuip-button-content');
                            if (!parent) return null;
                            let timeDiv = parent.querySelector('div.d-flex.align-items-center.justify-content-center');
                            return timeDiv ? timeDiv.childNodes[0].textContent.trim() : null;
                        }
                    """)
                    if time_text:
                        # Parse time (e.g. "08:15")
                        try:
                            dt = datetime(year, month, int(day_number), int(time_text[:2]), int(time_text[3:5]))
                            available_dates.append(dt)
                        except Exception as e:
                            print(f"Could not parse datetime for {day_number} {month_name} {time_text}: {e}")
                # Go back to the date navigator (if needed)
                await date_nav.click()
                await page.wait_for_selector("app-date-navigator", timeout=5000)
            # Click next month
            next_month_btn = await page.query_selector("button[title='Next month']")
            if next_month_btn:
                await next_month_btn.click()
                await page.wait_for_timeout(1000)
            else:
                break  # No more months

        return available_dates
    except Exception as e:
        print(f"Error finding test dates: {e}")
        return []

async def extract_scheduled_date(page):
    try:
        await page.wait_for_selector("app-offer span.offer-date", timeout=10000)
        elem = await page.query_selector("app-offer span.offer-date")
        if elem:
            date_text = (await elem.inner_text()).strip()
            # Example: "Mittwoch 19 november 2025  07:30"
            match = re.search(r"(\d{1,2})\s+([a-zA-Zäöüéèêûôîç]+)\s+(\d{4})\s+(\d{2}):(\d{2})", date_text.lower())
            if match:
                day = int(match.group(1))
                month_str = match.group(2)
                month = MONTHS.get(month_str, 0)
                year = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                if month:
                    return datetime(year, month, day, hour, minute)
            print(f"Could not parse scheduled date: {date_text}")
    except Exception as e:
        print(f"Could not extract scheduled date: {e}")
    return None

if __name__ == "__main__":
    config = load_config()
    asyncio.run(main())