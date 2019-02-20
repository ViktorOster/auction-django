from django.conf.urls import url, include
from . import views, apiview
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from rest_framework import routers, serializers, viewsets
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.models import User
#import django_cron
# django_cron.autodiscover()

# Serializers define the API representation.


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    #url(r'^api/search/$', include(router.urls)),
    url(r'^api/browse/$', apiview.postList.as_view()),
    url(r'^api/search/(?P<field_name>\w+)/$', apiview.postSearch.as_view()),
    url(r'^$', views.post_list, name='post_list'),
    url(r'^post/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^save_post/$', views.save_post, name='save_post'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', LoginView.as_view(),
        {'template_name': 'blog/login.html'}, name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^edit_user/$', views.edit_user, name='edit_user'),
    url(r'^post/(?P<pk>\d+)/make_bid/$', views.make_bid, name='make_bid'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
