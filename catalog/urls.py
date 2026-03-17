from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_book, name='scan-book'),  # Tu endpoint de la API
    # <-- NUEVA: La página web
    path('scanner/', views.scanner_view, name='scanner-ui'),
]
