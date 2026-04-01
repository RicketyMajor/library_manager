from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, MovieDirectoryViewSet, MovieWatcherViewSet, MovieWishlistViewSet

router = DefaultRouter()
router.register(r'inventory', MovieViewSet, basename='movie')
router.register(r'directories', MovieDirectoryViewSet,
                basename='movie-directory')
router.register(r'watchers', MovieWatcherViewSet, basename='movie-watcher')
router.register(r'wishlist', MovieWishlistViewSet, basename='movie-wishlist')

urlpatterns = [
    path('', include(router.urls)),
]
