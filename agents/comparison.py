# agents/comparison.py

import time


class ComparisonAgent:

    def __init__(self, processing_delay=0.2):
        self.processing_delay = processing_delay

    def compare(self, products):

        time.sleep(self.processing_delay)

        comparisons = []

        for _, product in products.iterrows():

            comparisons.append({
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "price": product["price"],
                "ram_gb": product["ram_gb"],
                "storage_gb": product["storage_gb"],
                "rating": product["rating"],
                "processor": product["processor"]
            })

        return comparisons