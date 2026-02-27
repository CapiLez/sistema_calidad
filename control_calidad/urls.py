from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('avance-obra/', views.avance_obra, name='avance_obra'),
    path('indicadores/', views.indicadores, name='indicadores'),
]
