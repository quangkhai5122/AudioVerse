# Purchases, entitlements, quotas and creator royalties

**Not implemented.** Payment flow is legally and operationally gated; no test mode charging real accounts and no live store keys are part of starter.

## Product offers
Trial free episodes; library subscription; interactive session/minute quota; one-off season purchases. Define a single transparent unit for users (e.g., minutes of new personalized audio) and do not invent misleading in-game currency unless legal/app-store review approves.

## Store source of truth
Google Play and Apple signed purchase event/receipts verified by server with store APIs. Entitlement service stores immutable verified transaction and expiration/refund state. Native app cannot self-grant subscription. Support restore, grace/billing retry, cancellation, family/share eligibility where applicable, price changes, refunds and store notifications.

## Ledger entities
`store_transactions`, `entitlement_grants`, `entitlement_revocations`, `ai_usage_reservations`, `ai_usage_settlements`, `creator_royalty_ledger`, `creator_payout_statements` with idempotency and audit. Reserve AI spend before expensive generation; settle based on actual provider usage, release on failure; don't spend more than cap. Every user-facing quote must show applicable pricing and limits before purchase.

## Royalty accounting
Separate gross store receipts, store fee, indirect taxes/withholding, refund, eligible net receipts, creator contractual share, promotions and administrative adjustments. Royalty agreement defines basis, territory, grant, renewal, statement frequency and dispute process. Legal/accounting review needed.

## RevenueCat vs direct SDK
RevenueCat centralizes cross-store entitlements but adds cost and an external dependency; direct store validation gives more control with more engineering. Compare uptime, webhook quality, privacy policy and pricing before ADR, with verified actual store receipts for tests.

## Fraud/edge tests
Duplicate webhook, out-of-order renewal, refund after unlock, restore on new device, purchase with multiple accounts, failed TTS after quota reservation, subscription expiry while audio playing, store offline, payment chargeback. No user billed twice for one idempotent request.
