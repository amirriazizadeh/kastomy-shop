from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
# from apps.stores.serializers import StoreReadSerializer
from apps.stores.models import Store
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

NOT_FOUND_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Store not found"),
    },
)


class StoresView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Retrieve A Store's Details (GET)",
        operation_description="Retrieve details of a specific store by its primary key (pk), including its items. Access is public (AllowAny).",
        responses={
            # 200: StoreReadSerializer,
            404: openapi.Response(
                description="Store not found",
                schema=NOT_FOUND_RESPONSE
            ),
        },
    )
    def get(self, request, pk):
        try:
            store = Store.objects.get(pk=pk)
            # serializer = StoreReadSerializer(store)
            return Response( status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response(
                {"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND
            )
