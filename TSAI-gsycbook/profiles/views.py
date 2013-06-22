# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from gsycbook.profiles.models import Profile
from gsycbook.profiles.models import Application
from django.shortcuts import render_to_response
from django.db import IntegrityError
from django.core import serializers
from django.contrib.auth import logout

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from django.template import RequestContext

from django.http import *

from urllib2 import *

from django.http import HttpResponse

from gsycbook.profiles.httpbasic import is_valid


#Errors handling:
# - In general we are gonna use an HTTPXXX exception + message system (http://docs.djangoproject.com/en/dev/topics/auth/) to customize them
# - For some errors another code fits better (ex.: 403 for trying to see a profile from someone we are not friend of, but there are not
#    such shortcuts, so we are going to implement it with class HttpResponseForbidden (403), class HttpResponseBadRequest (400), etc

class ApplicationContent():
    """Auxiliar class for application content management"""
    
    #The content is loaded in the constructor. TODO: exceptions
    def __init__(self, app_name, app_url):
        self.name = app_name
        try:
            resource = urlopen(app_url)
            self.content = resource.read()
            resource.close()
        except URLError:
            self.content = "It was impossible to retrieve the content from the application server"
        except ValueError:
            self.content = "It was impossible to retrieve the content from the given url"
    

   
@login_required
def show_profile(request, nick_search):
    try:
        #Retrieve the user to show
        user = User.objects.get(username = nick_search)
  
        #If the user's profile you are trying to see is a superuser (even if you are superuser), we raise a UserDoesNotExist for security reasons
        if(user.is_superuser):
            #request.user.message_set.create(message="You do not have permissions to access this profile")
            #raise Http404
            msg_403 = "You do not have permissions to access this profile"
            response = HttpResponseForbidden(msg_403, mimetype='text/plain')
            return response

        #If the request is from a superusers, we give him special threatment
        if(request.user.is_superuser):
            friends = user.get_profile().friends.all()
            return render_to_response('profiles_superuser_view.html', {'u': user, 'profile': user.get_profile(), 'friends': friends,}, context_instance=RequestContext(request),) 
        else:
            #If has permission (is himself of is his friend), we allow the operation
            if(request.user.get_profile().hasPermission(user.get_profile())):
                
                friends = user.get_profile().friends.all()
                
                #Get all the applications the visitor has associated (not for superuser)
                if(not(request.user.is_superuser)):
                    apps_assoc = request.user.get_profile().applications.all()
                    #Load the content for each of them
                    contents = []
                    for app in apps_assoc:
                        #Create and auxiliar class which retrieves the content
                        #If application is favourite cities, add some params.
                        if (app.name=="Favourite cities" or app.name=="TopTenFriends"):
                            app.url += "/?profile_nick=" + nick_search + "&visitor_nick=" + request.user.username
                        contents.append(ApplicationContent(app.name, app.url)) 
    
                    
                
                return render_to_response('profiles.html', {'u': user, 'profile': user.get_profile(), 'friends': friends,'app_contents': contents,}, context_instance=RequestContext(request),)
            else:
                #msg_403 = "You do not have permissions to access this profile"
                #response = HttpResponseForbidden(msg_403, mimetype='text/plain')
                
                #Show the option of request him as a friend
                already_req = user.get_profile().alreadyRequested(request.user.get_profile())
                return render_to_response('no_permissions.html', {'user_requested': user,  'already_req' : already_req,}, context_instance=RequestContext(request),)
    except User.DoesNotExist:
        request.user.message_set.create(message="That nick does not exit")
        raise Http404
        
@login_required  
def show_all_profiles(request):

    if(request.user.is_superuser):
        #Get all user who are not superusers and all the applications
        users = User.objects.exclude(is_superuser=True)
        all_apps = Application.objects.all()
        return render_to_response('show_all_profiles_superuser_view.html', {'users': users, 'apps': all_apps,}, context_instance=RequestContext(request),)

        
    else:

        #Get all the names of the people who have requested to be my friend
        friendship_requests = request.user.get_profile().requested_by.all()
        
        #Get all the names of the people who I have requested to be their friend
        my_requests = request.user.get_profile().friendship_request.all()
        
        #Show all the users that are friends of this user and which are not superusers (this should not happen, because superusers have not friends, but just in case)
        users = User.objects.filter(profile__friends__user__username__contains=request.user.username).exclude(is_superuser=True)
        
        #Get all the applications this user has
        apps_assoc = request.user.get_profile().applications.all()
        
        #Get the rest of application this user can register in
        rest_apps = Application.objects.exclude(profile__user__username=request.user.username)
        
        return render_to_response('show_all_profiles.html', {'friendship_requests': friendship_requests, 'my_requests': my_requests, 'users': users,'apps_assoc': apps_assoc,'rest_apps': rest_apps,}, context_instance=RequestContext(request),)
      
      
def show_form(request):
    return render_to_response('profile_form.html')

