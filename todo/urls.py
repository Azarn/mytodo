from django.conf.urls import url
from .views import CategoryList, CategoryDetail, TagList, TagDetail, TodoList, TodoDetail

urlpatterns = [
    url(r'^category/$', CategoryList.as_view(), name='category-list'),
    url(r'^category/(?P<pk>[0-9]+)/$', CategoryDetail.as_view(), name='category-detail'),
    url(r'^tag/$', TagList.as_view()),
    url(r'^tag/(?P<pk>[0-9]+)/$', TagDetail.as_view()),
    url(r'^todo/$', TodoList.as_view()),
    url(r'^todo/(?P<pk>[0-9]+)/$', TodoDetail.as_view()),
]
