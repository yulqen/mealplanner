import json

from django.contrib.messages import get_messages


class HtmxMessageMiddleware:
    """Attach Django messages to HTMX responses via HX-Trigger headers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.headers.get("HX-Request") and request.method != "GET":
            messages = list(get_messages(request))
            if messages:
                trigger_payload = self._build_payload(messages)
                triggers = self._merge_triggers(response.headers.get("HX-Trigger"), trigger_payload)
                response.headers["HX-Trigger"] = json.dumps(triggers)

        return response

    def _build_payload(self, messages):
        payload = [
            {
                "message": message.message,
                "type": self._normalize_type(message.tags or message.level_tag),
            }
            for message in messages
        ]
        return {"showToast": payload}

    def _merge_triggers(self, existing_header, payload):
        if not existing_header:
            return payload

        try:
            existing = json.loads(existing_header)
        except json.JSONDecodeError:
            return payload

        show_toast = payload.get("showToast")
        if show_toast:
            existing_show = existing.get("showToast")
            if existing_show:
                combined = []
                if isinstance(existing_show, list):
                    combined.extend(existing_show)
                else:
                    combined.append(existing_show)
                combined.extend(show_toast)
                existing["showToast"] = combined
            else:
                existing["showToast"] = show_toast

        return existing

    def _normalize_type(self, message_type):
        value = (message_type or "").lower()
        if "error" in value:
            return "error"
        if "warning" in value:
            return "warning"
        if "success" in value:
            return "success"
        if "info" in value:
            return "info"
        return "info"
