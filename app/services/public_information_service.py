import os
import re
from urllib.parse import quote

import requests


REQUEST_TIMEOUT = (3, 10)


def _get_json(url, params=None, headers=None):
    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _query_after_command(message, commands):
    """Extract a search term from command-style or natural-language requests."""
    text = (message or "").strip()
    alternatives = "|".join(re.escape(command) for command in sorted(commands, key=len, reverse=True))
    match = re.search(rf"#?\b(?:{alternatives})\b", text, flags=re.IGNORECASE)
    if match:
        text = text[match.end():]
    text = re.sub(r"^(please\s+)?(can you\s+)?(tell me\s+)?(what is\s+)?(the\s+)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(like|in|of|for|about|on)\s+", "", text, flags=re.IGNORECASE)
    return text.strip(" ?.!#")


def get_joke():
    try:
        data = _get_json("https://official-joke-api.appspot.com/jokes/general/random")
        joke = data[0] if isinstance(data, list) and data else data
        return f"{joke['setup']}\n{joke['punchline']}"
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return "Sorry, I couldn't retrieve a joke right now. Please try again later."


def get_news():
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "News lookup is not configured yet. Add NEWS_API_KEY to the service environment."
    try:
        data = _get_json(
            "https://newsapi.org/v2/top-headlines",
            params={"country": "in", "pageSize": 5, "apiKey": api_key},
        )
        articles = data.get("articles", [])[:5]
        if not articles:
            return "No news headlines were returned right now."
        return "Top news headlines:\n" + "\n".join(
            f"{index}. {item.get('title', 'Untitled')}\n{item.get('url', '')}"
            for index, item in enumerate(articles, start=1)
        )
    except (requests.RequestException, ValueError, TypeError):
        return "Sorry, news is temporarily unavailable. Please try again later."


def get_random_fact():
    try:
        data = _get_json("https://uselessfacts.jsph.pl/api/v2/facts/random?language=en")
        return data.get("text", "Sorry, no fact was returned right now.")
    except (requests.RequestException, ValueError, TypeError):
        return "Sorry, I couldn't retrieve a fact right now. Please try again later."


def get_synonyms(message):
    word = _query_after_command(message, ("synonyms", "synonym"))
    if not word:
        return "Please provide a word. Example: synonym happy"
    try:
        data = _get_json(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}")
        found = []
        for entry in data:
            for meaning in entry.get("meanings", []):
                found.extend(meaning.get("synonyms", []))
                for definition in meaning.get("definitions", []):
                    found.extend(definition.get("synonyms", []))
        unique = list(dict.fromkeys(found))[:10]
        return "Synonyms:\n" + (", ".join(unique) if unique else "No synonyms found for that word.")
    except (requests.RequestException, ValueError, TypeError):
        return "Sorry, I couldn't find synonyms for that word."


def get_meaning(message):
    word = _query_after_command(message, ("meaning", "define", "definition"))
    if not word:
        return "Please provide a word. Example: meaning resilience"
    try:
        data = _get_json(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}")
        definitions, examples = [], []
        for entry in data:
            for meaning in entry.get("meanings", []):
                for item in meaning.get("definitions", []):
                    if item.get("definition"):
                        definitions.append(item["definition"])
                    if item.get("example"):
                        examples.append(item["example"])
        if not definitions:
            return f"No definition found for '{word}'."
        result = f"Meaning of {word}:\n" + "\n".join(f"- {item}" for item in definitions[:5])
        if examples:
            result += "\n\nExamples:\n" + "\n".join(f"- {item}" for item in examples[:3])
        return result
    except (requests.RequestException, ValueError, TypeError):
        return f"Sorry, I couldn't find a meaning for '{word}'."


def get_book(message):
    name = _query_after_command(message, ("book",))
    if not name:
        return "Please provide a book title. Example: book Atomic Habits"
    try:
        data = _get_json(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": name, "maxResults": 1},
        )
        items = data.get("items", [])
        if not items:
            return f"I couldn't find a book named '{name}'."
        info = items[0].get("volumeInfo", {})
        authors = ", ".join(info.get("authors", [])) or "Not listed"
        return (
            f"Book: {info.get('title', name)}\n"
            f"Subtitle: {info.get('subtitle', 'Not listed')}\n"
            f"Author: {authors}\n"
            f"Publisher: {info.get('publisher', 'Not listed')}\n"
            f"Rating: {info.get('averageRating', 'Not rated')}\n"
            f"More: {info.get('infoLink', '')}"
        )
    except (requests.RequestException, ValueError, TypeError):
        return "Sorry, book information is temporarily unavailable."


