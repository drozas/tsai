from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render_to_response
from topfriends.ratings.models import Rating
from django.conf.urls.defaults import *
from django.db import IntegrityError
from django.core import serializers
from xml.dom.minidom import parse
from urllib2 import *
from django.http import *
from django.utils.datastructures import MultiValueDictKeyError




def vote(request):
    """Validate and store the votes received"""
    
#    Idea:   - Get the voting information - done
#            - Check that it does not exist already - done
#            - Check that the one who is voting is his friend using gsycbook services -done
#            - If everything ok, store it - done

    try:            
        vote_from = request.POST['vote_from']
        vote_to = request.POST['vote_to']
        try:
            points = int(request.POST['points'])
        except ValueError:
            return HttpResponse("Points must be a number between 0 and 10")
        
        #You can give from 0 til 10 points
        if ((points>0) and (points<=10)):
            try:
                #Read xml file from gsycbook - no protection
                #resource = urlopen("http://localhost:6666/xml/friends/" + vote_from)
                #dom = parse(resource)
                #resource.close()
                
                #Read xml web service from gsycbook (protected with HTTPBasic)
                password_mgr = HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, 'http://localhost:6666/xml/friends/' + vote_from, 'drozas', 'drozas')
                auth_handler = HTTPBasicAuthHandler(password_mgr)
                opener = build_opener(auth_handler)
                install_opener(opener)
                resource = opener.open("http://localhost:6666/xml/friends/" + vote_from)
                dom = parse(resource)
                resource.close()
                
                #Go through the XML document, adding the nicks of the friends
                friend_nicks = []
                for n in dom.getElementsByTagName("field"):
                    if n.getAttribute("name")=="username":
                        friend_nicks.append(n.firstChild.data)
                
                if (vote_to in friend_nicks):
                    
                    try:
                        #drozas: unique_toguether is not supported on sqlite, so we are check the integrity by hand
                        try:
                            r = Rating.objects.get(vote_from=vote_from, vote_to=vote_to)
                            #If no exception it is raised, it means this user has already vote this guy
                            raise IntegrityError
                        except Rating.DoesNotExist:
                            #If this exception was raised, it means it was a new vote
                            r = Rating(vote_from = vote_from, vote_to = vote_to, points = points)
                            r.save()
                        
                            #return HttpResponse("OK")
                            #If everything was ok, redirect to get_best_ratings
                            redirect = '/ratings/vote?profile_nick=%s&visitor_nick=%s' % (vote_to, vote_from)
                            
                            if (request.META.has_key('HTTP_REFERER')):
                                redirect = request.META['HTTP_REFERER']
                            
                            print('Redirigiendo a %s' % redirect)
                            
                            return HttpResponseRedirect(redirect)
                    except IntegrityError:
                        return HttpResponse("A vote has already been submitted from " + vote_from + " to " + vote_to)
                else:
                    return HttpResponse("You cannot vote for " + vote_to + " because he is not your friend")
            except URLError:
                return HttpResponse("It was no possible to access to gsycbook XML services")        
        else:
            return HttpResponse("Points must be a number between 1 and 10. You tried to vote with " + str(points) + " points")
    except MultiValueDictKeyError:
        msg_400 = "The parameters in the POST request are not correct"
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response        
        

def get_best_ratings(request):
    """Returns a top ten list of the candidates"""
    
    try:
        profile_nick = request.GET['profile_nick']
        visitor_nick = request.GET['visitor_nick']
    
        #If the user has already voted for it, we will show the points he gave
        try:
            r = Rating.objects.get(vote_from=visitor_nick, vote_to=profile_nick)
            #If no exception it is raised, it means this user has already vote this guy
            return render_to_response('ratings/show_ratings_already_voted.html', {'candidates_list': get_candidates_list(), 
                                                                'profile_nick': profile_nick, 
                                                                'visitor_nick': visitor_nick, 
                                                                'server': '%s:%s' % (request.META['SERVER_NAME'], request.META['SERVER_PORT']),
                                                                'rating': r,
                                                                })
        except Rating.DoesNotExist:
            #If the exception is raised, we will offer the opportunity of voting him
            return render_to_response('ratings/show_ratings_no_vote.html', {'candidates_list': get_candidates_list(), 
                                                                'profile_nick': profile_nick, 
                                                                'visitor_nick': visitor_nick, 
                                                                'server': '%s:%s' % (request.META['SERVER_NAME'], request.META['SERVER_PORT'])
                                                                })
    except MultiValueDictKeyError:
        msg_400 = "The parameters in the GET request are not correct"
        response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
        return response   


##### Internal methods #######
def get_candidates_list():
    """Returns a non sorted list of dictionaries with the information (name, summatory, number of votes and average) of all the candidates""" 
    
#    Idea:   - Compute an avg of the votes dinamically - done
#            - Return a list of users with the best voting sorted by avg- todo

    #Get a list of the different candidates
    candidates = Rating.objects.values("vote_to").distinct()
    
    #Get a list of all the ratings
    ratings = Rating.objects.all()
    
    #Compute the summatory, number of votes and average for each candidate
    #We are gonna create a list of dictionaries which will be sorted in the template
    candidates_list = []
    
    for c in candidates:
        new_candidate = {}
        new_candidate["name"] = c["vote_to"]
        new_candidate["summatory"] = 0
        new_candidate["votes"] = 0
        for r in ratings:
            if (c["vote_to"]==r.vote_to):
                new_candidate["summatory"] +=r.points
                new_candidate["votes"] = new_candidate["votes"] +1

        new_candidate["avg"] = new_candidate["summatory"] / new_candidate["votes"]
        candidates_list.append(new_candidate)
        
    return candidates_list
   


