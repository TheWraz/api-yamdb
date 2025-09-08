from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, signup, obtain_token


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', signup, name='auth-signup'),
    path('v1/auth/token/', obtain_token, name='auth-token'),
    path('v1/', include(router.urls)),
]

