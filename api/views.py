from rest_framework import permissions, viewsets, generics, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import django_filters.rest_framework
from django.shortcuts import get_object_or_404
from api.models import User, Post, Comment, Group, Follow
from api.serializers import (
    PostSerializer,
    CommentSerializer,
    FollowSerializer,
    GroupSerializer
)
from api.permissions import IsAuthorOrReadOnlyPermission


class APIPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnlyPermission
    ]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['group']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class APICommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnlyPermission
    ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Comment.objects.filter(post=self.kwargs.get('post_pk'))
        return queryset


class APIGroupViewSet(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class APIFollowViewSet(generics.ListCreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=following__username', '=user__username']

    def perform_create(self, serializer):
        following = get_object_or_404(
            User,
            username=self.request.data.get('following')
        )
        user = self.request.user
        follows = self.queryset.filter(user=user, following=following)
        if follows.exists():
            raise ValidationError(f'У вас уже есть подписка на {following}.')
        if user == following:
            raise ValidationError('Нельзя подписаться на самого себя.')
        serializer.save(user=user, following=following)
