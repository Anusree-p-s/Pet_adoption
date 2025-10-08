from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Pet pages
    path('explore/', views.expanded_home, name='expanded_home'),
    path('my-pets/', views.my_pets, name='my_pets'),
    path('pet/<int:pet_id>/', views.pet_details, name='pet_details'),
    path('add-pet/', views.add_pet, name='add_pet'),
    path('edit-pet/<int:pet_id>/', views.edit_pet, name='edit_pet'),
    path('delete-pet/<int:pet_id>/', views.delete_pet, name='delete_pet'),

    # Adoption
    path('adopt/<int:pet_id>/', views.adopt_pet, name='adopt_pet'),
    path('adoption-info/', views.adoption_info, name='adoption_info'),
    path('my-requests/', views.my_requests, name='my_requests'),

    # Admin adoption requests
    path('owner-requests/', views.owner_requests, name='owner_requests'),
    path('update-request/<int:request_id>/<str:status>/', views.update_request, name='update_request'),
    path('my-adopted-pets/', views.my_adopted_pets, name='my_adopted_pets'),
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    path('my-adopted-pets/', views.my_adopted_pets, name='my_adopted_pets'),

]








