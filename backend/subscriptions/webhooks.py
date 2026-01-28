"""
Stripe Webhook Handler for processing payment events.
"""
import stripe
import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime

from .models import Subscription, SubscriptionTier, Payment, Invoice

logger = logging.getLogger('subscriptions')

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
WEBHOOK_SECRET = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    
    Supported events:
    - checkout.session.completed: New subscription created
    - customer.subscription.updated: Subscription modified
    - customer.subscription.deleted: Subscription cancelled
    - invoice.payment_succeeded: Payment successful
    - invoice.payment_failed: Payment failed
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not WEBHOOK_SECRET:
        logger.error("Stripe webhook secret not configured")
        return HttpResponse(status=500)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)
    
    # Handle the event
    event_type = event['type']
    data = event['data']['object']
    
    logger.info(f"Processing Stripe webhook: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            handle_checkout_completed(data)
        elif event_type == 'customer.subscription.updated':
            handle_subscription_updated(data)
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(data)
        elif event_type == 'invoice.payment_succeeded':
            handle_payment_succeeded(data)
        elif event_type == 'invoice.payment_failed':
            handle_payment_failed(data)
        else:
            logger.info(f"Unhandled event type: {event_type}")
    except Exception as e:
        logger.error(f"Error handling {event_type}: {e}")
        return HttpResponse(status=500)
    
    return HttpResponse(status=200)


def handle_checkout_completed(session):
    """Handle successful checkout session."""
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    metadata = session.get('metadata', {})
    user_id = metadata.get('user_id')
    tier_slug = metadata.get('tier_slug')
    
    if not user_id or not tier_slug:
        logger.error("Missing user_id or tier_slug in checkout metadata")
        return
    
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        tier = SubscriptionTier.objects.get(slug=tier_slug)
        
        # Update or create subscription
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            defaults={
                'tier': tier,
                'status': 'active',
                'stripe_customer_id': customer_id,
                'stripe_subscription_id': subscription_id,
                'start_date': timezone.now(),
            }
        )
        
        # Get subscription details from Stripe
        stripe_sub = stripe.Subscription.retrieve(subscription_id)
        subscription.next_billing_date = datetime.fromtimestamp(
            stripe_sub.current_period_end, tz=timezone.utc
        )
        subscription.billing_period = 'yearly' if stripe_sub.items.data[0].price.recurring.interval == 'year' else 'monthly'
        subscription.save()
        
        logger.info(f"Subscription activated for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing checkout: {e}")
        raise


def handle_subscription_updated(stripe_subscription):
    """Handle subscription update events."""
    subscription_id = stripe_subscription.get('id')
    status = stripe_subscription.get('status')
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        
        # Map Stripe status to our status
        status_map = {
            'active': 'active',
            'past_due': 'past_due',
            'canceled': 'cancelled',
            'unpaid': 'past_due',
            'trialing': 'trialing',
        }
        
        subscription.status = status_map.get(status, 'active')
        subscription.next_billing_date = datetime.fromtimestamp(
            stripe_subscription.get('current_period_end'), tz=timezone.utc
        )
        
        if stripe_subscription.get('cancel_at_period_end'):
            subscription.auto_renew = False
        
        subscription.save()
        logger.info(f"Subscription {subscription_id} updated to status: {status}")
        
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription not found: {subscription_id}")


def handle_subscription_deleted(stripe_subscription):
    """Handle subscription cancellation."""
    subscription_id = stripe_subscription.get('id')
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.end_date = timezone.now()
        subscription.save()
        
        logger.info(f"Subscription {subscription_id} cancelled")
        
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription not found: {subscription_id}")


def handle_payment_succeeded(invoice):
    """Handle successful payment."""
    subscription_id = invoice.get('subscription')
    amount_paid = invoice.get('amount_paid', 0) / 100  # Convert cents to dollars
    invoice_id = invoice.get('id')
    invoice_pdf = invoice.get('invoice_pdf')
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        
        # Record payment
        Payment.objects.create(
            subscription=subscription,
            amount=amount_paid,
            currency=invoice.get('currency', 'usd').upper(),
            status='completed',
            stripe_payment_id=invoice.get('payment_intent'),
        )
        
        # Record invoice
        Invoice.objects.create(
            subscription=subscription,
            stripe_invoice_id=invoice_id,
            amount=amount_paid,
            currency=invoice.get('currency', 'usd').upper(),
            status='paid',
            pdf_url=invoice_pdf,
            paid_at=timezone.now(),
        )
        
        # Ensure subscription is active
        subscription.status = 'active'
        subscription.save()
        
        # Send payment success notification email
        from notifications.email_service import send_payment_succeeded_email
        send_payment_succeeded_email.delay(subscription.id, amount_paid)
        
        logger.info(f"Payment succeeded for subscription {subscription_id}")
        
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription not found: {subscription_id}")


def handle_payment_failed(invoice):
    """Handle failed payment."""
    subscription_id = invoice.get('subscription')
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = 'past_due'
        subscription.save()
        
        # Record failed payment
        Payment.objects.create(
            subscription=subscription,
            amount=invoice.get('amount_due', 0) / 100,
            currency=invoice.get('currency', 'usd').upper(),
            status='failed',
            stripe_payment_id=invoice.get('payment_intent'),
        )
        
        logger.warning(f"Payment failed for subscription {subscription_id}")
        
        # Send notification to user about failed payment
        from notifications.email_service import send_payment_failed_email
        send_payment_failed_email.delay(subscription.id)
        
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription not found: {subscription_id}")
