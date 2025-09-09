# django-whatsapp-api-wrapper

Um wrapper simples para enviar mensagens via WhatsApp Cloud API e expor um endpoint de webhook, pronto para integrar em qualquer projeto Django.

## Instalação

```bash
python -m pip install django-whatsapp-api-wrapper
```

## Configuração (Django)

1) Adicione o app em `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_whatsapp_api_wrapper",
]
```

2) Inclua as URLs no `urls.py` principal:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("whatsapp-api-wrapper/", include("django_whatsapp_api_wrapper.urls")),
]
```

3) Defina as variáveis de ambiente (ou no seu `.env`):

```bash
TOKEN=
PACKAGE_VERSION=0.1.1
API_VERSION=v23.0
PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
```

O endpoint de webhook ficará disponível em:

- GET/POST: `/whatsapp-api-wrapper/webhook/`
- Verificação (GET): `/whatsapp-api-wrapper/webhook/?hub.mode=subscribe&hub.verify_token=<TOKEN>&hub.challenge=123`

## Extensibilidade do Webhook

Você pode customizar o processamento do webhook no projeto hospedeiro de duas formas:

- Via setting com handler plugável:

```python
# settings.py
WHATSAPP_WEBHOOK_HANDLER = "meuapp.whatsapp.handle_webhook"
```

```python
# meuapp/whatsapp.py
from django.http import JsonResponse

def handle_webhook(request, payload):
    # sua lógica aqui (salvar eventos, acionar tasks, etc)
    return JsonResponse({"ok": True})
```

- Via signal `webhook_event_received`:

```python
from django.dispatch import receiver
from django_whatsapp_api_wrapper.signals import webhook_event_received

@receiver(webhook_event_received)
def on_whatsapp_event(sender, payload, request, **kwargs):
    # sua lógica aqui
    pass
```

## Uso Rápido (envio de mensagens)

```python
from django_whatsapp_api_wrapper import WhatsApp

wp = WhatsApp()

# Template
language = {"code": "pt_BR"}
template = {"name": "opa", "language": language}
m = wp.build_message(to="5521980340830", type="template", data=template)
m.send()

# Texto
data = {"preview_url": False, "body": "será que só funciona?"}
m2 = wp.build_message(to="+5521994740431", type="text", data=data)
m2.send()
```

## Notas

- Nome do pacote no PyPI: `django-whatsapp-api-wrapper`
- Nome do módulo/import: `django_whatsapp_api_wrapper`