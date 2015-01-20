# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.conf import settings
from django.template import TemplateDoesNotExist

from basic_email.send import send_email


class FakeEmailSend(TemplateView):
    # template_name = 'emails/fake.html'
    template_name = 'test.html'

    def get_context_data(self, *args, **kwargs):
        context = super(FakeEmailSend, self).get_context_data(*args, **kwargs)
        context['template'] = self.request.GET.get('template')
        context['email'] = getattr(settings, 'FAKE_EMAIL_TO', None)
        if context['template'] and context['email']:
            try:
                send_email(context['template'], context['email'], 'Fake email!')
            except TemplateDoesNotExist:
                context['template_does_not_exist'] = True
        return context


class ListEmailTemplatesView(TemplateView):
    template_name = "admin/list.html"
