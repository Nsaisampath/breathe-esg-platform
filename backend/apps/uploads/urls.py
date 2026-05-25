from django.urls import path
from . import views

urlpatterns = [
    path('sap/', views.upload_sap_data, name='upload-sap'),
    path('utility/', views.upload_utility_data, name='upload-utility'),
    path('travel/', views.upload_travel_data, name='upload-travel'),
]

