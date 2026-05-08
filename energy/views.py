from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import EnergyPlan, EnergyOrder
from .serializers import EnergyPlanSerializer, EnergyOrderSerializer
from .services import SohuEnergyService

class EnergyPlanViewSet(viewsets.ModelViewSet):
    queryset = EnergyPlan.objects.all()
    serializer_class = EnergyPlanSerializer
    filterset_fields = ["bot_id", "mode"]
    search_fields = ["name"]

class EnergyOrderViewSet(viewsets.ModelViewSet):
    queryset = EnergyOrder.objects.all()
    serializer_class = EnergyOrderSerializer
    filterset_fields = ["bot_id", "user_id", "status", "pay_type"]
    search_fields = ["order_no", "receiver_address", "pay_txid", "energy_txid", "platform_order_id"]

class EnergyCallbackView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        return Response(SohuEnergyService().handle_callback(request.data))
