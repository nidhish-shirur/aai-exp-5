# agents/ranking.py

import time


class RankingAgent:

    def __init__(self, processing_delay=0.2):
        self.processing_delay = processing_delay

    def rank(self, products, requirements):

        time.sleep(self.processing_delay)

        ranked_products = []

        max_price = requirements.get("max_price")
        min_ram = requirements.get("min_ram_gb")
        min_storage = requirements.get("min_storage_gb")
        min_rating = requirements.get("min_rating")

        for _, product in products.iterrows():

            price_score = (
                (max_price - product["price"]) / max_price
                if max_price
                else 0
            )

            ram_score = (
                product["ram_gb"] / min_ram
                if min_ram
                else 1
            )

            storage_score = (
                product["storage_gb"] / min_storage
                if min_storage
                else 1
            )

            rating_score = (
                product["rating"] / 5
                if min_rating
                else 1
            )

            score = (
                price_score * 0.30
                + ram_score * 0.20
                + storage_score * 0.20
                + rating_score * 0.30
            )

            ranked_products.append({
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "brand": product["brand"],
                "price": product["price"],
                "ram_gb": product["ram_gb"],
                "storage_gb": product["storage_gb"],
                "rating": product["rating"],
                "processor": product["processor"],
                "score": round(score, 4)
            })

        ranked_products.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked_products