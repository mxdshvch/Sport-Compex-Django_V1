from django.urls import path
from . import views

urlpatterns = [
    path('', views.trainers_page, name='trainers_page'),
    path('<int:trainer_id>/', views.trainer_detail, name='trainer_detail'),
    path('slider/', views.trainers_page, name='trainers_page'),
] 