from django.db import models

class FavCity(models.Model):
	city_name 	= models.CharField(max_length=255)
	nick 			= models.CharField(max_length=255)
	
		
	def __str__(self):
		return 'A %s le gusta la ciudad %s' % (self.nick, self.cityName)
	
