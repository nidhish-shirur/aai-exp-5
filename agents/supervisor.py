class SupervisorAgent:

    def review(self, state):

        errors = []

        if not state.get("search_results"):
            errors.append("Search Agent returned no products.")

        if not state.get("filtered_results"):
            errors.append("Filter Agent returned no matching products.")

        if not state.get("ranking"):
            errors.append("Ranking Agent returned no recommendations.")

        validation = state.get("validation", {})

        if validation and not validation.get("valid", False):
            errors.append("Recommendation failed validation.")

        if errors:

            return {
                "status": "REVIEW_REQUIRED",
                "errors": errors
            }

        return {
            "status": "READY_FOR_APPROVAL",
            "errors": []
        }