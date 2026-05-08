from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
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
