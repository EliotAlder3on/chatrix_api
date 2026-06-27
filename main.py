import argparse
import json
import logging
import threading
import time
from datetime import datetime
import os
import cloudscraper
import requests
from bs4 import BeautifulSoup as Soup
from flask import Flask, jsonify

app = Flask(__name__)

CHARTIX_URL = "https://chartix.ir/"
MARKET_URL = "https://chartix.ir/market/tala/GlobalMeltedTehran"
TGJU_URL = "https://www.tgju.org/profile/afghan_usd"

UPSTASH_URL = os.getenv("UPSTASH_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_TOKEN")
LIST_NAME = "prices_history"


ROUTES = {
    "/market/tala/AbshodeHazer": "AbshodeHazer",
    "/market/tala/SekkeJadidEmami": "SekkeJadidEmami",
    "/market/tala/jahaniMelted": "jahaniMelted",
    "/market/tala/Gold18": "Gold18",
    "/market/tala/TDT": "TDT",
    "/market/tala/Derham": "Derham",
    "/market/tala/ABSHODE2": "ABSHODE2",
}

parser = argparse.ArgumentParser()
parser.add_argument("--upstash", default="true", choices=["true", "false"])
args = parser.parse_args()

USE_UPSTASH = args.upstash.lower() == "true"

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s"
)

sending_enabled = True
scraper = cloudscraper.create_scraper()


def make_request(url):
    try:
        response = scraper.get(
            url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        return response
    except Exception as e:
        logging.error(f"Request Error: {e}")
        return None


def extract_price(html):
    soup = Soup(html, "html.parser")

    tag = soup.find("b")
    if tag:
        return tag.text.strip()

    tag = soup.select_one("b.text-white.font-sans")
    if tag:
        return tag.text.strip()

    return None


def get_chartix_prices():
    result = {}

    for route, name in ROUTES.items():
        logging.info(f"Fetching {name}")

        response = make_request(CHARTIX_URL + route)

        if response:
            result[name] = extract_price(response.text)
        else:
            result[name] = None

        time.sleep(1)

    return result


def get_market_prices():

    response = make_request("https://chartix.ir/market/tala/GlobalMeltedTehran")

    if not response:
        return {}

    soup = Soup(response.text, "html.parser")

    prices_list = {}

    for item in soup.select("a.pop_symbol-item"):
        href = item.get("href", "")

        if href not in ROUTES:
            continue

        ps = item.find_all("p")

        if len(ps) < 2:
            continue

        key = ROUTES[href]

        prices_list[key] = ps[1].get_text(strip=True)

    return prices_list


def get_herat_usd():
    try:
        logging.info("Fetching herat_usd")

        response = make_request(TGJU_URL)

        if not response:
            return None

        soup = Soup(response.text, "html.parser")

        tag = soup.find("span", attrs={"data-col": "info.last_trade.PDrCotVal"})

        if tag:
            return tag.text.strip()

    except Exception as e:
        logging.error(f"TGJU Error: {e}")

    return None


def push_to_upstash(data):
    try:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        encoded = json.dumps(payload, ensure_ascii=False)

        response = requests.post(
            f"{UPSTASH_URL}/rpush/{LIST_NAME}/{encoded}",
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"},
            timeout=30,
        )

        logging.info(f"Upstash Response: {response.status_code}")
        return True

    except Exception as e:
        logging.error(f"Upstash Error: {e}")
        return False


def print_payload(data):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))


def sender_loop():
    global sending_enabled

    while True:
        if not sending_enabled:
            time.sleep(5)
            continue

        try:
            logging.info("========== NEW CYCLE ==========")

            prices_list = get_market_prices()

            prices_list["ons"] = extract_price(
                make_request("https://chartix.ir/market/forex/OANDA_XAUUSD").text
            )

            prices_list["herat_usd"] = get_herat_usd()

            if USE_UPSTASH:
                push_to_upstash(prices_list)
                print_payload(prices_list)
            else:
                print_payload(prices_list)

        except Exception as e:
            logging.exception(f"Sender Error: {e}")

        logging.info("Sleeping 60 seconds...")
        time.sleep(60)


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "sending_enabled": sending_enabled,
            "upstash_enabled": USE_UPSTASH,
        }
    )


@app.route("/status")
def status():
    return jsonify(
        {
            "sending_enabled": sending_enabled,
            "upstash_enabled": USE_UPSTASH,
        }
    )


@app.route("/send")
def send():
    global sending_enabled

    sending_enabled = not sending_enabled

    return jsonify(
        {
            "success": True,
            "sending_enabled": sending_enabled,
        }
    )


@app.route("/prices")
def prices():
    return jsonify(
        {
            "data": get_market_prices(),
            "herat_usd": get_herat_usd(),
        }
    )


if __name__ == "__main__":
    sender_thread = threading.Thread(
        target=sender_loop,
        daemon=True,
    )

    sender_thread.start()

    logging.info("Background sender started")

    app.run(host="0.0.0.0", port=5000)
s
