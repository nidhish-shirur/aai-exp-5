import pandas as pd


class SearchAgent:

    def __init__(self, data_path):
        self.data_path = data_path

    def search(self, category=None):

        df = pd.read_csv(self.data_path)

        if category:

            category = category.lower().strip()

            # Handle common plural forms
            if category.endswith("s"):
                category = category[:-1]

            df = df[
                df["category"].str.lower().str.strip()
                == category
            ]

        return df