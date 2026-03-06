from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class SittersAPIView(APIView):
    # input_serializer_class = SittersPaginatedSerialzer
    # query_serializer_class = SittersQueryParametersSerializer
    def get(self, request):
        return Response(status=status.HTTP_200_OK)