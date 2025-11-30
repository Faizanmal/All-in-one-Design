"""
Stripe integration service for payment processing.
"""
import stripe
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger('subscriptions')

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None


class StripeService:
    """Service class for Stripe operations."""
    
    @staticmethod
    def create_customer(email: str, name: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Create a Stripe customer.
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata (e.g., user_id)
            
        Returns:
            Stripe customer ID or None if failed
        """
        if not stripe.api_key:
            logger.error("Stripe API key not configured")
            return None
            
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            logger.info(f"Created Stripe customer: {customer.id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            return None
    
    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Dict[str, Any] = None,
    ) -> Optional[Dict[str, str]]:
        """
        Create a Stripe Checkout session for subscription.
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID for the subscription
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            metadata: Additional metadata
            
        Returns:
            Dict with session_id and url, or None if failed
        """
        if not stripe.api_key:
            logger.error("Stripe API key not configured")
            return None
            
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
                subscription_data={
                    'metadata': metadata or {},
                },
                allow_promotion_codes=True,
            )
            logger.info(f"Created checkout session: {session.id}")
            return {
                'session_id': session.id,
                'url': session.url,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            return None
    
    @staticmethod
    def create_billing_portal_session(
        customer_id: str,
        return_url: str,
    ) -> Optional[str]:
        """
        Create a Stripe Billing Portal session for managing subscriptions.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal
            
        Returns:
            Portal URL or None if failed
        """
        if not stripe.api_key:
            logger.error("Stripe API key not configured")
            return None
            
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            return None
    
    @staticmethod
    def cancel_subscription(
        subscription_id: str,
        cancel_at_period_end: bool = True,
    ) -> bool:
        """
        Cancel a Stripe subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            cancel_at_period_end: If True, cancel at end of billing period
            
        Returns:
            True if successful, False otherwise
        """
        if not stripe.api_key:
            logger.error("Stripe API key not configured")
            return False
            
        try:
            if cancel_at_period_end:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                stripe.Subscription.delete(subscription_id)
            logger.info(f"Cancelled subscription: {subscription_id}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    @staticmethod
    def resume_subscription(subscription_id: str) -> bool:
        """
        Resume a cancelled subscription (if still in grace period).
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            True if successful, False otherwise
        """
        if not stripe.api_key:
            logger.error("Stripe API key not configured")
            return False
            
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False,
            )
            logger.info(f"Resumed subscription: {subscription_id}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to resume subscription: {e}")
            return False
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription details from Stripe.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription data or None if failed
        """
        if not stripe.api_key:
            logger.error("Stripe API key not configured")
            return None
            
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'canceled_at': subscription.canceled_at,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription: {e}")
            return None
    
    @staticmethod
    def construct_webhook_event(
        payload: bytes,
        sig_header: str,
        webhook_secret: str,
    ) -> Optional[stripe.Event]:
        """
        Construct and verify a Stripe webhook event.
        
        Args:
            payload: Request body bytes
            sig_header: Stripe-Signature header
            webhook_secret: Webhook endpoint secret
            
        Returns:
            Stripe Event object or None if verification failed
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return None
