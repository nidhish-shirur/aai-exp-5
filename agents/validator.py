class ValidatorAgent:

    def validate(self, ranking, requirements):

        if not ranking:
            return {
                "valid": False,
                "message": "No products available for validation.",
                "checks": {}
            }

        checks = {}

        for product in ranking:

            product_id = product["product_id"]

            checks[product_id] = {
                "budget": (
                    product["price"] <= requirements["max_price"]
                    if requirements.get("max_price") is not None
                    else True
                ),
                "ram": (
                    product["ram_gb"] >= requirements["min_ram_gb"]
                    if requirements.get("min_ram_gb") is not None
                    else True
                ),
                "storage": (
                    product["storage_gb"] >= requirements["min_storage_gb"]
                    if requirements.get("min_storage_gb") is not None
                    else True
                ),
                "rating": (
                    product["rating"] >= requirements["min_rating"]
                    if requirements.get("min_rating") is not None
                    else True
                )
            }

        top_product = ranking[0]
        top_checks = checks[top_product["product_id"]]

        valid = all(top_checks.values())

        return {
            "valid": valid,
            "message": (
                "Recommendation passed validation."
                if valid
                else "Recommendation failed validation."
            ),
            "checks": top_checks,
            "validated_product": top_product
        }