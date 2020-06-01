from rest_framework import permissions, viewsets, generics, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import django_filters.rest_framework
from django.shortcuts import get_object_or_404
from api.models import User, Post, Comment, Group, Follow
from api.serializers import PostSerializer, CommentSerializer, FollowSerializer, GroupSerializer
from api.permissions import IsAuthorOrReadOnlyPermission


class APIPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnlyPermission]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['group',]


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


    def perform_destroy(self, serializer):
        serializer.delete()


class APICommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnlyPermission]


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    def list(self, request, post_pk):
        comments = Comment.objects.filter(post=post_pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


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
        following = get_object_or_404(User, username=self.request.data.get('following'))
        user = get_object_or_404(User, username=self.request.user)
        follows = self.queryset.filter(user=user).filter(following=following)
        if follows.exists():
            raise ValidationError(f'У вас уже есть подписка на {following}.')
        if user == following:
            raise ValidationError(f'Нельзя подписаться на самого себя.')
        serializer.save(user=user, following=following)
