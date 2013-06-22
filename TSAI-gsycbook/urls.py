from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from gsycbook.profiles.feeds import LatestProfiles
from gsycbook.profiles.friendship import *

from django_restapi.model_resource import Collection
from django_restapi.responder import XMLResponder
from django_restapi.receiver import XMLReceiver

from gsycbook.profiles.models import Profile
from django.contrib.auth.models import User

from django.contrib.auth.views import login, logout


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#urlpatterns = patterns('',
    # Example:
    # (r'^gsycbook/', include('gsycbook.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
#)

# drozas: old configuration
#urlpatterns = patterns('',
#                       (r'^files/(?P<path>.*)$','django.views.static.serve', {'document_root': '/home/drozas/urjc_workspace/gsycbook/templates/transparentia'}),
#                       (r'^profiles/show_profile/(.*)', 'gsycbook.profiles.views.show_profile',),
#                       (r'^profiles/(.*)/delete', 'gsycbook.profiles.views.delete_profile',),
#                       (r'^profiles/show_all_profiles', 'gsycbook.profiles.views.show_all_profiles',),
#                       (r'^profiles/form', 'gsycbook.profiles.views.show_form',),
#                       (r'^profiles/create', 'gsycbook.profiles.views.create_profile',),
#                       (r'^profiles/(.*)/addfriend/$', 'gsycbook.profiles.views.add_friend',),
#)

feeds = {
    'latest': LatestProfiles,
}

profiles_resource = Collection(
    queryset = User.objects.all(),
    permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
    receiver = XMLReceiver(),
    responder = XMLResponder()
)



urlpatterns = patterns('',
                       (r'^files/(?P<path>.*)$','django.views.static.serve', {'document_root': '/home/drozas/urjc_workspace/gsycbook/templates'}),
                       #(r'^files/(?P<path>.*)$','django.views.static.serve', {'document_root': '/home/drozas/urjc_workspace/gsycbook/templates/transparentia'}),
                       #(r'^files/(?P<path>.*)$','django.views.static.serve', {'document_root': '/home/drozas/urjc_workspace/gsycbook/templates/dark_theme'}),
                       (r'^profiles', include('gsycbook.profiles.urls')),
                       (r'^xml/profiles/(.*)', 'gsycbook.profiles.views.show_profile_xml',),
                       (r'^xml/profiles', 'gsycbook.profiles.views.show_all_profiles_xml',),
                       (r'^json/profiles/(.*)', 'gsycbook.profiles.views.show_profile_json',),
                       (r'^json/profiles', 'gsycbook.profiles.views.show_all_profiles_json',),
                       (r'^xml/friends/(.*)', 'gsycbook.profiles.views.show_friends_xml',),
                       #TODO: Ask for redirect_to (to profiles or to show_all_profiles
                       (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/profiles/show_all_profiles'}),
                       (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
                       (r'^rest/profiles/(.*?)/?$', profiles_resource),
                       (r'^rest/friends/(?P<profile_nick>\w+)/(?P<friend_nick>\w+)/', FriendshipEntry(permitted_methods=('GET','DELETE'))),
                       #This one should be only GET, but if i change it i receive a "operation not permitted" error
                       (r'^rest/friends/(?P<profile_nick>\w+)/', FriendshipList(permitted_methods=('GET','DELETE'))),


                       (r'^accounts/login/$',  login),
                       (r'^accounts/logout/$', logout),
                       (r'^admin/(.*)', admin.site.root),
                       #(r'^simpleprotected/', 'gsycbook.profiles.views.simpleprotected'),



)



