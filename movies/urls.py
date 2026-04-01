from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, MovieDirectoryViewSet

router = DefaultRouter()
router.register(r'inventory', MovieViewSet, basename='movie')
router.register(r'directories', MovieDirectoryViewSet,
                basename='movie-directory')

urlpatterns = [
    path('', include(router.urls)),
]
