from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
	# This is the only required field for extends User
	user = models.ForeignKey(User, unique=True)
	
	fav_cite = models.CharField(max_length=400, null=True, blank=True)
	city = models.CharField(max_length=70, null=True, blank=True)
	fav_number = models.IntegerField(null=True, blank=True)
	
	website = models.URLField(blank=True)
	creation_date = models.DateTimeField(auto_now_add=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True, blank=True)
	template = models.CharField(max_length=30, null=False, blank=False, default="index_transparentia.html")

	#drozas:Recursive ManyToMany relationship with symmetrical = True: "If I am your friend, I am a friend of yours". The process to
	# request for friends will be managed in a different way
	friends = models.ManyToManyField('self', symmetrical=True, blank=True)
	
	#For requesting friendship. Idea:
	# If a->b means a has requested to be his friend
	# If b->a means b has accepted
	# Then, a symmetrical friends relationship is created
	# Based on: http://www.djangoproject.com/documentation/models/m2m_recursive/
	friendship_request = models.ManyToManyField('self', symmetrical=False, blank=True, related_name = 'requested_by')
	
	applications = models.ManyToManyField('Application', symmetrical=True, blank=True)
	
	def __unicode__(self):
		return self.user.first_name + " " + self.user.last_name + " (" + self.user.username + ")" + "\n Number of friends: " + str(self.getNumberOfFriends())
		#return self.id
	
	def getNumberOfFriends(self):
		return len(self.friends.all())
	
	def isFriendOf(self, anotherProfile):
		"""Returns true if there is a friendship relationship between both profiles, false otherwise"""
		#If we can perform this operation, is because there is a relationship between both (an entry in the table)
		#But if a DoesNotExist exception raises, it means they are not friends
		try:

			#Get all the friends of this user which are not admin
			users = User.objects.filter(profile__friends__user__username__contains=self.user.username).exclude(is_superuser=True)
			#And then we try to get the instance of the user we are visiting. If there is a DoesNotExist exceptions, it means he is not our friend
			user_req = users.get(username=anotherProfile.user.username)
    
			return True
		except User.DoesNotExist:
			return False
		
	def hasPermission(self, anotherProfile):
		"""Returns true if is himself or his friend"""
		return ((self==anotherProfile) or self.isFriendOf(anotherProfile))
	
	def hasPermissionToRequest(self, anotherProfile):
		"""Returns true if it is not my profile and it is not already my friend"""
		return ((self!=anotherProfile) and (not(self.isFriendOf(anotherProfile))))
	
	def alreadyRequested(self, anotherProfile):
		"""Returns true if anotherProfile has already requested to be your friend"""
		#Get all the request this user has received
		requests = self.requested_by.all()
		#And check if I have already been requested
		for p in requests:
			if (p.user.username==anotherProfile.user.username):
				return True
		
		return False
			
			
		
		


class Application(models.Model):
	name = models.CharField(max_length=100, unique=True, null=False, blank=False)
	url  = models.URLField(max_length=255, unique=True, null=False, blank=False, verify_exists=True)
	
	def __unicode__(self):
		return self.name + " (" + self.url + ")"
    
