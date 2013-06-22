from django.contrib.auth.models import User

#Small script to test the proper behaivour of the function isFriendOf

set1 = User.objects.filter(is_superuser=False)
all = User.objects.filter(is_superuser=False)

for x in set1:
    x.get_profile().filterUsersNotFriends(all)
    print("Friends of " + x.user.username + " : ")
    for y in all:
        print(y.username + ",")
    all = User.objects.filter(is_superuser=False)