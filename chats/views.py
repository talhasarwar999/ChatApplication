from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from . models import *
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage


# Create your views here.
def index(request):
    allusers = User.objects.all()
    reuser = str(request.user)
    content = {'allusers':allusers,'reuser':reuser}
    return render(request,"chats/index.html", content)

def SignUp(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if User.objects.filter(username=username):
            messages.warning(request, 'This username is already taken: Try another Username')
            return redirect('index')
        if (password != confirm_password):
            messages.error(request, "Passwords do not match")
            return redirect('index')
        if len(username) < 4:
            messages.error(request, " Your user name must be under 4 characters")
            return redirect('index')
        if len(password) < 6:
            messages.error(request, " Your password must be under 6 characters")
            return redirect('index')
        if not password.isalnum():
            messages.error(request, " Your password cannot contain special characters")
            return redirect('index')
        else:
            user=User.objects.create_user(username,email,password)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('chats/acc_active_email. html',
            {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            messages.success(request, "We have sent an email with a confirmation link to your email address. In order to complete the sign-up process, please click the confirmation link.")
            return redirect('index')
    return render(request,"chats/Signup.html")

def logins(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request,"Succesfully Login")
            return redirect('index')
        else:
            messages.error(request,"Invalid Credentials!")
        return redirect('index')
    return render(request, "chats/Login.html")

def logouts(request):
    logout(request)
    messages.success(request, "Succesfully Logout")
    return redirect('index')

def SendFriendRequest(request, receiver):
    r = User.objects.get(username = receiver)
    sender = Profile.objects.get(user = request.user)
    receiver_ = Profile.objects.get(user = r)
    status = "send"
    if Relationship.objects.filter(senderFriend = sender, receiverFriend = receiver_):
        return render(request, "chats/friendspage.html", {"errMsg": "Friend request is already sent"})
    if Relationship.objects.filter(senderFriend = receiver_ ,receiverFriend = sender):
        return render(request, "chats/friendspage.html", {"errMsg": "Friend request is already sent"})
        Relationship.objects.create\
    (
        senderFriend = sender,
        receiverFriend = receiver_,
        status = status
    )
    return render(request, "chats/friendspage.html")

def GetAllFriendRequests(request):
    user = Profile.objects.get(user = request.user)
    frndRequests = Relationship.objects.filter(receiverFriend = user, status="send")
    return render(request, "chats/friendspage.html", {"frdrequests": frndRequests})

def GetAllFriends(request):
    frnds =  Profile.objects.get(user=request.user)
    frndList = frnds.myFriends.all()
    print(frndList)
    msgNumbers=[]
    for frnd in frndList:
        sender = Profile.objects.get(user=frnd)
        msgs= Messages.objects.filter(messageSender=sender, messageReceiver=frnds, msgStatus="unread")
        no = msgs.count()
        all=(frnd,no)
        msgNumbers.append(all)
    return render(request, "chats/friendspage.html", {"frnds": msgNumbers})

def AcceptRequest(request, receiver):
    sender = User.objects.get(username=receiver)
    r = Profile.objects.get(user=request.user)
    s = Profile.objects.get(user=sender)
    obj = Relationship.objects.get(senderFriend=s, receiverFriend=r)
    if obj.status=="send":
        obj.status = "accepted"
    obj.save()
    return render(request, "chats/friendspage.html")

def SendMessage(request):
    if request.method =="POST":
        re = str(request.user)
        receiver = request.POST.get("receiver")
        r = User.objects.get(username=receiver)
        sender = Profile.objects.get(user=request.user)
        receiver_ = Profile.objects.get(user=r)
        msg = request.POST['message']
        Messages.objects.create(
            messageSender = sender,
            messageReceiver = receiver_,
            messageValue = msg
        )
    messageObjects1 = Messages.objects.filter(messageSender=sender, messageReceiver=receiver_)
    messageObjects2 = Messages.objects.filter(messageSender=receiver_, messageReceiver=sender)
    messageObjects = messageObjects2.union(messageObjects1)
    return render(request, "chats/Communication.html", {"msgs": messageObjects, "receiver": receiver,"re":re})

def GoToSendMessage(request, receiver):
    r = User.objects.get(username=receiver)
    re=str(request.user)
    sender = Profile.objects.get(user=request.user)
    receiver_ = Profile.objects.get(user=r)
    messageObjects1 = Messages.objects.filter(messageSender=sender, messageReceiver=receiver_)
    messageObjects2 = Messages.objects.filter(messageSender=receiver_, messageReceiver=sender)
    for msg in messageObjects2:
        msg.msgStatus="read"
        msg.save()
    messageObjects = messageObjects2.union(messageObjects1)
    return render(request, "chats/Communication.html", {"msgs": messageObjects, "receiver": receiver,"sender":sender,"re":re})

def dels(request,receiver):
    ru=request.user
    user = User.objects.get(id=receiver)
    pro=Profile.objects.get(user=user)
    ru.myFriends.remove(pro)
    messages.success(request, "Deleted")
    return redirect('index')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')