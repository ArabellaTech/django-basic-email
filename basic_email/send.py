# -*- coding: utf-8 -*-
import logging
import cssutils
import html2text

from django.contrib.sites.models import Site
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from premailer import Premailer

cssutils.log.setLevel(logging.CRITICAL)


def send_email(template, to, subject, variables={}, fail_silently=False,
               replace_variables={}, reply_to=False, attachments=None,
               memory_attachments=None):
    variables['site'] = Site.objects.get_current()
    variables['STATIC_URL'] = settings.STATIC_URL
    variables['is_secure'] = getattr(settings, 'IS_SECURE', False)
    html = render_to_string(template, variables)
    protocol = 'https://' if variables['is_secure'] else 'http://'
    replace_variables['protocol'] = protocol
    domain = variables['site'].domain
    replace_variables['domain'] = domain
    for key, value in replace_variables.items():
        if not value:
            value = ''
        html = html.replace('{%s}' % key.upper(), value)
    # Update path to have domains
    base = protocol + domain
    html = Premailer(html,
                     remove_classes=False,
                     exclude_pseudoclasses=False,
                     keep_style_tags=True,
                     include_star_selectors=True,
                     strip_important=False,
                     base_url=base).transform()
    headers = {}
    if reply_to:
        headers['Reply-To'] = reply_to

    # try to get text template, if not use text version of html
    txt_template = template.replace('html', 'txt')
    try:
        text = render_to_string(txt_template, variables)
    except TemplateDoesNotExist:
        text = html2text.HTML2Text()
        text.ignore_images = True
        text = text.handle(html)
    email = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [to],
                                   headers=headers)
    email.attach_alternative(html, "text/html")
    if attachments:
        for attachment in attachments:
            email.attach_file(attachment)
    if memory_attachments:
        for attachment in memory_attachments:
            email.attach(attachment['name'], attachment['content'],
                         attachment['mime'])
    email.send(fail_silently=fail_silently)
