# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from basic_email.views import FakeEmailSend, ListEmailTemplatesView, PreviewEmailView
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = patterns('',
                       url(r"fake/", staff_member_required(FakeEmailSend.as_view())),
                       url(r"admin/list/", staff_member_required(ListEmailTemplatesView.as_view()),
                           name='list-email-templates'),
                       url(r"admin/preview/", staff_member_required(PreviewEmailView.as_view()),
                           name='preview-email-templates'),
                       )