def get_movie(message):
    name = _query_after_command(message, ("movie", "film"))
    api_key = os.getenv("OMDB_API_KEY")
    if not name:
        return "Please provide a movie title. Example: movie Interstellar"
    if not api_key:
        return "Movie lookup is not configured yet. Add OMDB_API_KEY to the service environment."
    try:
        data = _get_json("https://www.omdbapi.com/", params={"t": name, "apikey": api_key})
        if data.get("Response") == "False":
            return f"I couldn't find movie '{name}'."
        return (
            f"Movie: {data.get('Title', name)} ({data.get('Year', 'N/A')})\n"
            f"Released: {data.get('Released', 'N/A')}\n"
            f"IMDb rating: {data.get('imdbRating', 'N/A')}\n"
            f"Runtime: {data.get('Runtime', 'N/A')}\n"
            f"Genre: {data.get('Genre', 'N/A')}\n"
            f"Language: {data.get('Language', 'N/A')}\n"
            f"Actors: {data.get('Actors', 'N/A')}\n"
            f"Poster: {data.get('Poster', 'N/A')}"
        )
    except (requests.RequestException, ValueError, TypeError):
        return "Sorry, movie information is temporarily unavailable."


def get_weather(message):
    city = _query_after_command(message, ("weather", "temperature"))
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not city:
        return "Please provide a city. Example: weather in Hyderabad"
    if not api_key:
        return "Weather lookup is not configured yet. Add OPENWEATHERMAP_API_KEY to the service environment."
    try:
        data = _get_json(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
        )
        main = data.get("main", {})
        wind = data.get("wind", {})
        country = data.get("sys", {}).get("country", "")
        return (
            f"Weather in {data.get('name', city)} {country}:\n"
            f"Temperature: {main.get('temp', 'N/A')}°C\n"
            f"Feels like: {main.get('feels_like', 'N/A')}°C\n"
            f"Humidity: {main.get('humidity', 'N/A')}%\n"
            f"Wind speed: {wind.get('speed', 'N/A')} m/s"
        )
    except (requests.RequestException, ValueError, TypeError):
        return f"Sorry, I couldn't retrieve weather for '{city}'."


def get_wikipedia_summary(message):
    query = _query_after_command(message, ("wikipedia", "wiki"))
    if not query:
        return "Please provide a Wikipedia topic. Example: wiki Python programming language"
    try:
        data = _get_json(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query.replace(' ', '_'))}",
            headers={"User-Agent": "AssistantService/1.0 (web chat)"},
        )
        summary = data.get("extract", "")
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        if not summary:
            return f"I couldn't find a Wikipedia summary for '{query}'."
        return f"{summary[:1500]}\n\nRead more: {page_url}"
    except (requests.RequestException, ValueError, TypeError):
        return f"Sorry, I couldn't find information about '{query}'."


def get_quote():
    try:
        data = _get_json("https://zenquotes.io/api/random")
        if isinstance(data, list) and data:
            item = data[0]
            return f"{item.get('q', 'No quote returned')} — {item.get('a', 'Unknown')}"
        return "Sorry, no quote was returned right now."
    except (requests.RequestException, ValueError, TypeError):
        return "Sorry, I couldn't retrieve a quote right now."


def get_covid_stats():
    # The original WhatsApp reference used a retired third-party endpoint.
    # Require an explicitly configured replacement instead of silently
    # returning stale or fabricated public-health figures.
    endpoint = os.getenv("COVID_STATS_API_URL")
    if not endpoint:
        return (
            "COVID statistics are not connected yet. The original data provider "
            "used by the reference bot is no longer a dependable source. Configure "
            "a verified provider with COVID_STATS_API_URL before enabling live figures."
        )
    try:
        data = _get_json(endpoint, params={"country": "India"})
        keys = (
            ("Total cases", "cases"),
            ("Recovered", "recovered"),
            ("Deaths", "deaths"),
            ("Active", "active"),
            ("Critical", "critical"),
            ("New cases today", "todayCases"),
            ("New deaths today", "todayDeaths"),
        )
        lines = [f"{label}: {data.get(key, 'N/A')}" for label, key in keys]
        return "COVID-19 statistics (India):\n" + "\n".join(lines)
    except (requests.RequestException, ValueError, TypeError):
        return "COVID statistics are temporarily unavailable from the configured provider."


def handle_information_request(intent, message):
    handlers = {
        "joke": lambda: get_joke(),
        "news": lambda: get_news(),
        "random_fact": lambda: get_random_fact(),
        "synonym": lambda: get_synonyms(message),
        "meaning": lambda: get_meaning(message),
        "book": lambda: get_book(message),
        "movie": lambda: get_movie(message),
        "weather": lambda: get_weather(message),
        "wikipedia": lambda: get_wikipedia_summary(message),
        "quote": lambda: get_quote(),
        "covid_stats": lambda: get_covid_stats(),
    }
    handler = handlers.get(intent)
    if not handler:
        return "I couldn't identify that information request. Please try again."
    return handler()
