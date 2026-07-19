# Stripe Subscription Checkout

A monthly subscription integration using Stripe's hosted Checkout, with a Flask backend and React (Vite) frontend.

## Features

- Stripe-hosted Checkout in subscription mode
- Multi-currency pricing (USD/EUR/INR) with local payment methods (iDEAL, SEPA, UPI, etc.)
- 30-day free trial
- Optional upsell item (Priority Support Add-on)
- Promo code support
- Automatic tax calculation (Stripe Tax)
- Custom checkout field
- Terms of service consent (live mode only)
- Webhook handling for checkout completion and subscription lifecycle events

## Project structure

```
backend/    Flask API (create-checkout-session, webhook)
frontend/   React app (Checkout, Success, Cancel pages)
render.yaml Render Blueprint for deploying both services
```

## Local development

### Backend

```
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in Stripe keys and price IDs
./venv/bin/python app.py
```

### Frontend

```
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL to the backend URL
npm run dev
```

### Webhook forwarding

```
stripe listen --forward-to localhost:5001/webhook
```

Copy the printed `whsec_...` into `backend/.env` as `STRIPE_WEBHOOK_SECRET`.

## Deployment

Deployed via the `render.yaml` Blueprint as two Render services:

- `stripe-backend` — Flask web service
- `stripe-frontend` — static site (Vite build)

After deploying, register a live webhook endpoint pointing at `<backend-url>/webhook` and set `STRIPE_WEBHOOK_SECRET` accordingly.
