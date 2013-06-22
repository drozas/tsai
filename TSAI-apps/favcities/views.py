from apps.favcities.models import FavCity
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest


from django.http import *
from xml.dom.minidom import parse
from urllib2 import *
from django.utils.datastructures import MultiValueDictKeyError

def get_cities(request):
	
	try:
		profile_nick = request.GET['profile_nick']
		visitor_nick = request.GET['visitor_nick']
		
		if (profile_nick == visitor_nick):
			return show_city_profile(request, profile_nick)			
		else:
			return show_shared_cities(request, profile_nick, visitor_nick)
	except MultiValueDictKeyError:
		msg_400 = "The parameters in the GET request are not correct"
		response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
		return response 
		
def update_cities(request):
	try:
		profile_nick = request.GET['profile_nick']
		city_names_param = request.POST['city_names']
		
		FavCity.objects.filter(nick=profile_nick).delete()
		
		city_names = city_names_param.split(",")
		
		for city_name in city_names:
			normalized_city_name=city_name.strip().lower().capitalize()
			
			count = FavCity.objects.filter(nick=profile_nick, city_name=normalized_city_name).count()
			
			if (FavCity.objects.filter(nick=profile_nick, city_name=normalized_city_name).count() == 0):
				fc = FavCity(nick=profile_nick, city_name=normalized_city_name)
				fc.save()	
		
		redirect = '/favcities/profiles?profile_nick=%s&visitor_nick=%s' % (profile_nick, profile_nick)
		
		if (request.META.has_key('HTTP_REFERER')):
			redirect = request.META['HTTP_REFERER']
		
		print('Redirigiendo a %s' % redirect)
		
		return HttpResponseRedirect(redirect)
	except MultiValueDictKeyError:
		msg_400 = "The parameters in the GET request are not correct"
		response = HttpResponseBadRequest(msg_400, mimetype='text/plain')
		return response 
	
##
## Internal methods
##

def show_shared_cities(request, profile_nick, visitor_nick):
	""" Show the cities that share as favorite the visitor and the owner of the current profile """
	
	print 'visitor_nick: %s' % visitor_nick
	visitor_cities = FavCity.objects.filter(nick=visitor_nick)
		
	shared_city_names = []

	for city in visitor_cities:
			
		shared_city = FavCity.objects.filter(nick=profile_nick, city_name=city.city_name).count()
		
		if (shared_city):
			shared_city_names.append(city.city_name)
			
	
	return render_to_response(
		'favcities/shared_cities.html', 
		{
			'shared_city_names': shared_city_names, 
			'profile_nick': profile_nick,
			'visitor_nick': visitor_nick,
			#'json_data': json
		})

def show_city_profile(request, profile_nick):
	""" Show the friends that have shared favorite cities along with those cities """

	try:
		#Read xml file from gsycbook
		#resource = urlopen("http://localhost:6666/xml/friends/" + profile_nick)
		#dom = parse(resource)
		#resource.close()
		
		#Read xml web service from gsycbook (protected with HTTPBasic)
		password_mgr = HTTPPasswordMgrWithDefaultRealm()
		password_mgr.add_password(None, 'http://localhost:6666/xml/friends/' + profile_nick, 'drozas', 'drozas')
		auth_handler = HTTPBasicAuthHandler(password_mgr)
		opener = build_opener(auth_handler)
		install_opener(opener)
		resource = opener.open("http://localhost:6666/xml/friends/" + profile_nick)
		dom = parse(resource)
		resource.close()
		
		#Go through the XML document, adding the nicks of the friends
		friend_nicks = []
		for n in dom.getElementsByTagName("field"):
			if n.getAttribute("name")=="username":
				friend_nicks.append(n.firstChild.data)


		cities_by_friend = {}
		
		profile_cities = FavCity.objects.filter(nick=profile_nick)
		
		for friend_nick in friend_nicks:	
			for city in profile_cities:
				
				city_profile_items = FavCity.objects.filter(nick=friend_nick, city_name=city.city_name).count()
				
				if (city_profile_items > 0):
					if cities_by_friend.has_key(friend_nick):
						cities_by_friend[friend_nick].append(city.city_name)
					else:
						cities_by_friend[friend_nick] = [city.city_name]
		
		city_profile_items = []
	
		for friend_nick in cities_by_friend:
			
			fav_city = CityProfileItem()
			fav_city.nick = friend_nick
			fav_city.city_names = cities_by_friend[friend_nick]
			
			city_profile_items.append(fav_city)
			
		profile_city_names = [city.city_name for city in profile_cities]
		
#		#drozas: List of cities, with a list of nicks who like it for each
		nick_profile_items = []
		for city in profile_city_names:
			nicks_list = []

			for item in city_profile_items:
				for c in item.city_names:
					if c == city:
						nicks_list.append(item.nick) 
			if (len(nicks_list)>0):
				nick_profile_items.append(NickProfileItem(city, nicks_list))

			
	
		return render_to_response(
			'favcities/city_profile.html', 
			{
				'city_profile_items': city_profile_items, 
				'nick_profile_items': nick_profile_items,
				'profile_nick': profile_nick,
				'profile_city_names': profile_city_names,
				'server': '%s:%s' % (request.META['SERVER_NAME'], request.META['SERVER_PORT'])
			})
	except URLError:
		#Not possible with AnonymousUser
		#request.user.message_set.create(message="It was impossible to retrieve the content from the application server")
		raise Http404
           

class CityProfileItem:
	""" Represents a list of cities for a given user identified by the nick """
	
	nick = ''
	city_names = []
	
class NickProfileItem():
	""" Represents a list of nicks for a given city """
	def __init__(self, city, nicks):
		self.city = city
		self.nicks = nicks
