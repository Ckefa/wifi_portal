from datetime import datetime, timedelta


class Package:
    def __init__(self, name: str, price: int, expiry_duration: timedelta):
        self.name = name
        self.price = price
        # timedelta representing expiry duration
        self.expiry_duration = expiry_duration

    def calculate_expiry(self):
        # Get the current datetime and add the expiry duration
        return datetime.now() + self.expiry_duration

    def __repr__(self):
        return f"{self.name} (Expires in: {self.expiry_duration}): {self.price} KES"


class PackageCatalog:
    def __init__(self):
        self.packages = [
            Package("1 Hour Package", 10, timedelta(hours=1)),
            Package("3 Hours Package", 15, timedelta(hours=3)),
            Package("12 Hours Package", 20, timedelta(hours=12)),
            Package("24 Hours Package", 30, timedelta(hours=24)),
            Package("2 Days Package", 50, timedelta(days=2)),
            Package("1 Week Package", 150, timedelta(weeks=1)),
            # Approximate month as 30 days
            Package("Monthly Package", 500, timedelta(days=30)),
        ]

    def list_packages(self):
        return self.packages

    def get_package(self, price):
        price = float(price)

        for package in self.packages:
            if package.price == price:
                return package
        return None


if __name__ == "__main__":
    # Usage example
    catalog = PackageCatalog()
    selected_package = catalog.get_package("1 Hour Package")
    if selected_package:
        expiry_time = selected_package.calculate_expiry()
        print(f"Package: {selected_package}")
        print(f"Expiry Time: {expiry_time}")
    else:
        print("Package not found.")

