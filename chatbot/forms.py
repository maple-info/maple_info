from django import forms

class ChatForm(forms.Form):
    message = forms.CharField(label='Your Message', max_length=500)