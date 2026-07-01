from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('directions/', views.directions_list, name='directions_list'),
    path('directions/<int:direction_id>/', views.direction_detail, name='direction_detail'),
    path('schedule/', views.schedule, name='schedule'),
    path('book/<int:workout_id>/', views.book_workout, name='book_workout'),
    path('cancel/<int:workout_id>/', views.cancel_booking, name='cancel_booking'),
    path('submit-application/', views.submit_application, name='submit_application'),
    path('trainers-carousel/', views.trainers_carousel, name='trainers_carousel'),
] 