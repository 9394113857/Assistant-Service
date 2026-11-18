from datetime import datetime
from app.intents.base_handler import BaseIntentHandler


class GreetingHandler(BaseIntentHandler):
    def handle(self, user_id: int, message: str) -> str:
        msg = (message or "").lower().strip()
        current_hour = datetime.now().hour

        if current_hour < 12:
            time_greeting = "Good morning ☀️"
        elif current_hour < 17:
            time_greeting = "Good afternoon 🌤"
        elif current_hour < 21:
            time_greeting = "Good evening 🌙"
        else:
            time_greeting = "Hello 🌟"

        if any(word in msg for word in ("hi", "hello", "hey", "hii", "heyy")):
            return f"{time_greeting}! 👋 How can I assist you today?"

        if any(phrase in msg for phrase in ("who made you", "who created you", "who developed you")):
            return "I was created by Raghunadh Barlapudi. ❤️"

        if "who are you" in msg or "your name" in msg:
            return "I'm your AI Assistant 🤖, built to help with products, orders, recommendations, and general information."

        if msg in {"about", "#about", "help", "#help", "features", "what can you do"}:
            return (
                "I'm your AI Assistant. I can help with products, orders, and "
                "recommendations, and I can also look up weather, news, books, "
                "movies, word meanings, synonyms, Wikipedia summaries, jokes, "
                "facts, and quotes. Try asking naturally, for example: "
                "'weather in Hyderabad' or 'meaning of Python'."
            )

        if "how are you" in msg:
            return "I'm functioning perfectly! 🚀 How can I help you today?"
        if any(word in msg for word in ("thank you", "thanks", "thx")):
            return "You're welcome! 😊 Let me know if you need anything else."
        if "good night" in msg:
            return "Good night! 🌙 Feel free to reach out anytime."
        if "good morning" in msg:
            return "Good morning! ☀️ What would you like to explore today?"
        if "good afternoon" in msg:
            return "Good afternoon! 🌤 How can I help?"
        if "good evening" in msg:
            return "Good evening! 🌆 Need help with something?"
        if msg == "fine":
            return "Nice to hear that! 😊 What can I do for you?"

        return (
            f"{time_greeting}! 👋 I can help with products, orders, "
            "recommendations, and general information. What would you like to do?"
        )
