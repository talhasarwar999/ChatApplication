from django.db import models
from  django.conf import settings
from django.db.models import ForeignKey
from  django.utils import timezone
from django.contrib.auth.models import User

# Models
class Profile(models.Model):
    user = models.OneToOneField(User, related_name="Profile", on_delete=models.CASCADE)
    myFriends = models.ManyToManyField(User, related_name="myFriends", blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user)
    def get_friends(self):
        return self.myFriends.all()
    def get_friend_no(self):
        return self.myFriends.all().count()

STATUS_CHOICES = ( ('send', 'send'), ('accepted', 'accepted'),)
class Relationship(models.Model):
    senderFriend = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="senderFriend")
    receiverFriend = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receiverFriend")
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.senderFriend}-{self.receiverFriend}-{self.status}"

class Messages(models.Model):
    messageSender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messageSender")
    messageReceiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="messageReceiver")
    messageValue = models.CharField(max_length=1000, null=False)
    msgStatus = models.CharField(max_length=10, default="unread")
    created = models.DateTimeField(auto_now_add=True)
