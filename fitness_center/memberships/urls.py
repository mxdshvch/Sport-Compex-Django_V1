from django.urls import path
from . import views

urlpatterns = [
    path('', views.memberships_list, name='memberships_list'),
    path('apply/', views.apply_for_membership, name='apply_for_membership'),
    path('apply/<int:membership_id>/', views.apply_for_membership, name='apply_for_specific_membership'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('admin/applications/', views.admin_applications_list, name='admin_applications_list'),
    path('admin/applications/<int:application_id>/', views.admin_application_update, name='admin_application_update'),
    path('admin/applications/search/', views.admin_application_search, name='admin_application_search'),
    path('admin/applications/update-status/<int:application_id>/', views.admin_application_update_status, name='admin_application_update_status'),
    path('submit-membership-application/', views.submit_membership_application, name='submit_membership_application'),
] 