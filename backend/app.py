import os
import random
import string

import stripe
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
stripe.api_version = "2026-06-24.dahlia"

DOMAIN = os.environ.get("DOMAIN", "http://localhost:5173")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
PRICE_ID = os.environ["STRIPE_PRICE_ID"]
UPSELL_PRICE_ID = os.environ["STRIPE_UPSELL_PRICE_ID"]
TRIAL_PERIOD_DAYS = 30
COLLECT_TERMS_OF_SERVICE = os.environ.get("COLLECT_TERMS_OF_SERVICE", "false").lower() == "true"

app = Flask(__name__)
CORS(app, origins=[DOMAIN])


def integration_tag(name: str) -> str:
    suffix = "".join(random.choices(string.ascii_letters, k=8))
    return f"{name}-{suffix}"


@app.post("/create-checkout-session")
def create_checkout_session():
    try:
        params = {
            "mode": "subscription",
            "line_items": [
                {
                    "price": PRICE_ID,
                    "quantity": 1,
                }
            ],
            "optional_items": [
                {
                    "price": UPSELL_PRICE_ID,
                    "quantity": 1,
                    "adjustable_quantity": {"enabled": False},
                }
            ],
            "subscription_data": {"trial_period_days": TRIAL_PERIOD_DAYS},
            "allow_promotion_codes": True,
            "automatic_tax": {"enabled": True},
            "custom_fields": [
                {
                    "key": "referral_source",
                    "label": {"type": "custom", "custom": "How did you hear about us?"},
                    "type": "text",
                    "optional": True,
                }
            ],
            "success_url": f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{DOMAIN}/cancel",
            "integration_identifier": integration_tag("checkout"),
        }
        if COLLECT_TERMS_OF_SERVICE:
            params["consent_collection"] = {"terms_of_service": "required"}

        session = stripe.checkout.Session.create(**params)
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.post("/webhook")
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return "", 400

    event_type = event["type"]
    data = event["data"]["object"]

    presentment = data["presentment_details"] if "presentment_details" in data else None

    if event_type == "checkout.session.completed":
        # TODO: fulfill the order (mark as paid, send email, etc.)
        if presentment:
            print(
                f"Checkout session completed: {data['id']} "
                f"paid {presentment['presentment_amount']} {presentment['presentment_currency']}"
            )
        else:
            print(f"Checkout session completed: {data['id']}")
    elif event_type == "payment_intent.succeeded":
        if presentment:
            print(
                f"PaymentIntent succeeded: {data['id']} "
                f"paid {presentment['presentment_amount']} {presentment['presentment_currency']}"
            )
    elif event_type == "customer.subscription.created":
        if presentment:
            print(
                f"Subscription created: {data['id']} "
                f"local currency {presentment['presentment_currency']}"
            )
    elif event_type == "customer.subscription.updated":
        # TODO: sync subscription status/plan changes (e.g. upgrade, downgrade, past_due)
        print(f"Subscription updated: {data['id']} -> {data['status']}")
    elif event_type == "customer.subscription.deleted":
        # TODO: revoke access for the canceled subscription
        print(f"Subscription canceled: {data['id']}")
    elif event_type == "invoice.payment_failed":
        # TODO: notify the customer and/or restrict access after retries are exhausted
        print(f"Invoice payment failed: {data['id']}")

    return jsonify(received=True)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
