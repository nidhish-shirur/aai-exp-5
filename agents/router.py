class RouterAgent:

    def route(self, task):

        routes = {
            "Search products": "Search Agent",
            "Filter products": "Filter Agent",
            "Compare products": "Comparison Agent",
            "Rank products": "Ranking Agent",
            "Validate recommendation": "Validator Agent"
        }

        return routes.get(task, "Unknown Agent")