# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client
from django.core import mail
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
        response = self.client.get(reverse('list-email-templates'))
        expected_url = '/admin/login/?next=/emails/admin/list/'
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200, msg_prefix='')
        # access by admin
        self.client.login(password=self.password, username=self.admin.username)
        response = self.client.get(reverse('list-email-templates'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context[0].get('files')), 4)

    def test_preview(self):
        response = self.client.get(reverse('preview-email-templates'))
        expected_url = '/admin/login/?next=/emails/admin/preview/'
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200, msg_prefix='')

        self.client.login(password=self.password, username=self.admin.username)
        response = self.client.get(reverse('preview-email-templates'))
        self.assertEqual(response.status_code, 500)

    def test_variables_list(self):
        pass
