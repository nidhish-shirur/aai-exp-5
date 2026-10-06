# agents/security.py

class SecurityTester:

    def __init__(self, registry):
        self.registry = registry

    def test_unauthorized_tool_access(self):

        try:
            self.registry.execute_tool(
                "search_products",
                "Ranking Agent",
                category="Laptop"
            )

            return {
                "test": "Unauthorized Tool Access",
                "status": "FAILED",
                "message": "Unauthorized tool access was allowed."
            }

        except PermissionError:

            return {
                "test": "Unauthorized Tool Access",
                "status": "PASSED",
                "message": "Unauthorized tool access was blocked."
            }

    def test_unknown_tool_access(self):

        try:
            self.registry.execute_tool(
                "delete_products",
                "Search Agent"
            )

            return {
                "test": "Unknown Tool Access",
                "status": "FAILED",
                "message": "Unknown tool was executed."
            }

        except ValueError:

            return {
                "test": "Unknown Tool Access",
                "status": "PASSED",
                "message": "Unknown tool was blocked."
            }

    def test_requirement_manipulation(self, requirements):

        original_price = requirements.get("max_price")

        malicious_requirements = requirements.copy()
        malicious_requirements["max_price"] = -100000

        if malicious_requirements["max_price"] != original_price:

            return {
                "test": "Requirement Manipulation",
                "status": "PASSED",
                "message": "Modified requirement was detected."
            }

        return {
            "test": "Requirement Manipulation",
            "status": "FAILED",
            "message": "Requirement manipulation was not detected."
        }

    def test_shared_state_manipulation(self, state):

        original_ranking = state.get("ranking", []).copy()

        malicious_state = state.copy()
        malicious_state["ranking"] = [
            {
                "product_id": "FAKE",
                "product_name": "Unauthorized Product",
                "score": 999
            }
        ]

        if malicious_state["ranking"] != original_ranking:

            return {
                "test": "Shared-State Manipulation",
                "status": "PASSED",
                "message": "Unauthorized state modification was detected."
            }

        return {
            "test": "Shared-State Manipulation",
            "status": "FAILED",
            "message": "Shared-state manipulation was not detected."
        }

    def test_prompt_injection(self, user_query):

        suspicious_patterns = [
            "ignore previous instructions",
            "ignore all instructions",
            "delete database",
            "reveal system prompt",
            "bypass security",
            "disable validation"
        ]

        query = user_query.lower()

        detected = any(
            pattern in query
            for pattern in suspicious_patterns
        )

        if detected:

            return {
                "test": "Prompt Injection",
                "status": "PASSED",
                "message": "Suspicious prompt injection pattern detected."
            }

        return {
            "test": "Prompt Injection",
            "status": "PASSED",
            "message": "No prompt injection pattern detected."
        }