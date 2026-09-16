# Design a Multi-Channel Notification Service

## Problem

Build a notification platform that can send email, push, and SMS to hundreds of millions of users.

**Functional**
- APIs to enqueue a notification (template + data + channels + priority).
- User preferences (opt-out, quiet hours, channel priority).
- Delivery receipts and basic analytics.
- Support for scheduled / delayed sends.

**Non-functional**
- Peak 100k notifications/sec.
- At-least-once delivery with idempotency.
- Email must not be lost; SMS can be best-effort under extreme load.
- Multi-region, with preference for local delivery when possible.

## Your task (with AI)

1. Clarify: transactional vs marketing, ordering requirements, template rendering location.
2. Generate two architectures (one queue-centric, one more event-sourced) and compare.
3. Draft the core enqueue API and the data model for preferences + delivery state.
4. Ask the model for failure modes (provider outage, thundering herd on a celebrity user, template render spike) and how the design degrades.
5. Rough cost / capacity for the queue and the worker fleet.

Time-box: 45–60 minutes.
