# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from basic_email.views import FakeEmailSend
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = patterns('',
                       url(r"$", staff_member_required(FakeEmailSend.as_view())),
                       )
