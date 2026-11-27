# Initial ML Intent Scope — Phase 1

## Purpose

The first supervised ML classifier is deliberately limited to five ecommerce intents. This is a staged learning milestone, not a removal of the application's other capabilities.

## Approved model classes

| Intent | Meaning |
|---|---|
| `add_to_cart` | User wants to add a product to the cart |
| `view_cart` | User wants to view the cart |
| `show_orders` | User wants to list their orders |
| `track_order` | User asks about delivery or shipment progress |
| `cancel_order` | User requests order cancellation |

## Data requirements

- Use only non-empty, human-reviewed `actual_intent` labels.
- Ignore all labels outside the five-intent allowlist for this first model.
- Preserve all historical Supabase records; do not delete the other 18 intent classes.
- Require at least 10 unique normalized messages for each approved intent.
- Normalize case and whitespace, detect conflicting labels, and remove exact normalized duplicates before splitting.
- Use a stratified 80/20 train/test split only after every class meets the minimum.
- Require at least 70% holdout accuracy and report per-class precision, recall, F1, macro F1, and the confusion matrix.
- Insufficient data or rejected quality must leave the existing artifact unchanged.

## Existing application behavior

The rule-based intent detector and handler registry continue to support the wider chatbot taxonomy. The five-intent allowlist is only a guard on which model artifact may be loaded.

The current cart handler still returns a capability message rather than executing cart operations. The order handler currently returns the order list; it does not implement cancellation or full shipment tracking. Therefore, this commit does **not** connect ML predictions to live action routing. That integration must wait until the relevant handlers and authorization paths are implemented and tested.

## Current collection snapshot

At the start of this phase, unique normalized message counts were:

| Intent | Unique messages | Minimum | Additional needed |
|---|---:|---:|---:|
| `add_to_cart` | 4 | 10 | 6 |
| `view_cart` | 3 | 10 | 7 |
| `show_orders` | 3 | 10 | 7 |
| `track_order` | 22 | 10 | 0 |
| `cancel_order` | 22 | 10 | 0 |

The first training run should report `INSUFFICIENT_DATA` until the three underrepresented classes meet the minimum. This is an expected data gate, not a pipeline software failure.
