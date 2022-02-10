from django.urls import path
from . import views

urlpatterns=[
    path('',views.index, name="index"),
    path('SignUp/',views.SignUp, name="SignUp"),
    path('logins/',views.logins, name="logins"),
    path('logouts/',views.logouts, name="logouts"),
    path('myown/<receiver>',views.SendFriendRequest, name="myown"),
    path('frndrequests/',views.GetAllFriendRequests, name="frndrequests"),
    path('frnds/',views.GetAllFriends, name="frnds"),
    path('acceptReq/<receiver>',views.AcceptRequest, name="acceptReq"),
    path('sendMessage/',views.SendMessage, name="sendMessage"),
    path('GoToSendMsg/<receiver>',views.GoToSendMessage, name="GoToSendMsg"),
    path('dels/<int:receiver>',views.dels, name="dels"),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
]