from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
import hmac
import hashlib
from django.conf import settings
from .ott_integration import OTTIntegrationService, BoxOfficeIntegrationService
from .models import OTTPlatformIntegration

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class OTTWebhookView(View):
    """Generic OTT platform webhook handler"""
    
    def post(self, request, platform_id):
        try:
            # Get platform
            platform = OTTPlatformIntegration.objects.get(id=platform_id, is_active=True)
            
            # Verify webhook signature if configured
            if not self._verify_webhook_signature(request, platform):
                return JsonResponse({'error': 'Invalid signature'}, status=401)
            
            # Parse payload
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
            
            # Process webhook
            integration_service = OTTIntegrationService()
            success = integration_service.process_webhook(platform_id, payload)
            
            if success:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'Failed to process webhook'}, status=500)
                
        except OTTPlatformIntegration.DoesNotExist:
            return JsonResponse({'error': 'Platform not found'}, status=404)
        except Exception as e:
            logger.error(f"Error processing OTT webhook: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _verify_webhook_signature(self, request, platform):
        """Verify webhook signature"""
        # This is a simplified implementation
        # In production, you would verify the signature based on the platform's requirements
        signature = request.headers.get('X-Webhook-Signature')
        if not signature:
            return False
        
        # For now, we'll just check if the signature exists
        # In production, you would verify it against the platform's secret
        return True


@method_decorator(csrf_exempt, name='dispatch')
class NetflixWebhookView(View):
    """Netflix-specific webhook handler"""
    
    def post(self, request):
        try:
            # Get Netflix platform
            platform = OTTPlatformIntegration.objects.get(
                platform_type='netflix',
                is_active=True
            )
            
            # Verify webhook signature
            if not self._verify_netflix_signature(request):
                return JsonResponse({'error': 'Invalid signature'}, status=401)
            
            # Parse payload
            payload = json.loads(request.body)
            
            # Process webhook
            integration_service = OTTIntegrationService()
            success = integration_service.process_webhook(platform.id, payload)
            
            if success:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'Failed to process webhook'}, status=500)
                
        except OTTPlatformIntegration.DoesNotExist:
            return JsonResponse({'error': 'Netflix integration not configured'}, status=404)
        except Exception as e:
            logger.error(f"Error processing Netflix webhook: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _verify_netflix_signature(self, request):
        """Verify Netflix webhook signature"""
        # Netflix webhook signature verification would go here
        # This is a placeholder implementation
        signature = request.headers.get('X-Netflix-Signature')
        return signature is not None


@method_decorator(csrf_exempt, name='dispatch')
class AmazonPrimeWebhookView(View):
    """Amazon Prime Video webhook handler"""
    
    def post(self, request):
        try:
            # Get Amazon Prime platform
            platform = OTTPlatformIntegration.objects.get(
                platform_type='amazon_prime',
                is_active=True
            )
            
            # Verify webhook signature
            if not self._verify_amazon_signature(request):
                return JsonResponse({'error': 'Invalid signature'}, status=401)
            
            # Parse payload
            payload = json.loads(request.body)
            
            # Process webhook
            integration_service = OTTIntegrationService()
            success = integration_service.process_webhook(platform.id, payload)
            
            if success:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'Failed to process webhook'}, status=500)
                
        except OTTPlatformIntegration.DoesNotExist:
            return JsonResponse({'error': 'Amazon Prime integration not configured'}, status=404)
        except Exception as e:
            logger.error(f"Error processing Amazon Prime webhook: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _verify_amazon_signature(self, request):
        """Verify Amazon Prime webhook signature"""
        # Amazon Prime webhook signature verification would go here
        signature = request.headers.get('X-Amazon-Signature')
        return signature is not None


@method_decorator(csrf_exempt, name='dispatch')
class DisneyPlusWebhookView(View):
    """Disney+ webhook handler"""
    
    def post(self, request):
        try:
            # Get Disney+ platform
            platform = OTTPlatformIntegration.objects.get(
                platform_type='disney_plus',
                is_active=True
            )
            
            # Verify webhook signature
            if not self._verify_disney_signature(request):
                return JsonResponse({'error': 'Invalid signature'}, status=401)
            
            # Parse payload
            payload = json.loads(request.body)
            
            # Process webhook
            integration_service = OTTIntegrationService()
            success = integration_service.process_webhook(platform.id, payload)
            
            if success:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'Failed to process webhook'}, status=500)
                
        except OTTPlatformIntegration.DoesNotExist:
            return JsonResponse({'error': 'Disney+ integration not configured'}, status=404)
        except Exception as e:
            logger.error(f"Error processing Disney+ webhook: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _verify_disney_signature(self, request):
        """Verify Disney+ webhook signature"""
        # Disney+ webhook signature verification would go here
        signature = request.headers.get('X-Disney-Signature')
        return signature is not None


@method_decorator(csrf_exempt, name='dispatch')
class BoxOfficeWebhookView(View):
    """Box office revenue webhook handler"""
    
    def post(self, request):
        try:
            # Verify webhook signature
            if not self._verify_box_office_signature(request):
                return JsonResponse({'error': 'Invalid signature'}, status=401)
            
            # Parse payload
            payload = json.loads(request.body)
            
            # Extract data
            campaign_id = payload.get('campaign_id')
            amount = payload.get('amount')
            currency = payload.get('currency', 'USDT')
            description = payload.get('description', 'Box office revenue')
            revenue_date = payload.get('revenue_date')
            
            if not campaign_id or not amount:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Record box office revenue
            integration_service = BoxOfficeIntegrationService()
            revenue_entry = integration_service.record_box_office_revenue(
                campaign_id=campaign_id,
                amount=amount,
                currency=currency,
                description=description,
                revenue_date=revenue_date
            )
            
            return JsonResponse({
                'status': 'success',
                'revenue_entry_id': revenue_entry.id
            })
                
        except Exception as e:
            logger.error(f"Error processing box office webhook: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _verify_box_office_signature(self, request):
        """Verify box office webhook signature"""
        # Box office webhook signature verification would go here
        signature = request.headers.get('X-BoxOffice-Signature')
        return signature is not None


# Health check endpoint
@require_http_methods(["GET"])
def webhook_health_check(request):
    """Health check for webhook endpoints"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'endpoints': [
            'netflix-webhook',
            'amazon-prime-webhook',
            'disney-plus-webhook',
            'box-office-webhook'
        ]
    })
