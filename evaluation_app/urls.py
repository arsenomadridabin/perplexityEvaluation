from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('matching/', views.matching, name='matching'),
    path('evaluation/', views.evaluation, name='evaluation'),
    path('statistics/', views.statistics, name='statistics'),
    path('export/', views.export_results, name='export_results'),
    path('api/create-pair/', views.create_pair, name='create_pair'),
    path('api/delete-pair/', views.delete_pair, name='delete_pair'),
    path('api/delete-entry/', views.delete_entry, name='delete_entry'),
    path('api/mark-no-match/', views.mark_no_match, name='mark_no_match'),
    path('api/clear-all-data/', views.clear_all_data, name='clear_all_data'),
    path('api/save-classification/', views.save_classification, name='save_classification'),
] 