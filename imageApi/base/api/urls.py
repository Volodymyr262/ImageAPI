from django.urls import path
from . import views
from .views import ImageUploadView

urlpatterns = [
    path('', views.getRoutes),
    path('images/', views.getImages, name='images'),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('create/', views.create_temporary_link_view.as_view(), name='create/'),
    path('link/<int:pk>/', views.check_temporary_link, name='link'),
]