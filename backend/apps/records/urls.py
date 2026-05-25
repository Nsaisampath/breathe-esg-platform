from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_records, name='list-records'),
    path('summary/', views.get_summary, name='summary'),
    path('<int:record_id>/', views.record_detail, name='record-detail'),
    path('<int:record_id>/approve/', views.approve_record, name='approve-record'),
]

