from django import forms


class AddPLayersForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    players = forms.CharField(widget=forms.Textarea)
