from rest_framework import routers
from django.urls import include, path, re_path

from api.views import (FollowViewSet,
                       IngredientViewSet,
                       RecipeViewSet,
                       SubscribeViewSet,
                       TagViewSet,
                       UserViewSet)


app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients',
                   IngredientViewSet,
                   basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('users', UserViewSet, basename='users')
# router_v1.register('users/subscriptions',
#                    FollowViewSet,
#                    basename='subscriptions')
# router_v1.register(r'users/(?P<id>\d+)/subscribe',
#                    SubscribeViewSet,
#                    basename='subscribe')

urlpatterns = [
    path('users/subscriptions/', FollowViewSet, name='subscriptions'),
    path('users/<int:user_id>/subscribe/', SubscribeViewSet, name='subscribe'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    re_path('r^auth/', include('djoser.urls.authtoken')),
]
