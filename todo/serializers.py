from django.utils.timezone import localtime
from rest_framework import serializers

from .models import Tag, Category, Todo


class DateTimeTzAwareField(serializers.DateTimeField):
    def to_representation(self, value, *args, **kwargs):
        if value:
            value = localtime(value)
        return super().to_representation(value, *args, **kwargs)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class TodoSerializer(serializers.ModelSerializer):
    deadline = DateTimeTzAwareField()

    class Meta:
        model = Todo
        fields = ('id', 'category', 'tags', 'text', 'is_done', 'deadline')