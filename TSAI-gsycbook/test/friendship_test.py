from gsycbook.profiles.models import Profile

#Small script to test the proper behaivour of the function isFriendOf

set1 = Profile.objects.all()
set2 = Profile.objects.all()

for x in set1:
    for y in set2:
        if x.isFriendOf(y):
            print(x.user.username + " is friend of " + y.user.username)
        else:
            print(x.user.username + " is NOT friend of " + y.user.username)