# -*- coding: utf-8 -*-
import os
from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.conf import settings
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

    def get_context_data(self, *args, **kwargs):
        context = super(ListEmailTemplatesView, self).get_context_data(*args, **kwargs)
        templates_dirs = [os.path.join(d, settings.BASIC_EMAIL_DIRECTORY) for d in settings.TEMPLATE_DIRS]
        fileList = []
        for rootdir in templates_dirs:
            for root, subFolders, files in os.walk(rootdir):
                for file in files:
                    if file.startswith('email_') and file.endswith('.html'):
                        fileList.append(file)
        context['files'] = fileList
        return context


class PreviewEmailView(TemplateView):
    template_name = 'admin/preview.html'

    def get_template_names(self, *args, **kwargs):
        return [os.path.join(settings.BASIC_EMAIL_DIRECTORY, self.request.GET.get('template'))]

    def get_context_data(self, *args, **kwargs):
        context = super(PreviewEmailView, self).get_context_data(*args, **kwargs)
        context['template'] = self.request.GET.get('template')
        return context
