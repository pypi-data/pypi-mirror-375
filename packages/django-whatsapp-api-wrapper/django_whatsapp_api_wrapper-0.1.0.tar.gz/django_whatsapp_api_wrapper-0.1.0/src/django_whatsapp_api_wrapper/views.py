import json
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def whatsapp_webhook(request: HttpRequest) -> HttpResponse:
    """
    Webhook endpoint for WhatsApp Cloud API.

    - GET: Verification handshake using hub.mode, hub.challenge, hub.verify_token
    - POST: Receive event notifications (messages, status updates, etc.)
    """
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == getattr(settings, "WHATSAPP_VERIFY_TOKEN", None):
            return HttpResponse(challenge or "", status=200)
        return HttpResponse(status=403)

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        # Basic structure check per WhatsApp webhook format
        # { object, entry: [ { changes: [ { field, value: { messaging_product, metadata, ... } } ] } ] }
        # For now, echo 200 OK to acknowledge receipt.
        # You can extend this to process messages, statuses, etc.
        return JsonResponse({"status": "received"}, status=200)

    return HttpResponse(status=405)


