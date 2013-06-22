from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^/profiles/update_cities', 	'favcities.views.update_cities', ),
	(r'^/profiles', 	'favcities.views.get_cities', ),
)
