from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
       model = Comment
       fields = ('name', "email", "comment")

       widgets ={
           "name": forms.TextInput(attrs={"id": "comment-author", "placeholder":" Name", "class":"custom-border"}),
           "email": forms.EmailInput(attrs={"id": "comment-email", "placeholder":" email@example.com", "class":"custom-border"}),
           "comment": forms.Textarea(attrs={"id": "comment-textarea", "placeholder":" Leave a comment!", "class":"custom-border"}),
       }

class ReplyForm(forms.ModelForm):
    class Meta:
       model = Comment
       fields = ("name", 'email', "comment",)

       widgets ={
           "name": forms.TextInput(attrs={"id": "reply-author", "placeholder":" Name", "class":"custom-border",}),
           "email": forms.EmailInput(attrs={"id": "reply-email", "placeholder":" email@example.com", "class":"custom-border",}),
            "comment": forms.Textarea(attrs={"id": "reply-textarea", "placeholder":"Your reply here!", "class":"custom-border", }),
       }

class UnsubscribeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id': 'email-input', "placeholder":" email@example.com"}))    