from django.conf.urls import url
from .views import CategoryList, CategoryDetail, TagList, TagDetail, TodoList, TodoDetail

urlpatterns = [
    url(r'^categories/$', CategoryList.as_view()),
    url(r'^categories/(?P<pk>[0-9]+)/$', CategoryDetail.as_view()),
    url(r'^tags/$', TagList.as_view()),
    url(r'^tags/(?P<pk>[0-9]+)/$', TagDetail.as_view()),
    url(r'^todo/$', TodoList.as_view()),
    url(r'^todo/(?P<pk>[0-9]+)/$', TodoDetail.as_view()),
]
