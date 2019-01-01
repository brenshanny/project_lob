from graphsite.models import Tank, Reading
from graphsite.serializers import TankSerializer, ReadingSerializer
from rest_framework import generics
from oauth2_provider.views.generic import ProtectedResourceView

class TankList(ProtectedResourceView,
               generics.ListCreateAPIView):
    queryset = Tank.objects.all().order_by('tank_id')
    serializer_class = TankSerializer

class TankDetail(ProtectedResourceView,
                 generics.RetrieveUpdateDestroyAPIView):
    queryset = Tank.objects.all().order_by('tank_id')
    serializer_class = TankSerializer

class ReadingList(ProtectedResourceView,
                  generics.ListCreateAPIView):
    queryset = Reading.objects.all().order_by('timestamp')
    serializer_class = ReadingSerializer

    def get_queryset(self):
        queryset = Reading.objects.all()
        tank_id = self.request.query_params.get("tank_id", None)
        r_type = self.request.query_params.get("reading_type", None)
        sort_by = self.request.query_params.get("sort_by", None)
        if tank_id is not None:
            queryset = queryset.filter(tank=tank_id)
        if r_type is not None:
            queryset = queryset.filter(reading_type=r_type)
        if sort_by is not None:
            queryset = queryset.order_by(sort_by)
        return queryset


class ReadingDetail(ProtectedResourceView,
                    generics.RetrieveUpdateDestroyAPIView):
    queryset = Reading.objects.all().order_by('timestamp')
    serializer_class = ReadingSerializer
