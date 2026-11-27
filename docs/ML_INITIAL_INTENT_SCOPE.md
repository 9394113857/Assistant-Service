# Initial ML Intent Scope — Phase 1

## Purpose

The first supervised ML classifier is deliberately limited to five ecommerce intents. This is a staged learning milestone, not a removal of the application's other capabilities or review taxonomy.

## Approved initial ML model classes

| Intent | Meaning |
|---|---|
| `add_to_cart` | User wants to add a product to the cart |
| `view_cart` | User wants to view the cart |
| `show_orders` | User wants to list their orders |
| `track_order` | User asks about delivery or shipment progress |
| `cancel_order` | User requests order cancellation |

## Administrator review taxonomy

The administrator training-review API accepts all 23 supported assistant intents:

`add_to_cart`, `assistant_about`, `assistant_identity`, `cancel_order`, `cheaper_product`, `clarification`, `costliest_product`, `general_knowledge`, `greeting`, `product_advice`, `product_alternatives`, `product_category`, `product_compare`, `product_detail`, `product_price`, `product_stock`, `recommend_product`, `show_orders`, `show_products`, `track_order`, `unknown`, `view_cart`, and `weather`.

This review allowlist is intentionally separate from the five-class ML allowlist. Administrators can continue reviewing the full assistant taxonomy, while the initial training pipeline selects only the five approved ML labels.

## Data requirements for the initial model

- Read only records whose `model_version` is exactly `rule_v4`.
- Use only non-empty, human-reviewed `actual_intent` labels.
- Select only the five approved initial ML intents.
- Never use `predicted_intent` as the supervised target.
- Preserve all historical Supabase records and all other intent classes.
- Require at least 10 unique normalized messages for each approved intent.
- Normalize case and whitespace, reject conflicting normalized-message labels, and remove exact normalized duplicates during preparation only.
- Use a stratified 80/20 train/test split only after every class meets the minimum.
- Require at least 70% holdout accuracy and report per-class precision, recall, F1, macro F1, and the confusion matrix.
- Treat a small holdout set as an initial engineering gate, not proof of production performance.
- Insufficient data or rejected quality must leave the existing artifact unchanged.

## Verified collection snapshot

The reviewed Supabase audit for `rule_v4` returned:

| Intent | Reviewed records | Unique messages | Duplicate records |
|---|---:|---:|---:|
| `add_to_cart` | 11 | 10 | 1 |
| `view_cart` | 10 | 10 | 0 |
| `show_orders` | 15 | 10 | 5 |
| `track_order` | 22 | 22 | 0 |
| `cancel_order` | 22 | 22 | 0 |
| **Total** | **80** | **74** | **6** |

The six exact duplicate rows are retained in Supabase and removed only from the prepared ML dataset. The duplicate audit found no conflicting labels. Six additional pending records were exact-message duplicates of already-reviewed `cancel_order` examples and remain pending/excluded.

## Existing application behavior and safety

The rule-based intent detector and handler registry continue to support the wider chatbot taxonomy. The five-intent allowlist is only a guard on which model artifact may be loaded and which labels enter the first ML training run.

The current cart handler still returns a capability message rather than executing cart operations. The order handler currently returns the order list; it does not implement cancellation or full shipment tracking. Therefore, this work does **not** connect ML predictions to live action routing. That integration must wait until the relevant handlers and authorization paths are implemented and tested.

No historical rows are deleted, no database schema migration is required, and no live ML action routing is enabled by this scope change.
