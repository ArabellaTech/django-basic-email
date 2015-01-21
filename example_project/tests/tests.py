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

    def test_send(self):
        send_email('start', 'foo@bar.com', 'Lorem')
        self.assertEqual(len(mail.outbox), 1)

    def test_list(self):
        # access page when not logged in - should throw an error
        response = self.client.get(reverse('list-email-templates'), follow=True)
        self.assertTemplateNotUsed(template_name='admin/list.html')
        # access by admin
        self.client.login(password=self.password, username=self.admin.username)
        response = self.client.get(reverse('list-email-templates'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[0].get('files')), 4)

    def test_preview(self):
        response = self.client.get(reverse('preview-email-templates'), follow=True)
        # expected_url = '/admin/login/?next=/emails/admin/preview/'
        self.assertTemplateNotUsed(template_name='admin/preview.html')
        # self.assertRedirects(response, expected_url, status_code=302, target_status_code=200, msg_prefix='')
        # trying to access w/o template parameter will raise an error
        self.client.login(password=self.password, username=self.admin.username)
        self.assertRaises(NameError, self.client.get, reverse('preview-email-templates'))

        # not existing template
        self.assertRaises(TemplateDoesNotExist, self.client.get,
                          reverse('preview-email-templates') + '?template=non_existing_fail')

        # proper
        response = self.client.get(reverse('preview-email-templates') + '?template=email_start.html')
        self.assertEqual(response.status_code, 200)

    def test_variables_list(self):
        pass
