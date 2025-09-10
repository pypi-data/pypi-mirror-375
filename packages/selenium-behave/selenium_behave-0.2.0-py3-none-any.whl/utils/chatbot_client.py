class ChatbotClient:
    def send(self, message: str) -> str:
        if message.strip().lower() == "hello":
            return "hello! how can i help you?"
        return f"echo: {message}"
