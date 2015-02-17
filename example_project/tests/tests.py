# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.template.base import TemplateDoesNotExist
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from basic_email.send import send_email


class EmailsTests(TestCase):
    def setUp(self):
        self.password = "password"
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', self.password)
        self.client = Client()

    def _test_access(self, url_name, template):
        # access page when not logged in - should throw an error
        response = self.client.get(reverse(url_name), follow=True)
        self.assertTemplateNotUsed(response, template)

    def _test_required_get_param_and_template_existence(self, url_name):
        # trying to access w/o template parameter will raise an error
        self.client.login(password=self.password, username=self.admin.username)
        self.assertRaises(NameError, self.client.get, reverse(url_name))

        # not existing template
        self.assertRaises(TemplateDoesNotExist, self.client.get,
                          reverse(url_name) + '?template=non_existing_fail')

    def _test_variables_list_response(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['template_variables']), 7)
        self.assertEqual(response.context['template_variables'][0], 'emailSubject')
        self.assertEqual(response.context['template_variables'][1], 'test_base_template_variable')
        self.assertEqual(response.context['template_variables'][2], 'test_template_variable_1')
        self.assertEqual(response.context['template_variables'][3], 'test_template_variable_2')
        self.assertEqual(response.context['template_variables'][4], 'test_template_variable_3')
        self.assertEqual(response.context['template_variables'][5], 'test_template_variable_4')
        self.assertEqual(response.context['template_variables'][6], 'test_template_variable_5')

    def test_send(self):
        send_email('emails/email_start.html', 'foo@bar.com', 'Lorem')
        self.assertEqual(len(mail.outbox), 1)

    def test_list(self):
        self._test_access('list-email-templates', 'admin/list.html')
        # access by admin
        self.client.login(password=self.password, username=self.admin.username)
        response = self.client.get(reverse('list-email-templates'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[0].get('files')), 1)

    def test_preview(self):
        self._test_access('preview-email-template', 'admin/preview.html')
        self._test_required_get_param_and_template_existence('preview-email-template')

        # proper
        response = self.client.get(reverse('preview-email-template') + '?template=email_start')
        self.assertEqual(response.status_code, 200)

    def test_variables_list(self):
        self._test_access('list-email-template-variables', 'admin/list.html')
        self._test_required_get_param_and_template_existence('list-email-template-variables')

        # proper
        response = self.client.get(reverse('list-email-template-variables') + '?template=email_start')
        self._test_variables_list_response(response)

    def test_sending_email_preview(self):
        self._test_access('send-email-preview', 'admin/email-form.html')
        self._test_required_get_param_and_template_existence('send-email-preview')

        response = self.client.get(reverse('send-email-preview') + '?template=email_start')
        self._test_variables_list_response(response)

        data = {
            'email': 'foo@bar.com',
            'emailSubject': 'test subject'
        }
        response = self.client.post(reverse('send-email-preview') + '?template=email_start', data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['success'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test subject')
