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

        if "simpler words" in msg or "simpler terms" in msg or "explain that" in msg:
            return "Of course! Which part would you like me to explain more simply?"

        if "something else" in msg or "start over" in msg:
            return "Of course! What would you like to explore next?"

        if (
            msg in {"about", "#about", "help", "#help", "features"}
            or "what can you do" in msg
            or "what can you help" in msg
            or "how can you help" in msg
            or "what services do you offer" in msg
            or "information about your services" in msg
            or "tell me about your services" in msg
            or "what do you offer" in msg
        ):
            return (
                "I'm your AI Assistant. I can help you browse products, check "
                "catalogue prices, access your orders when you're logged in, "
                "and provide recommendations. I can also look up weather, news, "
                "books, movies, word meanings, synonyms, Wikipedia summaries, "
                "jokes, facts, and quotes. Some commerce actions, including cart "
                "updates and live stock checks, are not yet available in chat."
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
