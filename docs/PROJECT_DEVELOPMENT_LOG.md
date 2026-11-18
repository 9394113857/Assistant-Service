# Assistant Service — Project Development Log

This file records verified code changes, tests, decisions, and pending work.

## 2026-11-18 — Web assistant reference capabilities (Phase 1)

### Scope
- Target channel: Angular/web chat API.
- Reference: the legacy WhatsApp bot `app.py` supplied in the project conversation.
- Preserve the existing Flask application factory, routes, orchestrator, intent registry, and handler structure.
- Do not add a Twilio/WhatsApp webhook in this phase.

### Changes prepared
- Expanded rule-based intent detection to recognize the reference bot's information commands and existing e-commerce intents.
- Aligned intent names with the handler registry.
- Added an information handler and a shared public-information service.
- Added request timeouts and environment-based API-key configuration for external providers.
- Extended greeting/identity/about responses.
- Updated the orchestrator's login gate to use explicit account-specific intent names instead of broad keyword substring checks.
- Added unit tests for intent classification.

### Provider notes
- Weather requires `OPENWEATHERMAP_API_KEY`.
- News requires `NEWS_API_KEY`.
- Movie lookup requires `OMDB_API_KEY`.
- COVID statistics require a verified provider URL in `COVID_STATS_API_URL`. The legacy reference endpoint is not reused because its reliability/status is not established.
- Joke, fact, dictionary, books, Wikipedia, and quote lookups use public endpoints. External services can change or impose limits.

### Validation status
- Code changes are committed on the feature branch, not merged into `main`.
- Unit tests are added but have not yet been executed in the deployed environment.
- External API calls and API-key configuration have not yet been verified.
- Do not mark a feature production-tested until its endpoint is exercised successfully.

### Next steps
1. Run unit tests and resolve any failures.
2. Configure API keys in the local environment and Render service environment.
3. Exercise each information intent through `POST /api/v1/assistant/chat`.
4. Review the Angular chat UI's handling of response, intent, confidence, and provider errors.
5. Add a CI test job and update the main project TODO tracker after verification.
