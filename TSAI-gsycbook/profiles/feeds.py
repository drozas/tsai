from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from gsycbook.profiles.models import Profile
from django.contrib.auth.models import User

class LatestProfiles(Feed):
    title = "Gsycbook - Latest Profiles"
    link = "/feeds/latest/"
    description = "Latest profiles created on gsycbook"

    def item_link(self, item):
        """
        Takes an item, as returned by items(), and returns the profile's URL.
        """

        return "/profiles/show_profile/" + item.username
    

    #Last 5 profiles ordered by creation date
    def items(self):
        return User.objects.order_by('-date_joined')[:5]

