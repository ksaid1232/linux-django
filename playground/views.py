from django.shortcuts import render
from django.core.mail import send_mail, mail_admins, BadHeaderError

from .tasks import notify_shit


def say_hello(request):
    
    notify_shit.delay('hello')
    return render(request, 'hello.html', {'name': 'Mosh'})
