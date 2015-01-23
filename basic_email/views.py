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

    def get_template_data(self):
        from django.template.loader import get_template
        template_data = get_template(self.get_template())
        return template_data

    def content_encode(self, content):
        content = content.replace('{{', '{##_')
        to_replace = "{% extends '"
        replacer = "{{#_extends '{dir}/".format(dir=self.sub_tmp_dir)
        content = content.replace(to_replace, replacer)
        to_replace = '{% extends "'
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

    def prepare_tmp_file(self, original_file, original_template_name, tmp_dir):
        f = open(original_file.name, 'r')
        content = f.read()
        content = self.content_encode(content)
        print content
        # create tmp file with name, save and return
        path = os.path.join(tmp_dir, self.sub_tmp_dir, original_template_name)
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        tmp_f = open(path, 'w+')
        tmp_f.write(content)
        tmp_f.close()
        return tmp_f

    def list_template_variables(self):
        tmp_dir = tempfile.mkdtemp()
        print tmp_dir
        template_data = self.get_template_data()
        settings.TEMPLATE_DIRS = settings.TEMPLATE_DIRS + (tmp_dir,)
        tmp_template_file = self.prepare_tmp_file(template_data.origin, template_data.name, tmp_dir)
        for n in template_data.nodelist:
            self.prepare_tmp_file(n.get_parent(None).origin, n.get_parent(None).name, tmp_dir)
        content = render_to_string(tmp_template_file.name.replace(tmp_dir + os.pathsep, ''))
        print content
        shutil.rmtree(tmp_dir)  # careful! removes whole tree.


class PreviewEmailView(ListEmailVariables):

    def get_context_data(self, *args, **kwargs):
        context = super(PreviewEmailView, self).get_context_data(*args, **kwargs)
        self.list_template_variables()
        return context
