# Web Assistant — Reference Capabilities

**Target:** Angular/web chat UI through the existing Assistant Service API.

**Chat endpoint:** `POST /api/v1/assistant/chat`

Example:
```json
{
  "user_id": null,
  "message": "What is the weather in Hyderabad?"
}
```

The existing response contract remains:
```json
{
  "response": "Weather details...",
  "intent": "weather",
  "confidence": 0.94,
  "model_version": "rule_v3"
}
```

## Supported reference capabilities

| Capability | Example message | Configuration |
|---|---|---|
| Greetings | `Good morning`, `How are you?` | None |
| Assistant identity | `Who are you?`, `Who made you?` | None |
| About/help | `What can you do?` | None |
| Joke | `Tell me a joke` | None |
| News | `Show today's news` | `NEWS_API_KEY` |
| Random fact | `Tell me a fact` | None |
| COVID statistics | `COVID stats India` | `COVID_STATS_API_URL` |
| Synonyms | `Synonym happy` | None |
| Meaning | `Meaning of resilience` | None |
| Book | `Book Atomic Habits` | None |
| Movie | `Movie Interstellar` | `OMDB_API_KEY` |
| Weather | `Weather in Hyderabad` | `OPENWEATHERMAP_API_KEY` |
| Wikipedia | `Wiki Python programming language` | None |
| General knowledge | `What is the capital of Japan?` | Wikipedia public API (no key) |
| Quote | `Give me a quote` | None |

Natural-language and command-style requests are both supported where a search term is required.

## Environment variables

Set provider keys in the local `.env` file and in the Render service's environment settings. Use `.env.example` as the variable-name reference. Do not commit actual keys.

- `OPENWEATHERMAP_API_KEY`
- `NEWS_API_KEY`
- `OMDB_API_KEY`
- `COVID_STATS_API_URL` (optional, only after verifying a provider)

The old WhatsApp reference used a COVID endpoint that is not reused here. The assistant reports that COVID lookup is not configured until a verified replacement is supplied. The configured endpoint is expected to accept `country=India` and return the documented statistics keys.

## Validation

Run unit tests:
```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow now executes this test command after dependency installation and syntax validation.

## Important limitations

- Public providers may impose rate limits, change response formats, or become unavailable.
- CI unit tests validate intent classification, follow-up resolution, product price filtering/sorting, and query extraction. Live Wikipedia/provider requests are not made by the unit tests.
- Configure API keys before expecting news, weather, or movie lookups to return live results.
- COVID statistics remain disabled until a reliable provider is configured.
- Public product-category searches do not require login. Explicit numeric budgets filter out products above the requested limit; cheapest/affordable requests sort by ascending price.
- Personalized recommendations and account-specific order actions remain login-protected.
- Order tracking currently routes to the existing order handler; specific order-id tracking is a separate enhancement.
