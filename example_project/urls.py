from django.conf.urls import include, patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'^emails/', include('basic_email.urls')),
)
