import logging

from rest_framework import views, mixins, generics, permissions, response, status, settings
from django.http import Http404
from django.utils import timezone

from .serializers import CategorySerializer, TagSerializer, TodoSerializer
from .models import Category, Tag, Todo


logger = logging.getLogger(__name__)


class MyGenericApiView(generics.GenericAPIView):
    # Disabling "options" method
    metadata_class = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        timezone.activate(request.user.profile.timezone)

    # Hiding "options" from available methods
    @property
    def allowed_methods(self):
        methods = super().allowed_methods
        methods.remove('OPTIONS')
        return methods


class CategoryList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   MyGenericApiView):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CategoryDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     MyGenericApiView):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TagList(mixins.ListModelMixin,
              mixins.CreateModelMixin,
              MyGenericApiView):
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TagDetail(mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                MyGenericApiView):
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TodoList(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               MyGenericApiView):
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        show = self.request.query_params.get('show')
        category = self.request.query_params.get('category')
        tags = self.request.query_params.getlist('tags')
        due_to = self.request.query_params.get('due_to')

        q = Todo.objects.filter(user=self.request.user)
        if show is not None:
            if show == 'done':
                q = q.filter(is_done=True)
            elif show == 'not_done':
                q = q.filter(is_done=False)

        if category is not None:
            try:
                category = int(category)
            except ValueError:
                pass
            else:
                q = q.filter(category__pk=category)

        if tags:
            try:
                tags = list(map(int, tags))
            except ValueError:
                pass
            else:
                logger.warn('Tags: {0}'.format(tags))
                for t in tags:
                    q = q.filter(tags__pk=t)

        if due_to is not None:
            today = timezone.datetime.combine(timezone.localtime(timezone.now()),
                                              timezone.datetime.max.time())
            today = timezone.make_aware(today)
            if due_to == 'today':
                q = q.filter(deadline__lte=today)
            elif due_to == 'tomorrow':
                today += timezone.timedelta(days=1)
                q = q.filter(deadline__lte=today)
            elif due_to == 'week':
                today += timezone.timedelta(days=7)
                q = q.filter(deadline__lte=today)
            logger.warn(str(today))

        return q.prefetch_related('tags')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TodoDetail(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 MyGenericApiView):
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
