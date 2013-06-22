from django_restapi.resource import Resource

from gsycbook.profiles.models import Profile
from django.contrib.auth.models import User

from django.core import serializers
from django.http import *

from django.utils import feedgenerator
from gsycbook.profiles.httpbasic import is_valid


class FriendshipList(Resource):
    

    def read(self, request, profile_nick):
        """Returns an atom feed with all the friends of this user if the user has an account in the system
        Validation is performed using http basic"""
        if (is_valid(request)):
            try:
                profile = User.objects.get(username = profile_nick).get_profile()
                friends = profile.friends.all()
        
                atom = feedgenerator.Atom1Feed( title= 'GSyC-Book - ' +  profile.user.username + '\'s friends', link='../../../profiles/show_profile/' + profile.user.username, description=u'These are all the friends of ' +  profile.user.username  + ' in GSyC-Book', language=u'en');
                for f in friends:
                    atom.add_item(title=f.user.username, link='../../../profiles/show_profile/' + f.user.username, description= f.user.get_full_name())
                    
                return HttpResponse(atom.writeString('UTF-8'), mimetype='text/xml')
            except User.DoesNotExist:
                raise Http404
        else:
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="GSyCBook-Friendship List webservice"'
            return response


class FriendshipEntry(Resource):

   
    def read(self, request, profile_nick, friend_nick):
        """Returns the profile of his friend in xml. Validation is performed using http basic"""
        
        if (is_valid(request)):
            try:
                profile = User.objects.get(username = profile_nick).get_profile()
                #Get all his friends (it will be only one), and filter by friend nick afterwards
                friends = profile.friends.all().filter(user__username=friend_nick)
                
                #If they are not friends or the nick is invalid (empty query), raise a UserDoesNotExist exception (404)
                if (friends.count()<1):
                    raise User.DoesNotExist
                
                xml = serializers.serialize('xml', list(friends))
                return HttpResponse(xml, mimetype='text/xml')
            except User.DoesNotExist:
                raise Http404
        else:
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="GSyCBook-Friendship Entry webservice"'
            return response
    

    def delete(self, request, profile_nick, friend_nick):
        """Deletes the relationship between profile_nick and his friend and returns the new list of friends in xml. 
        If it does not exist, the same list is returned. Validation is performed using http basic"""
        if (is_valid(request)):
            try:
                profile = User.objects.get(username = profile_nick).get_profile()
                friends = profile.friends.all().filter(user__username=friend_nick)
                
                #If they are not friends or the nick is invalid (empty query), raise a UserDoesNotExist exception (404)
                if (friends.count()<1):
                    raise User.DoesNotExist
                
                for f in friends:
                    profile.friends.remove(f)
    
                #Return the new set of friends
                friends = profile.friends.all()
                xml = serializers.serialize('xml', list(friends))
                return HttpResponse(xml, mimetype='text/xml')
            except User.DoesNotExist:
                raise Http404
        else:
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="GSyCBook-Friendship Entry webservice"'
            return response

