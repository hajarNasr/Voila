from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from .forms import ContactForm 
from voila.settings import MY_EMAIL as my_email


def page_not_found(request, exception):
    return render(request, "404.html", {}) 
  
def base_view(request):
    if request.method == 'POST':
        # Someone has sent a message through the contact form
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = "Hello"
            name   = form.cleaned_data['name']
            email_from = form.cleaned_data['email']
            email_to = my_email
            message= form.cleaned_data['message']
            email = EmailMessage(subject=subject, body=message, from_email=email_from, to=[email_to], reply_to=[email_from])
            email.send()
            return render(request,'thanks-for-your-email.html',{"name":name})    
    form = ContactForm()
    return render(request, 'base.html', {'form': form})


