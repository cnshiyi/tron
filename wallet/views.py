from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Address, ChainTransaction, ListenAddress
from .serializers import AddressSerializer, ChainTransactionSerializer, ListenAddressSerializer
from .services import TronGridService

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filterset_fields = ["address_type", "allocated", "bot_id", "user_id"]
    search_fields = ["address", "username"]

class ChainTransactionViewSet(viewsets.ModelViewSet):
    queryset = ChainTransaction.objects.all()
    serializer_class = ChainTransactionSerializer
    filterset_fields = ["token_type", "confirmed", "to_address", "from_address"]
    search_fields = ["txid", "from_address", "to_address"]

class ListenAddressViewSet(viewsets.ModelViewSet):
    queryset = ListenAddress.objects.all()
    serializer_class = ListenAddressSerializer
    filterset_fields = ["bot_id", "token_type", "enabled"]
    search_fields = ["address", "label"]

class TransactionProbeView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, address: str):
        return Response(TronGridService().account_overview(address))
