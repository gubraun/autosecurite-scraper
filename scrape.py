import asyncio
import locale
import re
from playwright.async_api import async_playwright
from datetime import datetime
from scraper import find_test_dates
from utils.config_utils import load_config
from utils.storage_utils import load_last_dates, save_current_dates
from utils.telegram_utils import send_telegram_message
from utils.date_utils import month_mapping

async def main():
    # Read config
    config = load_config()
    url = config["DEFAULT"].get("URL")
    date_languages = config["DEFAULT"].get("DATE_LANGUAGES", "de").lower().replace(" ", "").split(",")

    # Set locale for date formatting
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')  # Set to German locale
    except locale.Error as e:
        print(f"Could not set locale to de_DE.UTF-8: {e}. Date formatting may not be correct.")

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
            await page.locator("cuip-cookies-consent-banner button").wait_for(state="visible", timeout=5000)
            await page.locator("cuip-cookies-consent-banner button").click()
            print("Cookie banner accepted.")
        except Exception as e:
            print(f"No cookie banner found or error accepting cookies: {e}")

        # Extract currently scheduled date
        scheduled_date = await extract_scheduled_date(page)
        if scheduled_date:
            print(f"Currently scheduled date: {scheduled_date}")

        # Click the button to change the reservation
        try:
            await page.locator("button:has-text('Verändern'), button:has-text('Change')").wait_for(state="visible", timeout=5000)
            await page.locator("button:has-text('Verändern'), button:has-text('Change')").click()
            print("Clicked the button to change the reservation.")
        except Exception as e:
            print(f"Could not find or click the change reservation button: {e}")

        # Click "Verändern" next to the "Termin" part on the second page
        try:
            await page.locator("h5:text('Termin')").wait_for(state="visible", timeout=5000)
            section = page.locator("app-section:has(h5:text('Termin'))")
            veraendern_button = section.locator("button:has-text('Verändern')")
            if await veraendern_button.count() > 0:
                await veraendern_button.first.click()
                print("Clicked 'Verändern' next to 'Termin'.")
            else:
                print("Could not find 'Verändern' button next to 'Termin'.")
        except Exception as e:
            print(f"Could not find or click 'Verändern' next to 'Termin': {e}")

        # Click "Wählen Sie eine andere Verfügbarkeit aus" button on the next page
        try:
            await page.locator("button:has-text('Wählen Sie eine andere Verfügbarkeit aus')").wait_for(state="visible", timeout=5000)
            await page.locator("button:has-text('Wählen Sie eine andere Verfügbarkeit aus')").click()
            print("Clicked 'Wählen Sie eine andere Verfügbarkeit aus' button.")
        except Exception as e:
            print(f"Could not find or click 'Wählen Sie eine andere Verfügbarkeit aus' button: {e}")

        # Enter "4731" in the "Ort, Postleitzahl, Führerscheinzentrum" field
        try:
            await page.locator("div.ng-placeholder:text('Ort, Postleitzahl, Führerscheinzentrum')").wait_for(state="visible", timeout=5000)
            input_box = page.locator("app-site-selector input[type='text']")
            if await input_box.count() > 0:
                await input_box.first.click()
                await input_box.first.fill("4731")
                print("Entered '4731' in the 'Ort, Postleitzahl, Führerscheinzentrum' field.")
            else:
                print("Could not find the input box for 'Ort, Postleitzahl, Führerscheinzentrum'.")
        except Exception as e:
            print(f"Could not interact with the 'Ort, Postleitzahl, Führerscheinzentrum' field: {e}")

        # Select "Führerscheinzentrum Eupen (1029)" from the dropdown
        try:
            await page.locator("div.ng-option .site-text:text('Führerscheinzentrum Eupen (1029)')").wait_for(state="visible", timeout=5000)
            await page.locator("div.ng-option .site-text:text('Führerscheinzentrum Eupen (1029)')").click()
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
            await page.locator("button.cuip-button-empty-danger span.cuip-button-content:text('Änderung abbrechen')").wait_for(state="visible", timeout=5000)
            await page.locator("button.cuip-button-empty-danger span.cuip-button-content:text('Änderung abbrechen')").click()
            print('Clicked "Änderung abbrechen" to abort the process.')
        except Exception as e:
            print(f'Could not find or click "Änderung abbrechen": {e}')

        if not headless:
            # Keep browser open for manual inspection
            await page.wait_for_timeout(10000)
            
        await browser.close()

def should_send_telegram(current_dates, config, scheduled_date=None):
    # If FORCE_NOTIFY flag is set, send notification regardless of dates
    force_notify = config.getboolean("TELEGRAM", "FORCE_NOTIFY", fallback=False)
    if force_notify:
        print("FORCE_NOTIFY send flag is set. Sending message regardless of dates.")
        return True  # Always send if the flag is set

    # If NOTIFY_ONLY_IF_EARLIER is set, notification is only send if there are new dates that
    # are earlier than the currently scheduled date
    notify_only_if_earlier  = config.getboolean("TELEGRAM", "NOTIFY_ONLY_IF_EARLIER ", fallback=False)

    # Check for new dates since last run
    last_dates = load_last_dates()
    new_dates = set(current_dates) - last_dates
    if new_dates:
        save_current_dates(current_dates)
        if not notify_only_if_earlier:
            return True # If NOTIFY_ONLY_IF_EARLIER is not set, send if there are any new dates

    # If at least one of the new dates is earlier than the scheduled date, send a message
    if scheduled_date:
        earlier_dates = [dt for dt in new_dates if dt < scheduled_date]
        if earlier_dates:
            return True
    else:
        return True  # If no scheduled date, send if there are any new dates
        
    return False

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
                month = month_mapping.get(month_str, 0)
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
    asyncio.run(main())