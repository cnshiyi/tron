from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    google_code = request.data.get("google_code") or request.data.get("googleCode")

    if (
        username != settings.DEV_LOGIN_USERNAME
        or password != settings.DEV_LOGIN_PASSWORD
        or google_code != settings.DEV_LOGIN_GOOGLE_CODE
    ):
        return Response({"code": 401, "data": None, "message": "账号、密码或 Google 验证码错误"}, status=401)

    return Response({"code": 0, "data": {"accessToken": "dev-token"}, "message": "ok"})


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh(request):
    return Response({"data": "dev-token", "status": 0})


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    return Response({"code": 0, "data": True, "message": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def codes(request):
    return Response({"code": 0, "data": ["AC_100100", "AC_100110", "AC_100120"], "message": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def user_info(request):
    return Response({
        "code": 0,
        "data": {
            "userId": "1",
            "username": "admin",
            "realName": "TRON管理员",
            "avatar": "",
            "desc": "TRON energy bot admin",
            "homePath": "/tron/dashboard",
            "roles": ["super"],
        },
        "message": "ok",
    })
