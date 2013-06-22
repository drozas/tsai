from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#urlpatterns = patterns('',
    # Example:
    # (r'^gsycbook/', include('gsycbook.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
#)

urlpatterns = patterns('',
                       #('/', 'gsycbook.profiles.views.show_all_profiles',),
                       ('/show_profile/(.*)', 'gsycbook.profiles.views.show_profile',),
                       ('/(.*)/delete', 'gsycbook.profiles.views.delete_friendship',),
                       ('/show_all_profiles', 'gsycbook.profiles.views.show_all_profiles',),
                       ('/form', 'gsycbook.profiles.views.show_form',),
                       ('/create', 'gsycbook.profiles.views.create_profile',),
                       ('/(.*)/addfriend/$', 'gsycbook.profiles.views.add_friend',),
                       ('/associate_application/$', 'gsycbook.profiles.views.associate_application',),
                       ('/register_application/$', 'gsycbook.profiles.views.register_application',),
                       ('/confirm_friendship_request/$', 'gsycbook.profiles.views.confirm_friendship_request',),
                       ('/delete_my_profile/', 'gsycbook.profiles.views.delete_my_profile',),
                       ('/confirm_delete_my_profile/', 'gsycbook.profiles.views.confirm_delete_my_profile',),
                       ('/change_template/$', 'gsycbook.profiles.views.change_template',),
)