#drozas: extended for adding authentication functionality
#We are gonna have to keep both objects all the time. IT IS NOT INHERITANCE
def create_profile(request):
    
 
    #TODO: Check that all the fields exist, and catch exceptions
    #drozas: changes for creating user added
    try:
        username = request.POST['nick']
        first_name = request.POST['name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        email = request.POST['email']
        
        if (username=="" or first_name =="" or last_name =="" or password =="" or email== ""):
            raise ValueError
        
        
        new_user = User.objects.create_user(username, email, password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
    except IntegrityError:
        msg_400 = "The nick you have chosen already exists. Please, choose another one."
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response
    except ValueError:
        msg_400 = "You did not enter some of the mandatory fields"
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response


    #Conversions and validations (check how email and website fields should be validated)
    try:

        fav_number = int(request.POST['fav_number'])
        
        #TODO: create my own exception (this is overlaping some errors sometimes)
        if (fav_number<0 or fav_number>=10):
            raise ValueError
        
        fav_cite = request.POST['fav_cite']
        city = request.POST['city']
        website = request.POST['website']
        
        new_profile = Profile(user = new_user,fav_number=fav_number, city=city, website=website, fav_cite = fav_cite)
        new_profile.save()


          #Check exceptions now that we are working with two objects at the same time      
    except ValueError:
        #If it was not possible to store the profile, delete also the user
        new_user.delete()
        #message = "The favourite number has to be an integer between 0 and 10"
        #return render_to_response('profile_operation_result.html', {'message': message,})

        msg_400 = "The favourite number has to be an integer between 0 and 10"
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response

    message = "The profile was created sucessfully."
    return render_to_response('profile_operation_result.html', {'message': message,})

@login_required
def delete_friendship(request, nick_search):
   
    try:

        my_profile = User.objects.get(username = request.user.username).get_profile()
        ex_friend_profile = User.objects.get(username = nick_search).get_profile()

        if (my_profile.isFriendOf(ex_friend_profile)):
            my_profile.friends.remove(ex_friend_profile)
            return HttpResponseRedirect('/profiles/show_all_profiles')
            
        else:
            request.user.message_set.create(message="The user that you are trying to stop being friend of (" + nick_search + ") it is not already your friend")
            raise Http404
        
       
        #Check exceptions now that we are working with two objects at the same time
    except User.DoesNotExist:
        #message = "The user that you are trying to delete (" + nick_search + ") does not exist"
        #return render_to_response('profile_operation_result.html', {'message': message, 'path': '../',})
        request.user.message_set.create(message="The user that you are trying to stop being friend of (" + nick_search + ") does not exist")
        raise Http404

        
    #message = "The profile for " + nick_search + " has been deleted successfully"
    #return render_to_response('profile_operation_result.html', {'message': message, 'path': '../',})

#It was necessary to create one more view, because if we redirected directly from JS from delete_my_profile view
#no content was returned and an exception raised
@login_required
def confirm_delete_my_profile(request):
    return render_to_response('confirm_delete.html', context_instance=RequestContext(request),)

@login_required
def delete_my_profile(request):
   
    try:


        user = User.objects.get(username = request.user.username)
        user.get_profile().delete()
        user.delete();
        
        logout(request)       
        return HttpResponseRedirect('/')
        
        #Check exceptions now that we are working with two objects at the same time
    except User.DoesNotExist:
        #message = "The user that you are trying to delete (" + nick_search + ") does not exist"
        #return render_to_response('transparentia/profile_operation_result.html', {'message': message, 'path': '../',})
        #Since you have already been authenticated, the user should exists. This should never happen
        request.user.message_set.create(message="The user that you are trying to delete (" + nick_search + ") does not exist")
        raise Http404



@login_required
def add_friend(request, my_nick):
    
    new_friend_nick = request.GET['nick']
    
    #Recover both profiles, check that both exist and establish a request relationship
    try:
        my_profile = User.objects.get(username = my_nick).get_profile()
        new_friend_user = User.objects.get(username = new_friend_nick)
        
        #If he is a superuser, raise as if he did not exist
        if (new_friend_user.is_superuser):
            raise User.DoesNotExist
        
        new_friend_profile = new_friend_user.get_profile()
        
        if (not my_profile.alreadyRequested(new_friend_profile)):

            #Store friendship request from A (me) to B (new_friend)
            if (my_profile.hasPermissionToRequest(new_friend_profile)):
                my_profile.friendship_request.add(new_friend_profile)
            else:
                request.user.message_set.create(message="You are already friend of " + new_friend_nick + " or you are trying to be friend of yourself")
                raise Http404
        else:
            request.user.message_set.create(message= new_friend_nick + "has already requested to be your friend. Confirm it in the main menu.")
            raise Http404
            
    except User.DoesNotExist:
        request.user.message_set.create(message="One (or both) of the following nicks: " + my_nick + "," + new_friend_nick + " does not exist")
        raise Http404
        
    #If everything was ok, we redirect to main page
    return HttpResponseRedirect('/profiles/show_all_profiles')

@login_required
def confirm_friendship_request(request):
    
    new_friend_nick = request.GET['nick']
    
    #Recover both profiles, check that both exist and establish a symmetrical friendship relationship
    try:
        my_profile = User.objects.get(username = request.user.username).get_profile()
        new_friend_profile = User.objects.get(username = new_friend_nick).get_profile()

        #Delete request from A (another) to me (B)
        my_profile.requested_by.remove(new_friend_profile)
        
        #Store friendship (in both senses)
        #If they were already friends it is not a problem (a new tuple is stored), but we are gonna try to avoid it
        my_profile.friends.add(new_friend_profile)
    except User.DoesNotExist:
        request.user.message_set.create(message="One (or both) of the following nicks: " + request.user.username + "," + new_friend_nick + " does not exist")
        raise Http404
        
    #If everything was ok, we redirect to the main page
    return HttpResponseRedirect('/profiles/show_all_profiles/')

@login_required
def associate_application(request):
    
    app_pk = request.POST['id_application']
    
    #Recover both profile from request and application
    try:
        p = request.user.get_profile()
        app = Application.objects.get(pk=app_pk)
        
        #Store relationship between both
        p.applications.add(app)

    except User.DoesNotExist:
        request.user.message_set.create(message="The user does not exist")
        raise Http404
    except Application.DoesNotExist:
        request.user.message_set.create(message="The application does not exist")
        raise Http404
    except URLError:
        request.user.message_set.create(message="It was not possible to retrieve the content from " + app.url)
        raise Http404
        
        
    #If everything was ok, we redirect to the main page (the same we receive the request
    return HttpResponseRedirect('/profiles/show_all_profiles')

@login_required
def register_application(request):
    
 
    try:
        app_name = request.POST['app_name']
        app_url = request.POST['app_url']
        
        if (app_name=="" or app_url==""):
            raise ValueError
        
        if (not request.user.is_superuser):
            msg_403 = "You do not have permissions to access this profile"
            response = HttpResponseForbidden(msg_403, mimetype='text/plain')
            return response
        

        new_app = Application(name = app_name, url = app_url)
        new_app.save()
    except IntegrityError:
        msg_400 = "The application you are trying to upload already exists."
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response
    except ValueError:
        msg_400 = "Both fields are mandatory"
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response

    #If everything was ok, we redirect to the main page (the same we receive the request
    return HttpResponseRedirect('/profiles/show_all_profiles')

@login_required
def change_template(request):
    
    try:
        template = request.POST['id_template']
        p = request.user.get_profile()
        p.template = template
        p.save()
        
    except ValueError:
        msg_400 = "POST parameter was not sent"
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response
    except User.DoesNotExist:
        request.user.message_set.create(message="The user does not exist")
        raise Http404

    #If everything was ok, we redirect to the main page (the same we receive the request
    return HttpResponseRedirect('/profiles/show_all_profiles')



################# Web Services - Protected by HTTPBasic ##################

def show_profile_xml(request, nick_search):
    """Show a profile in xml if exists, an empty xml otherwise. This service is protected by HTTPBasic"""
    if (is_valid(request)):  
        p = Profile.objects.filter(user__username=nick_search)
        xml = serializers.serialize('xml',p)
        response = HttpResponse(xml, mimetype='text/xml')
        return response
    else:
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="GSyCBook-Profile XML webservice"'
        return response
        
def show_all_profiles_xml(request):
    """Show a list of profiles in xml if there are any, an empty xml otherwise. This service is protected by HTTPBasic"""
    if (is_valid(request)):  
        list_profiles= list(Profile.objects.all())
        xml = serializers.serialize('xml', list_profiles)
        response = HttpResponse(xml, mimetype='text/xml')
        return response
    else:
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="GSyCBook-ProfileList XML webservice"'
        return response
     
def show_profile_json(request, nick_search):
    """Show a profile in json if exists, an empty json otherwise. This service is protected by HTTPBasic"""
    if (is_valid(request)):  
        p = Profile.objects.filter(user__username=nick_search)
        json = serializers.serialize('json', p)
        response = HttpResponse(json, mimetype='text/json')
        return response
    else:
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="GSyCBook-Profile JSON webservice"'
        return response
     
def show_all_profiles_json(request):
    """Show a list of profiles in json if there are any, an empty json otherwise. This service is protected by HTTPBasic"""
    if (is_valid(request)):  
        list_profiles= list(Profile.objects.all())
        json = serializers.serialize('json', list_profiles)
        response = HttpResponse(json, mimetype='text/json')
        return response
    else:
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="GSyCBook-ProfileList JSON webservice"'
        return response
    
def show_friends_xml(request, nick_search):
    """Show all the friends of this user in xml format. It is protected by httpbasic"""  
    if (is_valid(request)):  
        #Get all the users that are friends of this user and which are not superusers (this should not happen, because superusers have not friends, but just in case)
        friends = User.objects.filter(profile__friends__user__username__contains=nick_search).exclude(is_superuser=True)
    
        #Serialize only the nicknames
        xml = serializers.serialize('xml', friends, fields=('username'))
        response = HttpResponse(xml, mimetype='text/xml')
        return response
    else:
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="GSyCBook-Friendship XML-List webservice"'
        return response


    