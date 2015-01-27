# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


class EmailPreviewForm(forms.Form):
    email = forms.EmailField(label=_("Receiver"))

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass
