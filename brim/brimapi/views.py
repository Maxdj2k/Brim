import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import rust_ext


@csrf_exempt
@require_POST
def create_user_view(request):
    try:
        payload = json.loads(request.body or "{}")
        username = payload.get("username")
        password = payload.get("password")

        if not username or not password:
            return JsonResponse({"error": "username and password are required"}, status=400)

        user_json = rust_ext.create_user(username, password)
        return JsonResponse(json.loads(user_json), status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid JSON body"}, status=400)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


def admin_users_view(request):
    return render(request, "brimapi/admin_users.html")
