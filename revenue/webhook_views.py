import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .ott_integration import OTTIntegrationService
from .models import OTTPlatformIntegration, RevenueWebhook

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class OTTWebhookView(View):
    """Generic OTT platform webhook handler"""
    
    def post(self, request, platform_name):
        """Handle OTT platform webhook"""
        try:
            # Get platform configuration
            try:
                platform = OTTPlatformIntegration.objects.get(
                    name=platform_name,
                    is_active=True
                )
            except OTTPlatformIntegration.DoesNotExist:
                logger.error(f"Platform not found or inactive: {platform_name}")
                return JsonResponse(
                    {'error': 'Platform not found'}, 
                    status=404
                )
            
            # Parse request body
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON payload from {platform_name}")
                return JsonResponse(
                    {'error': 'Invalid JSON payload'}, 
                    status=400
                )
            
            # Verify webhook signature if configured
            if not self._verify_webhook_signature(request, platform, payload):
                logger.error(f"Invalid webhook signature from {platform_name}")
                return JsonResponse(
                    {'error': 'Invalid signature'}, 
                    status=401
                )
            
            # Process webhook
            ott_service = OTTIntegrationService()
            success = ott_service.process_webhook(platform_name, payload)
            
            if success:
                logger.info(f"Webhook processed successfully for {platform_name}")
                return JsonResponse({'status': 'success'})
            else:
                logger.error(f"Failed to process webhook for {platform_name}")
                return JsonResponse(
                    {'error': 'Failed to process webhook'}, 
                    status=500
                )
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return JsonResponse(
                {'error': 'Internal server error'}, 
                status=500
            )
    
    def _verify_webhook_signature(self, request, platform, payload):
        """Verify webhook signature"""
        # This is a simplified verification
        # In production, you would implement proper signature verification
        # based on the platform's webhook security requirements
        
        signature = request.headers.get('X-Webhook-Signature')
        if not signature:
            # For now, allow webhooks without signature verification
            return True
        
        # TODO: Implement proper signature verification
        # This would involve:
        # 1. Getting the webhook secret from platform configuration
        # 2. Computing the expected signature using HMAC
        # 3. Comparing with the provided signature
        
        return True


@method_decorator(csrf_exempt, name='dispatch')
class NetflixWebhookView(View):
    """Netflix-specific webhook handler"""
    
    def post(self, request):
        """Handle Netflix webhook"""
        return OTTWebhookView().post(request, 'netflix')


@method_decorator(csrf_exempt, name='dispatch')
class AmazonPrimeWebhookView(View):
    """Amazon Prime-specific webhook handler"""
    
    def post(self, request):
        """Handle Amazon Prime webhook"""
        return OTTWebhookView().post(request, 'amazon_prime')


@method_decorator(csrf_exempt, name='dispatch')
class DisneyPlusWebhookView(View):
    """Disney+ specific webhook handler"""
    
    def post(self, request):
        """Handle Disney+ webhook"""
        return OTTWebhookView().post(request, 'disney_plus')


@method_decorator(csrf_exempt, name='dispatch')
class GenericOTTWebhookView(View):
    """Generic OTT platform webhook handler"""
    
    def post(self, request, platform_name):
        """Handle generic OTT webhook"""
        return OTTWebhookView().post(request, platform_name)


@require_http_methods(["GET"])
def webhook_status(request, webhook_id):
    """Get webhook processing status"""
    try:
        webhook = RevenueWebhook.objects.get(id=webhook_id)
        
        return JsonResponse({
            'id': webhook.id,
            'platform': webhook.platform.name,
            'campaign': webhook.campaign.title,
            'status': webhook.status,
            'response_code': webhook.response_code,
            'response_message': webhook.response_message,
            'processed_at': webhook.processed_at.isoformat() if webhook.processed_at else None,
            'created_at': webhook.created_at.isoformat()
        })
        
    except RevenueWebhook.DoesNotExist:
        return JsonResponse(
            {'error': 'Webhook not found'}, 
            status=404
        )
    except Exception as e:
        logger.error(f"Error getting webhook status: {e}")
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )


@require_http_methods(["POST"])
def test_webhook(request, platform_name):
    """Test webhook endpoint for development"""
    try:
        # Create test payload
        test_payload = {
            'campaign_id': 1,
            'revenue_data': {
                'entries': [
                    {
                        'amount': 1000.00,
                        'currency': 'USDT',
                        'title': 'Test Revenue Entry',
                        'date': '2024-01-01T00:00:00Z'
                    }
                ]
            }
        }
        
        # Process test webhook
        ott_service = OTTIntegrationService()
        success = ott_service.process_webhook(platform_name, test_payload)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': f'Test webhook processed for {platform_name}',
                'payload': test_payload
            })
        else:
            return JsonResponse(
                {'error': 'Failed to process test webhook'}, 
                status=500
            )
            
    except Exception as e:
        logger.error(f"Error processing test webhook: {e}")
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )


@require_http_methods(["GET"])
def platform_integrations(request):
    """Get list of active OTT platform integrations"""
    try:
        platforms = OTTPlatformIntegration.objects.filter(is_active=True)
        
        integrations = []
        for platform in platforms:
            integrations.append({
                'id': platform.id,
                'name': platform.name,
                'platform_type': platform.platform_type,
                'api_endpoint': platform.api_endpoint,
                'webhook_url': platform.webhook_url,
                'is_active': platform.is_active,
                'created_at': platform.created_at.isoformat()
            })
        
        return JsonResponse({
            'integrations': integrations,
            'count': len(integrations)
        })
        
    except Exception as e:
        logger.error(f"Error getting platform integrations: {e}")
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )