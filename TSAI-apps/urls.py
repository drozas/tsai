from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^favcities', include('apps.favcities.urls')),    
)
