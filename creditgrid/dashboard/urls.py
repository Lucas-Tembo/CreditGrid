from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard, name="dashboard"),
    path('transactions', views.transactions, name= "transactions"),
    path('analytics', views.analytics, name="analytics"),
    path('borrower_detail/<int:pk>/', views.borrower_detail, name='borrower_detail'),
    path('mark_as_paid/<int:pk>/', views.mark_as_paid, name="mark_as_paid"),
    path('delete_borrower/<int:pk>/', views.delete_borrower, name='delete_borrower'),
    path('transaction_history_view/', views.transaction_history_view, name='transaction_history'),
    path('transaction-history/pdf/', views.download_transactions_pdf, name='download_transactions_pdf'),
]