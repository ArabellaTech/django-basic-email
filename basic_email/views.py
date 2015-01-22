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
    template_name = os.path.join(os.path.dirname(__file__), 'templates/admin/list.html')

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


class ListEmailVariables(TemplateView):

    def get_template(self, *args, **kwargs):
        if not self.request.GET.get('template'):
            raise NameError("?template=... is required")
        return os.path.join(settings.BASIC_EMAIL_DIRECTORY, self.request.GET.get('template'))

    def get_template_names(self, *args, **kwargs):
        return [self.get_template()]

    def get_template_data(self):
        from django.template.loader import get_template
        template_data = get_template(self.get_template())
        return template_data

    def content_encode(self, content):
        content = content.replace('{{', '{##_')
        return content

    def contend_decode(self, content):
        content = content.replace('{##', '{{')
        return content

    def list_template_variables(self):
        template_data = self.get_template_data()
        files = []
        for n in template_data.nodelist:
            # print ('filename in loop')
            # print n.get_parent(None).origin
            # print n.source[0]
            files.append('%s' % n.get_parent(None).origin)
        files.append('%s' % template_data.origin)
        f = open(self.dir + file_name, 'r')
        # save in tmp using random name: https://docs.python.org/2/library/tempfile.html
        # add this tmp directory to settings to search for template there. 
        content = f.read()
        content = self.content_encode(content)
        tmp_f = open(self.tmp_dir + file_name, 'w+')
        tmp_f.write(content)
        tmp_f.close()
        print files


class PreviewEmailView(ListEmailVariables):

    def get_context_data(self, *args, **kwargs):
        context = super(PreviewEmailView, self).get_context_data(*args, **kwargs)
        self.list_template_variables()
        return context
