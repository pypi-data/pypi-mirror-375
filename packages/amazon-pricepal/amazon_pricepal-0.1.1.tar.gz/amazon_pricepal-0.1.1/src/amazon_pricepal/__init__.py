import requests
from bs4 import BeautifulSoup


def get_amazon_price(url: str, headers=None) -> float:
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    price_tag = soup.find("span", class_="a-price-whole")
    coins_tag = soup.find("span", class_="a-price-fraction")
    if not price_tag:
        raise ValueError("Price not found on page.")
    price = float(f"{price_tag.text}{coins_tag.text}")
    return price

