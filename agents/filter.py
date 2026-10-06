import pandas as pd


class FilterAgent:

    def __init__(self, simulate_failure=False):
        self.simulate_failure = simulate_failure
        self.failure_triggered = False

    def filter_products(self, products, requirements):

        if self.simulate_failure and not self.failure_triggered:
            self.failure_triggered = True
            raise RuntimeError(
                "Temporary filtering service failure."
            )

        df = products.copy()

        category = requirements.get("category")
        max_price = requirements.get("max_price")
        min_ram = requirements.get("min_ram_gb")
        min_storage = requirements.get("min_storage_gb")
        min_rating = requirements.get("min_rating")

        if category:

            category = category.lower().strip()

            if category.endswith("s"):
                category = category[:-1]

            df = df[
                df["category"].str.lower().str.strip()
                == category
            ]

        if max_price is not None:
            df = df[
                df["price"] <= float(max_price)
            ]

        if min_ram is not None:
            df = df[
                df["ram_gb"] >= float(min_ram)
            ]

        if min_storage is not None:
            df = df[
                df["storage_gb"] >= float(min_storage)
            ]

        if min_rating is not None:
            df = df[
                df["rating"] >= float(min_rating)
            ]

        return df.reset_index(drop=True)


def filter_with_retry(
    filter_agent,
    products,
    requirements,
    max_retries=2
):

    attempts = 0

    while attempts <= max_retries:

        try:

            attempts += 1

            result = filter_agent.filter_products(
                products,
                requirements
            )

            return result, attempts

        except Exception:

            if attempts > max_retries:
                raise

    return None, attempts