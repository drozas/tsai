from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^/vote', 	'ratings.views.vote', ),
	(r'^/get_best_ratings', 	'ratings.views.get_best_ratings', ),
)
