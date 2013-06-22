from django.db import models

class Rating(models.Model):
    vote_from = models.CharField(max_length=255, null=False, blank=False)
    vote_to = models.CharField(max_length=255, null=False, blank=False)
    points = models.IntegerField(null=False, blank=False)
    votation_date = models.DateTimeField(auto_now_add=True, blank=False)
    
    #A person can only vote for another person once. Doc from: http://docs.djangoproject.com/en/dev/ref/models/options/
    #drozas: This function it is not supported on sqlite, so we are gonna implement it by code
    unique_together = ("vote_from", "vote_to")

        
    def __unicode__(self):
        return self.vote_from + " has given " + str(self.points) + " points to " + self.vote_to