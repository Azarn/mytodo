from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from .models import Category, Todo, Profile
from .views import CategoryDetail, CategoryList, TagDetail, TagList, TodoDetail, TodoList


class DefaultCategoryTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='user')

    def _check_exists(self):
        return Category.objects.filter(user=self.user, name=Category.DEFAULT_NAME).exists()

    def test_default_category_getting(self):
        self.assertIsNone(Category.get_default_category(self.user))
        category = Category.get_or_create_default(self.user)
        self.assertEqual(category, Category.get_default_category(self.user))
        Category.delete_default_if_empty(self.user)
        self.assertIsNone(Category.get_default_category(self.user))

    def test_default_category_creation_deletion(self):
        self.assertFalse(self._check_exists())
        Category.get_or_create_default(self.user)
        self.assertTrue(self._check_exists())
        Category.delete_default_if_empty(self.user)
        self.assertFalse(self._check_exists())

    def test_todo_empty_category(self):
        todo = Todo.objects.create(user=self.user, text='Test todo', deadline=timezone.now())
        self.assertEqual(todo.category, Category.objects.get(user=self.user, name=Category.DEFAULT_NAME))

        test_category = Category.objects.create(user=self.user, name='Test category')
        todo.category = test_category
        todo.save()
        self.assertFalse(self._check_exists())

        todo.reset_category()
        self.assertTrue(self._check_exists())

        todo.category = test_category
        todo.save()
        self.assertFalse(self._check_exists())
        test_category.delete()
        self.assertTrue(self._check_exists())
        todo = Todo.objects.get(pk=todo.pk)
        self.assertEqual(todo.category, Category.get_default_category(todo.user))

        todo.delete()
        self.assertFalse(self._check_exists())


class ApiUserRestrictionCategoryListTestCase(TestCase):
    def setUp(self):
        self.my_user = get_user_model().objects.create(username='my_user')
        Profile(user=self.my_user).save()
        self.other_user = get_user_model().objects.create(username='other_user')
        Profile(user=self.other_user).save()
        self.my_category = Category.objects.create(user=self.my_user, name='Test my category')
        self.other_category = Category.objects.create(user=self.other_user, name='Test my category')
        self.factory = APIRequestFactory()
        self.url = reverse('todo:category-list')
        self.view = CategoryList.as_view()

    def test_category_list_methods_not_authenticated(self):
        request = self.factory.get(self.url, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        request = self.factory.post(self.url, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_list_get(self):
        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.my_user, self.my_user.auth_token)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'], [{'id': self.my_category.id, 'name': self.my_category.name}])

    def test_category_list_create(self):
        data = {'name': 'New category', 'id': 100, 'user': self.other_user.id}
        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, self.my_user, self.my_user.auth_token)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.all().count(), 3)
        new_category = Category.objects.get(pk=response.data['id'])
        self.assertNotEqual(new_category.id, data['id'])
        self.assertNotEqual(new_category.user_id, self.other_user.id)
        self.assertEqual(new_category.name, data['name'])
        self.assertEqual(response.data, {'id': new_category.id, 'name': data['name']})


class ApiUserRestrictionCategoryDetailTestCase(TestCase):
    def setUp(self):
        self.my_user = get_user_model().objects.create(username='my_user')
        Profile(user=self.my_user).save()
        self.other_user = get_user_model().objects.create(username='other_user')
        Profile(user=self.other_user).save()
        self.my_category = Category.objects.create(user=self.my_user, name='Test my category')
        self.other_category = Category.objects.create(user=self.other_user, name='Test my category')
        self.factory = APIRequestFactory()
        self.view = CategoryDetail.as_view()
        self.urls = [reverse('todo:category-detail', args=(self.my_category.id,)),
                     reverse('todo:category-detail', args=(self.other_category.id,))]

    def test_category_detail_methods_not_authenticated(self):
        for url in self.urls:
            request = self.factory.get(url, format='json')
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            request = self.factory.put(url, format='json')
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            request = self.factory.delete(url, format='json')
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_detail_get(self):
        request = self.factory.get(self.urls[0], format='json')
        force_authenticate(request, self.my_user, self.my_user.auth_token)
        response = self.view(request, pk=self.my_category.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': self.my_category.id, 'name': self.my_category.name})
        request = self.factory.get(self.urls[1], format='json')
        force_authenticate(request, self.my_user, self.my_user.auth_token)
        response = self.view(request, pk=self.other_category.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_detail_put(self):
        data = {'id': 100, 'user': 100, 'name': "New category name"}
        request = self.factory.put(self.urls[0], data, format='json')
        force_authenticate(request, self.my_user, self.my_user.auth_token)
        response = self.view(request, pk=self.my_category.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': self.my_category.id, 'name': data['name']})
        self.my_category = Category.objects.get(id=self.my_category.id)
        self.assertEqual(self.my_category.name, data['name'])
        self.assertEqual(self.my_category.user.id, self.my_user.id)
        request = self.factory.put(self.urls[1], data, format='json')
        force_authenticate(request, self.my_user, self.my_user.auth_token)
        response = self.view(request, pk=self.other_category.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_category = Category.objects.get(id=self.other_category.id)
        self.assertNotEqual(self.other_category.name, data['name'])
        self.assertEqual(self.other_category.user.id, self.other_user.id)