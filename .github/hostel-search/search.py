"""Find cheap hostels in Chiang Mai on Booking.com and Hostelworld with headless Playwright."""
from playwright.sync_api import sync_playwright

CHECKIN, CHECKOUT = "2026-10-31", "2026-11-03"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"

BOOKING = (
    "https://www.booking.com/searchresults.en-gb.html?ss=Chiang+Mai%2C+Thailand"
    f"&checkin={CHECKIN}&checkout={CHECKOUT}&group_adults=1&no_rooms=1&group_children=0"
    "&nflt=ht_id%3D203&order=price&selected_currency=EUR&lang=en-gb"
)


def text(el, sel):
    n = el.query_selector(sel)
    return " ".join(n.inner_text().split()) if n else ""


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent=UA, locale="en-GB", viewport={"width": 1366, "height": 900})
    page = ctx.new_page()

    print(f"=== Booking.com hostels, Chiang Mai, {CHECKIN} -> {CHECKOUT}, 1 adult, EUR, cheapest first ===")
    try:
        page.goto(BOOKING, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)
        for btn in ("button#onetrust-accept-btn-handler", "button[aria-label='Dismiss sign-in info.']"):
            if page.query_selector(btn):
                page.click(btn)
        for _ in range(4):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)
        cards = page.query_selector_all('[data-testid="property-card"]')
        print("Title:", page.title(), "| cards:", len(cards))
        for c in cards[:30]:
            print(" | ".join(filter(None, [
                text(c, '[data-testid="title"]'),
                text(c, '[data-testid="price-and-discounted-price"]'),
                text(c, '[data-testid="review-score"]'),
                text(c, '[data-testid="address"]'),
                text(c, '[data-testid="distance"]'),
                text(c, '[data-testid="recommended-units"]')[:120],
            ])))
        if not cards:
            print(page.inner_text("body")[:2500])
    except Exception as e:
        print(f"Booking error: {e!r}")

    print("\n=== Hostelworld ===")
    try:
        page.goto("https://www.hostelworld.com/st/hostels/asia/thailand/chiang-mai/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)
        print("Title:", page.title())
        print(page.inner_text("body")[:6000])
    except Exception as e:
        print(f"Hostelworld error: {e!r}")
    b.close()
