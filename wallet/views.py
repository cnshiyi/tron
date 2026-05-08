from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Address
from .serializers import AddressSerializer
from .services import TronGridService

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filterset_fields = ["address_type", "allocated", "bot_id", "user_id"]
    search_fields = ["address", "username"]

class TransactionProbeView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, address: str):
        return Response(TronGridService().account_overview(address))
