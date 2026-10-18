from html.parser import HTMLParser
import re
import os

class ProductParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = []
        self.current = {}
        self.field = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if "product" in attrs.get("class", "").lower():
            self.current = {}

        if self.current is not None:
            classes = attrs.get("class", "").lower()

            if "name" in classes or "title" in classes:
                self.field = "name"
            elif "price" in classes:
                self.field = "price"
            elif "rating" in classes or "stars" in classes:
                self.field = "rating"

    def handle_data(self, data):
        if self.field and self.current is not None:
            value = data.strip()
            if value:
                self.current[self.field] = (
                    self.current.get(self.field, "") + value
                )

    def handle_endtag(self, tag):
        if self.field:
            self.field = None

        if self.current and all(
            key in self.current for key in ("name", "price", "rating")
        ):
            self.products.append(self.current)
            self.current = {}

def normalize_price(price):
    value = re.sub(r"[^\d.]", "", price)
    try:
        return float(value)
    except ValueError:
        return None

def extract_products(path):
    parser = ProductParser()

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                parser.feed(line)
    except OSError:
        print(f"Warning: Could not read {path}")
        return []

    results = []

    for product in parser.products:
        name = product["name"].strip()
        price = normalize_price(product["price"])

        rating_match = re.search(r"\d+(?:\.\d+)?", product["rating"])

        if not name or price is None or not rating_match:
            continue

        rating = float(rating_match.group())

        if rating < 0 or rating > 5:
            continue

        results.append({
            "name": name,
            "price": price,
            "rating": rating
        })

    return results

print("=== Offline Web Scraping Ranker ===")

p, k = map(int, input("Enter number of HTML files and K: ").split())

files = []

for i in range(p):
    files.append(input(f"Enter HTML file path {i + 1}: ").strip())

unique_products = {}

for path in files:
    for product in extract_products(path):
        key = product["name"].casefold()

        if key not in unique_products:
            unique_products[key] = product
        elif (
            product["rating"] > unique_products[key]["rating"]
            or (
                product["rating"] == unique_products[key]["rating"]
                and product["price"] < unique_products[key]["price"]
            )
        ):
            unique_products[key] = product

ranked_products = sorted(
    unique_products.values(),
    key=lambda product: (
        -product["rating"],
        product["price"],
        product["name"].casefold()
    )
)

for product in ranked_products[:k]:
    price = int(product["price"]) if product["price"].is_integer() else product["price"]
    print(f"{product['name']} {price} {product['rating']:.1f}")