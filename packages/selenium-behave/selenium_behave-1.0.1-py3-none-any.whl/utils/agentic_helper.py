class Agent:
    def __init__(self, max_steps: int = 3):
        self.max_steps = max_steps

    def run(self, goal: str) -> str:
        if "capital of france" in goal.lower():
            return "Paris"
        return f"Answer for '{goal}' (mock)"
