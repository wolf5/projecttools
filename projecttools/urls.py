from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^timesheet/", "timesheet.views.clock"),
    url(r"^login/", "django.contrib.auth.views.login", {"template_name": "me/login.html"}),
    url(r"^logout/", "django.contrib.auth.views.logout_then_login", {"login_url": settings.LOGIN_URL}),
    url(r"^customer/(?P<customer_id>\d+)/report(\.(?P<format_identifier>\w+))?/((?P<year>\d{4})(/(?P<month>\d{1,2}))?)?", "timesheet.views.customer_report"),
    url(r"^css/main.css", "timesheet.views.main_css"),
    url(r"^register/", "me.views.register"),
)
