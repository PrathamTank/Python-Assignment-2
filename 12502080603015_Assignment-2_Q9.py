import json
import os

class Product:
    def __init__(self, product_id, name, stock, purchase_price, selling_price):
        self.product_id = product_id
        self.name = name
        self.stock = int(stock)
        self.purchase_price = float(purchase_price)
        self.selling_price = float(selling_price)

    @property
    def total_value(self):
        return self.stock * self.purchase_price

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "stock": self.stock,
            "purchase_price": self.purchase_price,
            "selling_price": self.selling_price
        }


class Inventory:
    def __init__(self, name="Inventory"):
        self.name = name
        self.products = {}

    def add_product(self, product):
        if product.product_id in self.products:
            return False

        self.products[product.product_id] = product
        return True

    def delete_product(self, product_id):
        return self.products.pop(product_id, None) is not None

    def update_stock(self, product_id, quantity):
        if product_id not in self.products:
            return False

        new_stock = self.products[product_id].stock + int(quantity)

        if new_stock < 0:
            return False

        self.products[product_id].stock = new_stock
        return True

    @property
    def total_value(self):
        return sum(product.total_value for product in self.products.values())

    def __lt__(self, other):
        return self.total_value < other.total_value

    def __eq__(self, other):
        if not isinstance(other, Inventory):
            return NotImplemented
        return self.total_value == other.total_value

    def __add__(self, other):
        merged = Inventory(self.name + "+" + other.name)

        for product in self.products.values():
            merged.products[product.product_id] = Product(
                product.product_id,
                product.name,
                product.stock,
                product.purchase_price,
                product.selling_price
            )

        for product in other.products.values():
            if product.product_id in merged.products:
                existing = merged.products[product.product_id]
                existing.stock += product.stock
                existing.purchase_price = min(
                    existing.purchase_price, product.purchase_price
                )
                existing.selling_price = max(
                    existing.selling_price, product.selling_price
                )
            else:
                merged.products[product.product_id] = Product(
                    product.product_id,
                    product.name,
                    product.stock,
                    product.purchase_price,
                    product.selling_price
                )

        return merged

    def display(self):
        for product_id in sorted(self.products):
            product = self.products[product_id]
            print(
                f"{product.product_id} {product.name} "
                f"stock={product.stock} "
                f"purchase={product.purchase_price:g} "
                f"selling={product.selling_price:g}"
            )

        print(f"TOTAL_VALUE {self.total_value:g}")

    def save(self, file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                [product.to_dict() for product in self.products.values()],
                file,
                indent=2
            )

    @staticmethod
    def load(file_path):
        inventory = Inventory(os.path.basename(file_path))

        with open(file_path, "r", encoding="utf-8") as file:
            records = json.load(file)

        for record in records:
            product = Product(
                record["product_id"],
                record["name"],
                record["stock"],
                record["purchase_price"],
                record["selling_price"]
            )
            inventory.add_product(product)

        return inventory


print("=== OOP Inventory Merger ===")

try:
    file_a = input("Enter inventory A JSON file: ").strip()
    file_b = input("Enter inventory B JSON file: ").strip()

    inventory_a = Inventory.load(file_a)
    inventory_b = Inventory.load(file_b)

    while True:
        print("\n1. ADD")
        print("2. DELETE")
        print("3. UPDATE")
        print("4. MERGE")
        print("5. COMPARE")
        print("6. DISPLAY")
        print("7. SAVE")
        print("8. EXIT")

        choice = input("Enter operation: ").strip().upper()

        if choice == "1" or choice == "ADD":
            target = input("Enter inventory (A/B): ").strip().upper()
            inventory = inventory_a if target == "A" else inventory_b

            product_id = input("Enter product ID: ").strip()
            name = input("Enter product name: ").strip()
            stock = int(input("Enter stock: "))
            purchase = float(input("Enter purchase price: "))
            selling = float(input("Enter selling price: "))

            if not product_id or not name or stock < 0 or purchase < 0 or selling < 0:
                print("INVALID_PRODUCT")
            else:
                product = Product(product_id, name, stock, purchase, selling)
                print("ADDED" if inventory.add_product(product) else "DUPLICATE_ID")

        elif choice == "2" or choice == "DELETE":
            target = input("Enter inventory (A/B): ").strip().upper()
            inventory = inventory_a if target == "A" else inventory_b
            product_id = input("Enter product ID: ").strip()

            print("DELETED" if inventory.delete_product(product_id) else "NOT_FOUND")

        elif choice == "3" or choice == "UPDATE":
            target = input("Enter inventory (A/B): ").strip().upper()
            inventory = inventory_a if target == "A" else inventory_b
            product_id = input("Enter product ID: ").strip()
            quantity = int(input("Enter stock change (+/-): "))

            print("UPDATED" if inventory.update_stock(product_id, quantity) else "UPDATE_FAILED")

        elif choice == "4" or choice == "MERGE":
            merged = inventory_a + inventory_b
            print("\nMerged Inventory:")
            merged.display()

        elif choice == "5" or choice == "COMPARE":
            if inventory_a > inventory_b:
                print("Inventory A has greater total value.")
            elif inventory_a < inventory_b:
                print("Inventory B has greater total value.")
            else:
                print("Both inventories have equal total value.")

        elif choice == "6" or choice == "DISPLAY":
            target = input("Enter inventory (A/B): ").strip().upper()
            inventory = inventory_a if target == "A" else inventory_b
            inventory.display()

        elif choice == "7" or choice == "SAVE":
            inventory_a.save("inventory_a.json")
            inventory_b.save("inventory_b.json")
            print("SAVED")

        elif choice == "8" or choice == "EXIT":
            break

        else:
            print("INVALID_OPERATION")

except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
    print("ERROR:", e)