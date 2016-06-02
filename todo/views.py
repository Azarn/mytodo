import logging

from rest_framework import mixins, generics, permissions, exceptions
from django.conf import settings
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

    @staticmethod
    def _raise_invalid_param(param_name):
        raise exceptions.ParseError('parameter `{0}` is invalid'.format(param_name))

    def parse_get_int(self, param_name, default=None):
        param = self.request.query_params.get(param_name, default)
        if param != default:
            try:
                param = int(param)
            except ValueError:
                self._raise_invalid_param(param_name)
        return param

    def parse_get_bool(self, param_name, default=None):
        param = self.parse_get_int(param_name, default)
        if param != default:
            if param not in (0, 1):
                self._raise_invalid_param(param_name)
            param = bool(param)
        return param

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
        return self.update(request, *args, partial=True, **kwargs)

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
        return self.update(request, *args, partial=True, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TodoList(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               MyGenericApiView):
    serializer_class = TodoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        Gets query according to GET params

        Available GET params:
        only_done: if specified, todos will be filtered by `todo.is_done` = only_done
        category: if specified todos will be filtered by this category
        tags: if specified todos will be filtered by this tags list
        only_one_day: if specified changes behaviour of by_date(see below) to show todos only for one day
        by_date: if specified todos will be filtered by this date,
        if it is equal to `None`, filters todos without deadline
        :return: queryset
        """
        q = Todo.objects.filter(user=self.request.user)
        only_done = self.parse_get_bool('only_done')
        only_one_day = self.parse_get_bool('only_one_day', False)
        category = self.request.query_params.get('category')
        tags = self.request.query_params.getlist('tags')
        by_date = self.request.query_params.get('by_date')

        if only_done is not None:
            if only_done:
                q = q.filter(is_done=True)
            else:
                q = q.filter(is_done=False)

        if category is not None:
            try:
                category = int(category)
            except ValueError:
                raise exceptions.ParseError('parameter `category` is invalid')
            else:
                q = q.filter(category__pk=category)

        if tags:
            try:
                tags = list(map(int, tags))
            except ValueError:
                raise exceptions.ParseError('parameter `tags` is invalid')
            else:
                for t in tags:
                    q = q.filter(tags__pk=t)

        if by_date is not None:
            if by_date in ('today', 'tomorrow', 'week', 'none'):
                date = timezone.localtime(timezone.now())
            else:
                try:
                    date = timezone.datetime.strptime(by_date, settings.DATE_FORMAT)
                except TypeError:
                    raise exceptions.ParseError('parameter `by_date` is invalid')
            date = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))

            if by_date == 'tomorrow':
                date += timezone.timedelta(days=1)
            elif by_date == 'week':
                date += timezone.timedelta(days=6)
            logger.warn(str(date))

            if by_date == 'none':
                q = q.filter(deadline__isnull=True)
            elif only_one_day:
                q = q.filter(deadline__date=date)
            else:
                q = q.filter(deadline__lte=date)

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
        return self.update(request, *args, partial=True, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
