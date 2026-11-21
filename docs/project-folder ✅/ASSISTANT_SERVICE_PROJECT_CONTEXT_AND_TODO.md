# 🧠 Assistant Service – Project Context, Architecture & TODO Tracker

**Repository:** [9394113857/assistant-service](https://github.com/9394113857/assistant-service)  
**Branch:** `main`  
**Project:** E-commerce AI Assistant Microservice  
**Backend:** Python + Flask  
**Database:** Supabase PostgreSQL / SQLite  
**Deployment:** Render + Docker Hub  
**CI/CD:** GitHub Actions  
**Last Repository Inspection:** 18-Nov-2026

---

# 1. Project Overview

The Assistant Service is an independent Flask microservice integrated with an e-commerce platform.

Its primary responsibility is to understand user messages, identify user intent, maintain conversational context, execute the appropriate backend operations, and generate assistant responses.

The architecture is designed to support:

- Rule-based intent detection.
- Machine Learning-based intent classification.
- Intent handler architecture.
- Conversation session management.
- Follow-up query resolution.
- Guest and authenticated user interactions.
- Product and order service integrations.
- Personalized product recommendations.
- Assistant training data collection.
- Future LLM and Agentic AI integrations.

# 2. Existing Project Structure

```text
assistant-service/
│
├── .github/
│   └── workflows/
│       ├── B-auth-image-first-push.yml
│       ├── ci-render.yml
│       └── cd-render.yml
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── intents/
│   │   ├── base_handler.py
│   │   ├── greeting_handler.py
│   │   ├── order_handler.py
│   │   ├── product_handler.py
│   │   ├── recommendation_handler.py
│   │   └── unknown_handler.py
│   │
│   ├── models/
│   │   ├── assistant_training_log.py
│   │   ├── chat_message.py
│   │   └── chat_session.py
│   │
│   ├── routes/
│   │   └── assistant_routes.py
│   │
│   └── services/
│       ├── assistant_orchestrator.py
│       ├── followup_resolver.py
│       ├── intent_registry.py
│       ├── intent_service.py
│       ├── llm_service.py
│       ├── ml_model_loader.py
│       └── tool_router.py
│
├── docs/
│   ├── Model-Development/
│   ├── Stages-Wise-To-Do-Setups/
│   ├── project-folder/
│   ├── feature1_assistant_architecture.md
│   └── project-updates.txt
│
├── migrations/
│   ├── env.py
│   └── versions/
│
├── models/
│   └── assistant_intent_model.pkl
│
├── Dockerfile
├── requirements.txt
├── run.py
└── wsgi.py
```

# 3. Existing Technology Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| API Architecture | REST API |
| Database | Supabase PostgreSQL |
| Local Database | SQLite |
| ORM | Flask-SQLAlchemy |
| Database Migration | Flask-Migrate / Alembic |
| ML Framework | Scikit-learn |
| Model Serialization | Joblib |
| API Communication | Requests |
| LLM Integration | OpenAI API service |
| Authentication Integration | JWT authorization forwarding |
| Containerization | Docker |
| Container Registry | Docker Hub |
| Deployment | Render |
| CI/CD | GitHub Actions |
| Email Notifications | Gmail SMTP |
| Frontend Integration | Angular Chat Widget |

# 4. Existing Application Architecture

```text
Angular Ecommerce Application
             |
             v
       Chat Widget
             |
             v
    Assistant Flask API
             |
             v
    Assistant Orchestrator
             |
             v
     Chat Session Manager
             |
             v
      Conversation Context
             |
             v
       Follow-up Resolver
             |
             v
        Intent Detection
             |
             v
        Intent Registry
             |
             v
        Intent Handler
             |
      +------+-------+
      |      |       |
      v      v       v
   Product Order Recommendation
   Handler Handler Handler
      |      |       |
      +------+-------+
             |
             v
     Backend Microservices
             |
             v
       Assistant Response
             |
             v
       Chat Message Storage
             |
             v
    Assistant Training Logs
             |
             v
       Future ML Retraining
```

# 5. Existing API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application health check |
| POST | `/api/v1/assistant/chat` | Process assistant messages |

Example request:

```json
{
  "user_id": 101,
  "message": "show products"
}
```

Example response:

```json
{
  "response": "Here are some products",
  "intent": "show_products",
  "confidence": 0.90,
  "model_version": "rule_v1"
}
```

# 6. Existing Database Models

## chat_sessions

- id
- user_id (nullable for guest users)
- created_at

## chat_messages

- id
- session_id
- role
- message
- created_at

## assistant_training_logs

- id
- user_id (nullable for guest users)
- user_message
- predicted_intent
- confidence_score
- actual_intent
- model_version
- created_at

Alembic migration history currently contains:

1. Initial assistant tables.
2. Assistant training logs table.
3. Allow guest chat sessions.
4. Allow guest users in assistant training logs.

# 7. Existing Features and Implementation Status

## Feature 1 – Assistant Foundation

Implemented components:

- Flask assistant microservice.
- Assistant API endpoint.
- Intent handler architecture.
- Intent registry.
- Product handler.
- Order handler.
- Recommendation handler.
- Greeting handler.
- Unknown intent handler.
- Guest user support.
- Login restrictions for protected operations.
- Chat session storage.
- Assistant message storage.
- Training log storage.
- Product microservice communication.

## Feature 2 – Conversation Context Memory

Implemented components:

- Reuse latest chat session.
- Retrieve recent conversation messages.
- Conversation context preparation.
- Follow-up resolver.
- Context-aware intent detection input.
- Product-related follow-up handling.

Example:

```text
User: Show products

Assistant: Here are some products.

User: Recommend one.

Assistant: Resolves the follow-up using previous context.
```

Note: The follow-up resolver currently supports only limited keyword-based scenarios.

## Feature 3 – ML Recommendation Integration

Historical documentation records Feature 3 as the next planned milestone.

The recommendation service integration already has a basic handler and API communication function.

Further ML recommendation improvements remain open.

# 8. Important Existing Issues Identified During Repository Inspection

These are code-review findings, not confirmed production incidents.

## Issue 1 – ML Model Is Loaded But Not Used

File:

`app/services/ml_model_loader.py`

The application loads:

`models/assistant_intent_model.pkl`

However, `app/services/intent_service.py` currently uses keyword-based rule matching.

The loaded ML model is not currently invoked by `detect_intent()`.

Required resolution:

- Inspect the serialized model and its training pipeline.
- Verify the expected input format.
- Integrate actual ML prediction.
- Return predicted intent and confidence.
- Retain rule-based fallback when ML is unavailable.
- Record accurate model version information.

## Issue 2 – Intent Naming Mismatch

Files:

- `app/services/intent_service.py`
- `app/services/intent_registry.py`
- `app/services/assistant_orchestrator.py`

Current detector examples:

- `show_products`
- `show_orders`
- `recommend_product`
- `track_order`

Registry currently expects:

- `product`
- `order`
- `recommendation`
- `greeting`
- `unknown`

Required resolution:

- Define a consistent intent naming convention.
- Introduce intent normalization.
- Map product-related intents to ProductHandler.
- Map order-related intents to OrderHandler.
- Map recommendation-related intents to RecommendationHandler.
- Add explicit tests for every mapping.

## Issue 3 – Greeting Keyword Matching

File:

`app/services/intent_service.py`

Current implementation checks whether `"hi"` exists anywhere in the message.

This can incorrectly classify unrelated messages containing those characters.

Required resolution:

- Use word-boundary matching.
- Normalize punctuation and whitespace.
- Support common greeting variations.
- Add false-positive test cases.

## Issue 4 – Guest Session Separation

File:

`app/services/assistant_orchestrator.py`

Current session lookup uses:

`ChatSession.query.filter_by(user_id=user_id)`

For guest users, `user_id` is NULL.

Different guest visitors could therefore reuse the same guest session.

Required resolution:

- Introduce a unique guest session identifier.
- Accept a session identifier from the frontend.
- Validate ownership and session continuity.
- Keep authenticated user sessions isolated.
- Add database indexes and constraints where appropriate.
- Create a safe migration.

## Issue 5 – Login Restriction Keyword Matching

File:

`app/services/assistant_orchestrator.py`

Current login restriction checks keywords such as:

- order
- track
- status
- recommend

These checks can incorrectly block unrelated messages.

Required resolution:

- Use normalized intent-based access policies.
- Validate authenticated identity.
- Avoid relying only on substring matching.
- Ensure downstream APIs enforce authorization independently.

## Issue 6 – Follow-up Resolver Limitations

File:

`app/services/followup_resolver.py`

Current implementation supports a limited set of product-related follow-ups.

Required improvements:

- Support multi-turn context.
- Handle pronouns and references.
- Handle product categories.
-


# 15. Web Assistant Reference Capabilities — Implementation Update (18-Nov-2026)

The legacy WhatsApp bot `app.py` was used as a functional reference. The selected target is the existing Angular/web chat API; no Twilio webhook is being added in this phase.

## Added architecture components

- `app/intents/information_handler.py` — routes information intents to the service layer.
- `app/services/public_information_service.py` — contains isolated provider functions for public information lookups.
- `app/services/intent_service.py` — expanded rule-based intent recognition; rule-based model version is now `rule_v3`.
- `app/services/intent_registry.py` — maps the expanded intent names to existing and new handlers.
- `tests/test_intent_service.py` — unit tests for reference commands, e-commerce intents, greeting false positives, and query extraction.
- `docs/PROJECT_DEVELOPMENT_LOG.md` — date-wise implementation and validation log.

## Reference capabilities recognized

- Greeting and conversational responses.
- Assistant identity and About/help.
- Jokes.
- Top news headlines.
- Random facts.
- COVID statistics (requires a verified provider configuration).
- Synonyms.
- Word meanings and examples.
- Book information.
- Movie information.
- Weather.
- Wikipedia summaries.
- Quotes.

Existing e-commerce product, order, tracking, and recommendation intent names are also mapped through the registry.

## External provider configuration

Set these environment variables in local development and the Render service environment where required:

- `OPENWEATHERMAP_API_KEY` — weather.
- `NEWS_API_KEY` — India top headlines.
- `OMDB_API_KEY` — movie details.
- `COVID_STATS_API_URL` — optional verified COVID statistics provider endpoint.

Never commit real API keys. An example variable file is available at `.env.example`.

## Validation record

- GitHub Actions CI run #15 passed.
- Python syntax validation passed for 30 Python files.
- Six unit tests passed.
- Live external API calls and Render integration have not yet been verified.
- Changes remain on `feature/web-assistant-reference-capabilities`; they have not been merged into `main`.

## Remaining work

1. Configure provider API keys securely.
2. Test each public-information capability through `POST /api/v1/assistant/chat`.
3. Add mocked integration tests for external provider response shapes and error handling.
4. Verify Angular chat rendering and response behavior.
5. Review provider reliability, rate limits, and terms before production use.
6. Choose and verify a reliable COVID statistics provider before enabling that capability.
7. Verify public category filtering, explicit budget filtering, and cheapest-first sorting through the live Angular chat after the backend deployment.
8. Review order tracking so `track_order` can retrieve a specific order status rather than only returning the recent-order list.


# 16. Product Chat Regression Fixes — 21-Nov-2026

The following changes are committed to `main` in `Assistant-Service`:

- Fixed follow-up resolution so the standalone word `one` is not matched inside `smartphones` or `headphones`; only prior user messages are used as context.
- Kept public catalogue/category searches and price searches outside the login-required intent set.
- Added `cheapest` recognition and ascending price sorting.
- Added explicit numeric budget parsing for values such as `₹20,000`, `20k`, and `1 lakh`; `below`/ `under` are strict upper bounds, while `up to`/ `within` are inclusive.
- Added a public general-knowledge route backed by Wikipedia search and page summaries.
- Added regression tests for intent routing, follow-up resolution, price filtering, sorting, and the general-knowledge answer path.
- Updated CI to execute the unit test suite.

The Angular chat component and ML training repository were reviewed for this issue but did not require code changes: the frontend parser already accepts the backend's product response format, and the current runtime intent detector is rule-based rather than invoking the trained ML classifier. Do not connect the ML model to live intent routing until it passes the agreed evaluation threshold.
