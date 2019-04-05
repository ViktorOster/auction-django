from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('blog.urls'))
    # url('^sw.js', get_static, {
    #    'path': 'agenda/js/serviceworker.js', 'content_type': 'application/javascript'})
]
