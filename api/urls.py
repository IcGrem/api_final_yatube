from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    APIPostViewSet,
    APICommentViewSet,
    APIGroupViewSet,
    APIFollowViewSet
)


router = DefaultRouter()
router.register('posts', APIPostViewSet)
router.register(
    r'posts/(?P<post_pk>\d+)/comments',
    APICommentViewSet, basename='comments'
)


urlpatterns = [
    path('', include(router.urls)),
    path('group/', APIGroupViewSet.as_view()),
    path('follow/', APIFollowViewSet.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
