# -*- coding: utf-8 -*-
import os
import tempfile
import shutil
import re

from django.core.urlresolvers import reverse_lazy
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.conf import settings

from basic_email.send import send_email
from basic_email.forms import EmailPreviewForm


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
                        fileList.append(file.replace('.html', ''))
        context['files'] = fileList
        return context


class PreviewEmailView(TemplateView):

    def get_email_template(self, *args, **kwargs):
        if not self.request.GET.get('template'):
            raise NameError("?template=... is required")
        return os.path.join(settings.BASIC_EMAIL_DIRECTORY, '%s.%s' % (self.request.GET.get('template'), 'html'))

    def get_template(self, *args, **kwargs):
        if self.template_name:
            return self.template_name
        return self.get_email_template()

    def get_template_names(self, *args, **kwargs):
        return [self.get_template()]


class ListEmailVariablesView(PreviewEmailView):
    sub_tmp_dir = 'emails_tmp'
    tmpl_variable_prefix = '{##_'
    template_name = os.path.join(os.path.dirname(__file__), 'templates/admin/list-template-variables.html')

    def content_encode(self, content):
        to_replace = "{{% extends '{dir}/".format(dir=settings.BASIC_EMAIL_DIRECTORY)
        replacer = "{{#_extends '{dir}/".format(dir=self.sub_tmp_dir)
        content = content.replace(to_replace, replacer)
        to_replace = '{{% extends "{dir}'.format(dir=settings.BASIC_EMAIL_DIRECTORY)
        replacer = '{{#_extends "{dir}'.format(dir=self.sub_tmp_dir)
        content = content.replace(to_replace, replacer)

        content = content.replace('{% block ', '{#_block ')
        content = content.replace('{% endblock ', '{#_endblock ')
        content = content.replace('{%', '{#_')
        content = content.replace('{{', self.tmpl_variable_prefix)
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
        file_name = self.get_email_template().replace(settings.BASIC_EMAIL_DIRECTORY, self.sub_tmp_dir)
        content = render_to_string(file_name)
        regexp = re.compile(self.tmpl_variable_prefix + '\s*\w+')
        # this regexp (?<={##_\s+)\w+') will not work since look behind statement requires fixed width expression
        # need to manually remove prefix
        variables = [v.replace(self.tmpl_variable_prefix, '').strip() for v in regexp.findall(content)]
        shutil.rmtree(tmp_dir)  # careful! removes whole tree.
        return variables

    def get_context_data(self, *args, **kwargs):
        context = super(ListEmailVariablesView, self).get_context_data(*args, **kwargs)
        context['template_variables'] = self.list_template_variables()
        context['template'] = self.request.GET.get('template')
        return context


class SendEmailPreviewView(ListEmailVariablesView):
    template_name = os.path.join(os.path.dirname(__file__), 'templates/admin/email-form.html')
    form_class = EmailPreviewForm
    success_url = reverse_lazy('list-email-templates')  # fixme - better success url

    def get_form(self, *args, **kwargs):
        return self.form_class(self.request.POST or None, extra=self.list_template_variables())

    def get_context_data(self, **kwargs):
        context = super(SendEmailPreviewView, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.form_class)
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        send_email(self.get_email_template(), form.cleaned_data.get('email'), 'Fake email!', form.cleaned_data)
        context = self.get_context_data()
        context['form'] = form
        context['success'] = True
        return self.render_to_response(context)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form))
