from django import forms

class ContactForm(forms.Form):
    name    = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'mdl-textfield__input required', 'id':'name'}))
    email   = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'mdl-textfield__input required', 'id':'email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'mdl-textfield__input required', 'id':'textarea'}))
