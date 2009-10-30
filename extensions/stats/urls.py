from django.conf.urls.defaults import *

urlpatterns = patterns('mailng.extensions.stats.main',
                       url(r'^$', 'index', name='fullindex'),
                       url(r'^(?P<dom_id>\d+)/$', 'index', name='domindex'),
                       (r'^display/(?P<dom_id>\d+)/(?P<graph_t>\w+)/$', 'graph_display'),
                       (r'^domain/(?P<dom_id>\d+)/$', 'domain'),
                       )

