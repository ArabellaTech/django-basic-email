# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


class EmailPreviewForm(forms.Form):
    email = forms.EmailField(label=_("Receiver"))

    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra')
        super(EmailPreviewForm, self).__init__(*args, **kwargs)

        for i, f in enumerate(extra):
            self.fields['%s' % i] = forms.CharField(label=f, required=False)
