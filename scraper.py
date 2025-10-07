import re

from datetime import datetime
from utils.date_utils import month_mapping

async def find_test_dates(page, flag_selector):
    """
    Finds available test dates on the page for the next 3 months.
    Args:
        page: Playwright page object.
        flag_selector: CSS selector for language flags.
    Returns:
        List of datetime objects for available test dates.
    """
    available_dates = []
    try:
        date_nav = page.locator("app-date-navigator")
        await date_nav.wait_for(state="visible", timeout=10000)

        for _ in range(3):  # Next 3 months
            year, current_month = await get_month_info(date_nav)
            day_cells = await get_available_days(date_nav, current_month)
            for day, day_number in day_cells:
                offer_times = await extract_offer_times(page, day, year, current_month, day_number, flag_selector)
                available_dates.extend(offer_times)
                await date_nav.click()
                await page.locator("app-date-navigator").wait_for(state="visible", timeout=5000)
            await click_next_month(page)
        return available_dates
    except Exception as e:
        print(f"Error finding test dates: {e}")
        return []

async def get_month_info(date_nav):
    """
    Extracts the current month and year from the date navigator.
    Args:
        date_nav: Playwright locator for the date navigator.
    Returns:
        Tuple (year, current_month) as integers.
    """
    month_name_elem = date_nav.locator(".ngb-dp-month-name")
    month_name = (await month_name_elem.first.inner_text()).strip().lower() if await month_name_elem.count() > 0 else "?"
    match = re.search(r"([a-zäöüéèêûôîç]+)\s+(\d{4})", month_name)
    if match:
        month_str = match.group(1)
        year = int(match.group(2))
    else:
        month_str = month_name.split()[0]
        year = datetime.now().year
    current_month = month_mapping.get(month_str, 0)
    return year, current_month

async def get_available_days(date_nav, current_month):
    """
    Returns a list of tuples (day_element, day_number) for available days in the current month.
    Args:
        date_nav: Playwright locator for the date navigator.
        current_month: Integer month to filter days.
    Returns:
        List of tuples (day_element, day_number).
    """
    day_cells = await date_nav.locator("div.ngb-dp-day:not(.disabled) .day:not(.text-muted) .simple-day").element_handles()
    result = []
    for day in day_cells:
        date_of_day_element = await day.evaluate("""
            el => {
                while (el) {
                    if (el.hasAttribute('aria-label')) {
                        return el.getAttribute('aria-label');
                    }
                    el = el.parentElement;
                }
                return null;
            }
        """)
        month_of_day_element = int(date_of_day_element.split("/")[1])
        if current_month != month_of_day_element:
            continue
        has_offer = await day.evaluate(
            "el => el.parentElement.querySelector('.available-offer-bubble') !== null"
        )
        if not has_offer or not current_month:
            continue
        day_number = (await day.inner_text()).strip()
        result.append((day, day_number))
    return result

async def extract_offer_times(page, day, year, month, day_number, flag_selector):
    """
    Extracts available offer times for a given day.
    Args:
        page: Playwright page object.
        day: Playwright element handle for the day.
        year: Integer year.
        month: Integer month.
        day_number: String day number.
        flag_selector: CSS selector for language flags.
    Returns:
        List of datetime objects for available offer times.
    """
    times = []
    await day.click()
    await page.locator(".sites-offers").wait_for(state="visible", timeout=5000)
    offer_buttons = await page.locator(f"app-offer-button {flag_selector}").element_handles()
    for offer_btn in offer_buttons:
        time_text = await offer_btn.evaluate("""
            el => {
                let parent = el.closest('.cuip-button-content');
                if (!parent) return null;
                let timeDiv = parent.querySelector('div.d-flex.align-items-center.justify-content-center');
                return timeDiv ? timeDiv.childNodes[0].textContent.trim() : null;
            }
        """)
        if time_text:
            try:
                dt = datetime(year, month, int(day_number), int(time_text[:2]), int(time_text[3:5]))
                times.append(dt)
            except Exception as e:
                print(f"Could not parse datetime for {day_number} {month} {time_text}: {e}")
    return times

async def click_next_month(page):
    """
    Clicks the next month button if available.
    Args:
        page: Playwright page object.
    """
    next_month_btn = page.locator("button[title='Next month']")
    if await next_month_btn.count() > 0:
        await next_month_btn.first.click()
        await page.wait_for_timeout(1000)
