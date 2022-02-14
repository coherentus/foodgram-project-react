from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', ProductViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
]
