"""Fetch live one-way flights from Google Flights (fast-flights) and try Skyscanner via Playwright."""
import os
import sys

from fast_flights import FlightQuery, Passengers, create_query, get_flights

DATE = os.environ.get("FLIGHT_DATE", "2026-10-31")
ORIGINS = os.environ.get("FLIGHT_FROM", "BKK,DMK").split(",")
DEST = os.environ.get("FLIGHT_TO", "CNX")

print(f"=== Google Flights: {'/'.join(ORIGINS)} -> {DEST} on {DATE}, 1 adult, economy, THB ===")
rows = []
for origin in ORIGINS:
    try:
        q = create_query(
            flights=[FlightQuery(date=DATE, from_airport=origin, to_airport=DEST)],
            trip="one-way",
            seat="economy",
            passengers=Passengers(adults=1),
            language="en-US",
            currency="THB",
        )
        res = get_flights(q)
    except Exception as e:
        print(f"[{origin}] error: {e!r}")
        continue
    for f in res:
        legs = f.flights
        dep, arr = legs[0].departure, legs[-1].arrival
        dur = sum(l.duration for l in legs)
        rows.append((
            f.price, origin, ", ".join(f.airlines),
            "%02d:%02d" % tuple(dep.time), "%02d:%02d" % tuple(arr.time),
            legs[0].from_airport.code, legs[-1].to_airport.code,
            f"{dur // 60}h{dur % 60:02d}m", len(legs) - 1,
        ))

rows.sort()
print(f"{'PRICE':>9}  {'AIRLINE':<28} DEP   ARR   ROUTE    DUR     STOPS")
for p, _, al, d, a, fa, ta, du, st in rows:
    print(f"THB {p:>5}  {al[:28]:<28} {d} {a} {fa}-{ta}  {du:<7} {st}")
print(f"Total itineraries: {len(rows)}")

print("\n=== Skyscanner (Playwright headless) ===")
try:
    from playwright.sync_api import sync_playwright

    url = f"https://www.skyscanner.net/transport/flights/bkkt/cnx/{DATE[2:4]}{DATE[5:7]}{DATE[8:10]}/?adultsv2=1&cabinclass=economy&rtn=0&currency=THB"
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = b.new_page(locale="en-GB", viewport={"width": 1366, "height": 900})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(25000)
        print("Title:", page.title())
        print(page.inner_text("body")[:4000])
        page.screenshot(path="skyscanner.png")
        b.close()
except Exception as e:
    print(f"Skyscanner error: {e!r}")
sys.exit(0)
