"""
International payment processing service for CineChainLanka
Handles multiple payment methods and currencies across different regions
"""

import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
import requests
from decimal import Decimal
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InternationalPaymentService:
    """
    Service for processing international payments
    """
    
    # Supported payment methods by region
    PAYMENT_METHODS = {
        'LK': {
            'local': ['lanka_qr', 'ez_cash', 'frimi', 'bank_transfer'],
            'international': ['stripe', 'paypal', 'wise', 'crypto'],
            'currency': 'LKR'
        },
        'US': {
            'local': ['stripe', 'paypal', 'venmo', 'zelle'],
            'international': ['stripe', 'paypal', 'wise', 'crypto'],
            'currency': 'USD'
        },
        'UK': {
            'local': ['stripe', 'paypal', 'bank_transfer', 'faster_payments'],
            'international': ['stripe', 'paypal', 'wise', 'crypto'],
            'currency': 'GBP'
        },
        'SG': {
            'local': ['stripe', 'paypal', 'paynow', 'grab_pay'],
            'international': ['stripe', 'paypal', 'wise', 'crypto'],
            'currency': 'SGD'
        },
        'AU': {
            'local': ['stripe', 'paypal', 'bank_transfer', 'payid'],
            'international': ['stripe', 'paypal', 'wise', 'crypto'],
            'currency': 'AUD'
        },
        'EU': {
            'local': ['stripe', 'paypal', 'sepa', 'ideal'],
            'international': ['stripe', 'paypal', 'wise', 'crypto'],
            'currency': 'EUR'
        }
    }
    
    # Exchange rates (in production, this would be fetched from a real API)
    EXCHANGE_RATES = {
        'USD': 1.0,
        'LKR': 320.0,
        'GBP': 0.79,
        'SGD': 1.35,
        'AUD': 1.52,
        'EUR': 0.92,
        'USDT': 1.0
    }
    
    @classmethod
    def get_supported_payment_methods(cls, jurisdiction: str) -> Dict:
        """Get supported payment methods for a jurisdiction"""
        return cls.PAYMENT_METHODS.get(jurisdiction.upper(), {})
    
    @classmethod
    def convert_currency(cls, amount: float, from_currency: str, to_currency: str) -> Tuple[float, float]:
        """Convert amount from one currency to another"""
        try:
            # Get exchange rates
            from_rate = cls.EXCHANGE_RATES.get(from_currency.upper(), 1.0)
            to_rate = cls.EXCHANGE_RATES.get(to_currency.upper(), 1.0)
            
            # Convert to USD first, then to target currency
            usd_amount = amount / from_rate
            converted_amount = usd_amount * to_rate
            
            # Calculate exchange rate
            exchange_rate = to_rate / from_rate
            
            return round(converted_amount, 2), round(exchange_rate, 6)
            
        except Exception as e:
            logger.error(f"Currency conversion error: {e}")
            return amount, 1.0
    
    @classmethod
    def process_payment(cls, payment_data: Dict) -> Dict:
        """Process international payment"""
        try:
            payment_method = payment_data.get('payment_method')
            jurisdiction = payment_data.get('jurisdiction', 'LK')
            amount = payment_data.get('amount', 0)
            currency = payment_data.get('currency', 'LKR')
            
            # Validate payment method for jurisdiction
            supported_methods = cls.get_supported_payment_methods(jurisdiction)
            if payment_method not in supported_methods.get('local', []) + supported_methods.get('international', []):
                return {
                    'success': False,
                    'error': f'Payment method {payment_method} not supported in {jurisdiction}'
                }
            
            # Process based on payment method
            if payment_method == 'stripe':
                return cls._process_stripe_payment(payment_data)
            elif payment_method == 'paypal':
                return cls._process_paypal_payment(payment_data)
            elif payment_method == 'lanka_qr':
                return cls._process_lanka_qr_payment(payment_data)
            elif payment_method == 'ez_cash':
                return cls._process_ez_cash_payment(payment_data)
            elif payment_method == 'frimi':
                return cls._process_frimi_payment(payment_data)
            elif payment_method == 'bank_transfer':
                return cls._process_bank_transfer(payment_data)
            elif payment_method == 'crypto':
                return cls._process_crypto_payment(payment_data)
            elif payment_method == 'wise':
                return cls._process_wise_payment(payment_data)
            else:
                return {
                    'success': False,
                    'error': f'Payment method {payment_method} not implemented'
                }
                
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return {
                'success': False,
                'error': f'Payment processing failed: {str(e)}'
            }
    
    @classmethod
    def _process_stripe_payment(cls, payment_data: Dict) -> Dict:
        """Process Stripe payment"""
        try:
            # This would integrate with actual Stripe API
            # For now, we'll simulate the process
            
            amount = payment_data.get('amount', 0)
            currency = payment_data.get('currency', 'USD')
            
            # Simulate Stripe API call
            stripe_response = {
                'id': f'pi_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'status': 'succeeded',
                'amount': int(amount * 100),  # Stripe uses cents
                'currency': currency.lower(),
                'payment_method': payment_data.get('payment_method_id'),
                'created': int(datetime.now().timestamp())
            }
            
            return {
                'success': True,
                'payment_id': stripe_response['id'],
                'status': stripe_response['status'],
                'amount': amount,
                'currency': currency,
                'provider': 'stripe',
                'provider_response': stripe_response
            }
            
        except Exception as e:
            logger.error(f"Stripe payment error: {e}")
            return {
                'success': False,
                'error': f'Stripe payment failed: {str(e)}'
            }
    
    @classmethod
    def _process_paypal_payment(cls, payment_data: Dict) -> Dict:
        """Process PayPal payment"""
        try:
            # This would integrate with actual PayPal API
            amount = payment_data.get('amount', 0)
            currency = payment_data.get('currency', 'USD')
            
            # Simulate PayPal API call
            paypal_response = {
                'id': f'PAYID-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'state': 'approved',
                'amount': {
                    'total': str(amount),
                    'currency': currency
                },
                'create_time': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'payment_id': paypal_response['id'],
                'status': paypal_response['state'],
                'amount': amount,
                'currency': currency,
                'provider': 'paypal',
                'provider_response': paypal_response
            }
            
        except Exception as e:
            logger.error(f"PayPal payment error: {e}")
            return {
                'success': False,
                'error': f'PayPal payment failed: {str(e)}'
            }
    
    @classmethod
    def _process_lanka_qr_payment(cls, payment_data: Dict) -> Dict:
        """Process LankaQR payment"""
        try:
            # This would integrate with actual LankaQR API
            amount = payment_data.get('amount', 0)
            
            # Simulate LankaQR API call
            lanka_qr_response = {
                'transaction_id': f'LQR{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'status': 'success',
                'amount': amount,
                'currency': 'LKR',
                'qr_code': f'data:image/png;base64,{payment_data.get("qr_data", "")}'
            }
            
            return {
                'success': True,
                'payment_id': lanka_qr_response['transaction_id'],
                'status': lanka_qr_response['status'],
                'amount': amount,
                'currency': 'LKR',
                'provider': 'lanka_qr',
                'provider_response': lanka_qr_response
            }
            
        except Exception as e:
            logger.error(f"LankaQR payment error: {e}")
            return {
                'success': False,
                'error': f'LankaQR payment failed: {str(e)}'
            }
    
    @classmethod
    def _process_ez_cash_payment(cls, payment_data: Dict) -> Dict:
        """Process eZ Cash payment"""
        try:
            amount = payment_data.get('amount', 0)
            
            ez_cash_response = {
                'transaction_id': f'EZC{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'status': 'success',
                'amount': amount,
                'currency': 'LKR'
            }
            
            return {
                'success': True,
                'payment_id': ez_cash_response['transaction_id'],
                'status': ez_cash_response['status'],
                'amount': amount,
                'currency': 'LKR',
                'provider': 'ez_cash',
                'provider_response': ez_cash_response
            }
            
        except Exception as e:
            logger.error(f"eZ Cash payment error: {e}")
            return {
                'success': False,
                'error': f'eZ Cash payment failed: {str(e)}'
            }
    
    @classmethod
    def _process_frimi_payment(cls, payment_data: Dict) -> Dict:
        """Process FriMi payment"""
        try:
            amount = payment_data.get('amount', 0)
            
            frimi_response = {
                'transaction_id': f'FRI{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'status': 'success',
                'amount': amount,
                'currency': 'LKR'
            }
            
            return {
                'success': True,
                'payment_id': frimi_response['transaction_id'],
                'status': frimi_response['status'],
                'amount': amount,
                'currency': 'LKR',
                'provider': 'frimi',
                'provider_response': frimi_response
            }
            
        except Exception as e:
            logger.error(f"FriMi payment error: {e}")
            return {
                'success': False,
                'error': f'FriMi payment failed: {str(e)}'
            }
    
    @classmethod
    def _process_bank_transfer(cls, payment_data: Dict) -> Dict:
        """Process bank transfer"""
        try:
            amount = payment_data.get('amount', 0)
            currency = payment_data.get('currency', 'LKR')
            
            bank_response = {
                'transaction_id': f'BANK{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'status': 'pending',
                'amount': amount,
                'currency': currency,
                'bank_reference': f'REF{datetime.now().strftime("%Y%m%d%H%M%S")}'
            }
            
            return {
                'success': True,
                'payment_id': bank_response['transaction_id'],
                'status': bank_response['status'],
                'amount': amount,
                'currency': currency,
                'provider': 'bank_transfer',
                'provider_response': bank_response
            }
            
        except Exception as e:
            logger.error(f"Bank transfer error: {e}")
            return {
                'success': False,
                'error': f'Bank transfer failed: {str(e)}'
            }
    
    @classmethod
    def _process_crypto_payment(cls, payment_data: Dict) -> Dict:
        """Process cryptocurrency payment"""
        try:
            amount = payment_data.get('amount', 0)
            currency = payment_data.get('currency', 'USDT')
            
            crypto_response = {
                'transaction_id': f'CRYPTO{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'status': 'confirmed',
                'amount': amount,
                'currency': currency,
                'blockchain_tx_hash': f'0x{datetime.now().strftime("%Y%m%d%H%M%S")}'
            }
            
            return {
                'success': True,
                'payment_id': crypto_response['transaction_id'],
                'status': crypto_response['status'],
                'amount': amount,
                'currency': currency,
                'provider': 'crypto',
                'provider_response': crypto_response
            }
            
        except Exception as e:
            logger.error(f"Crypto payment error: {e}")
            return {
                'success': False,
                'error': f'Crypto payment failed: {str(e)}'
            }
    
    @classmethod
    def _process_wise_payment(cls, payment_data: Dict) -> Dict:
        """Process Wise (formerly TransferWise) payment"""
        try:
            amount = payment_data.get('amount', 0)
            currency = payment_data.get('currency', 'USD')
            
            wise_response = {
                'transaction_id': f'WISE{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'status': 'completed',
                'amount': amount,
                'currency': currency,
                'exchange_rate': cls.EXCHANGE_RATES.get(currency, 1.0)
            }
            
            return {
                'success': True,
                'payment_id': wise_response['transaction_id'],
                'status': wise_response['status'],
                'amount': amount,
                'currency': currency,
                'provider': 'wise',
                'provider_response': wise_response
            }
            
        except Exception as e:
            logger.error(f"Wise payment error: {e}")
            return {
                'success': False,
                'error': f'Wise payment failed: {str(e)}'
            }
    
    @classmethod
    def get_payment_fees(cls, payment_method: str, amount: float, jurisdiction: str) -> Dict:
        """Get payment processing fees"""
        try:
            # Fee structure by payment method
            fee_structures = {
                'stripe': {
                    'percentage': 2.9,
                    'fixed': 0.30,
                    'currency': 'USD'
                },
                'paypal': {
                    'percentage': 3.4,
                    'fixed': 0.30,
                    'currency': 'USD'
                },
                'lanka_qr': {
                    'percentage': 0.5,
                    'fixed': 0,
                    'currency': 'LKR'
                },
                'ez_cash': {
                    'percentage': 1.0,
                    'fixed': 0,
                    'currency': 'LKR'
                },
                'frimi': {
                    'percentage': 1.0,
                    'fixed': 0,
                    'currency': 'LKR'
                },
                'bank_transfer': {
                    'percentage': 0.1,
                    'fixed': 5.0,
                    'currency': 'LKR'
                },
                'crypto': {
                    'percentage': 0.5,
                    'fixed': 0,
                    'currency': 'USDT'
                },
                'wise': {
                    'percentage': 0.65,
                    'fixed': 0,
                    'currency': 'USD'
                }
            }
            
            fee_structure = fee_structures.get(payment_method, {})
            if not fee_structure:
                return {'error': 'Payment method not supported'}
            
            # Calculate fees
            percentage_fee = amount * (fee_structure['percentage'] / 100)
            fixed_fee = fee_structure['fixed']
            total_fee = percentage_fee + fixed_fee
            
            return {
                'payment_method': payment_method,
                'amount': amount,
                'percentage_fee': percentage_fee,
                'fixed_fee': fixed_fee,
                'total_fee': total_fee,
                'net_amount': amount - total_fee,
                'currency': fee_structure['currency']
            }
            
        except Exception as e:
            logger.error(f"Fee calculation error: {e}")
            return {'error': f'Fee calculation failed: {str(e)}'}
    
    @classmethod
    def validate_payment_data(cls, payment_data: Dict) -> Tuple[bool, List[str]]:
        """Validate payment data before processing"""
        errors = []
        
        required_fields = ['payment_method', 'amount', 'currency', 'user_id']
        for field in required_fields:
            if field not in payment_data or not payment_data[field]:
                errors.append(f'Missing required field: {field}')
        
        # Validate amount
        amount = payment_data.get('amount', 0)
        if amount <= 0:
            errors.append('Amount must be greater than 0')
        
        # Validate currency
        currency = payment_data.get('currency', '')
        if currency not in cls.EXCHANGE_RATES:
            errors.append(f'Unsupported currency: {currency}')
        
        # Validate payment method
        payment_method = payment_data.get('payment_method', '')
        jurisdiction = payment_data.get('jurisdiction', 'LK')
        supported_methods = cls.get_supported_payment_methods(jurisdiction)
        
        if payment_method not in supported_methods.get('local', []) + supported_methods.get('international', []):
            errors.append(f'Payment method {payment_method} not supported in {jurisdiction}')
        
        return len(errors) == 0, errors

