from django.urls import path
from . import views
from .views import ImageUploadView
urlpatterns = [
    path('', views.getRoutes),
    path('image/<str:pk>', views.getImage),
    path('images/', views.getImages),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
]