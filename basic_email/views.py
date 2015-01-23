# -*- coding: utf-8 -*-
import os
import tempfile
import shutil

from django.template.loader import render_to_string
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
    sub_tmp_dir = 'emails_tmp'

    def get_template(self, *args, **kwargs):
        if not self.request.GET.get('template'):
            raise NameError("?template=... is required")
        return os.path.join(settings.BASIC_EMAIL_DIRECTORY, self.request.GET.get('template'))

    def get_template_names(self, *args, **kwargs):
        return [self.get_template()]

    def content_encode(self, content):
        content = content.replace('{{', '{##_')
        to_replace = "{{% extends '{dir}/".format(dir=settings.BASIC_EMAIL_DIRECTORY)
        replacer = "{{#_extends '{dir}/".format(dir=self.sub_tmp_dir)
        content = content.replace(to_replace, replacer)
        to_replace = '{{% extends "{dir}'.format(dir=settings.BASIC_EMAIL_DIRECTORY)
        replacer = '{{#_extends "{dir}'.format(dir=self.sub_tmp_dir)
        content = content.replace(to_replace, replacer)

        content = content.replace('{% block ', '{#_block ')
        content = content.replace('{% endblock ', '{#_endblock ')
        content = content.replace('{%', '{#_')
        content = content.replace('{{', '{##_')
        content = content.replace('{#_extends', '{% extends')
        content = content.replace('{#_block ', '{% block ')
        content = content.replace('{#_endblock ', '{% endblock ')

        return content

    def prepare_tmp_files(self, tmp_dir):
        for d in settings.TEMPLATE_DIRS:
            d = os.path.join(d, settings.BASIC_EMAIL_DIRECTORY)
            if os.path.exists(d):
                for file_name in os.listdir(d):
                    if not os.path.isdir(d + file_name):
                        f = open(os.path.join(d, file_name), 'r')
                        content = f.read()
                        content = self.content_encode(content)
                        path = os.path.join(tmp_dir, self.sub_tmp_dir, file_name)
                        dir_name = os.path.dirname(path)
                        if not os.path.exists(dir_name):
                            os.makedirs(dir_name)
                        tmp_f = open(path, 'w+')
                        tmp_f.write(content)
                        tmp_f.close()

    def list_template_variables(self):
        tmp_dir = tempfile.mkdtemp()
        settings.TEMPLATE_DIRS = settings.TEMPLATE_DIRS + (tmp_dir,)
        self.prepare_tmp_files(tmp_dir)
        file_name = self.get_template().replace(settings.BASIC_EMAIL_DIRECTORY, self.sub_tmp_dir)
        content = render_to_string(file_name)
        print (content)
        shutil.rmtree(tmp_dir)  # careful! removes whole tree.


class PreviewEmailView(ListEmailVariables):

    def get_context_data(self, *args, **kwargs):
        context = super(PreviewEmailView, self).get_context_data(*args, **kwargs)
        self.list_template_variables()
        return context
