from django.utils.timezone import localtime
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Tag, Category, Todo


class DateTimeTzAwareField(serializers.DateTimeField):
    def to_representation(self, value, *args, **kwargs):
        if value:
            value = localtime(value)
        return super().to_representation(value, *args, **kwargs)


class PrimaryKeyRelatedByUser(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return super().get_queryset().filter(user=self.context['request'].user)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class TodoSerializer(serializers.ModelSerializer):
    deadline = DateTimeTzAwareField(required=False, allow_null=True)
    category = PrimaryKeyRelatedByUser(required=False, allow_null=True, queryset=Category.objects.all())
    tags = PrimaryKeyRelatedByUser(required=False, many=True, queryset=Tag.objects.all())

    class Meta:
        model = Todo
        fields = ('id', 'category', 'tags', 'text', 'is_done', 'deadline')