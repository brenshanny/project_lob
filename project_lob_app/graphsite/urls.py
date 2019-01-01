from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from graphsite import views

urlpatterns = [
    path('tanks/', views.TankList.as_view()),
    path('tanks/<int:pk>/', views.TankDetail.as_view()),
    path('readings/', views.ReadingList.as_view()),
    path('readings/<int:pk>/', views.ReadingDetail.as_view())
]
