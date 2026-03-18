from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Creamos el enrutador y registramos nuestras nuevas vistas automáticas
router = DefaultRouter()
router.register(r'library', views.BookViewSet, basename='library')
router.register(r'watchers-crud', views.WatcherViewSet,
                basename='watcher-crud')
router.register(r'wishlist-crud', views.WishlistItemViewSet,
                basename='wishlist-crud')
router.register(r'friends', views.FriendViewSet, basename='friends')
router.register(r'loans', views.LoanViewSet, basename='loans')

urlpatterns = [
    # Tus endpoints antiguos siguen funcionando intactos
    path('scan/', views.scan_book, name='scan-book'),
    path('scanner/', views.scanner_view, name='scanner-ui'),
    path('watchers/', views.get_active_watchers, name='watchers-list'),
    path('wishlist/add/', views.add_wishlist_item, name='wishlist-add'),

    # Inyectamos todas las rutas automáticas generadas por el router
    path('', include(router.urls)),
]
