from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('image/<str:pk>', views.getImage),
    path('images/', views.getImages),
]