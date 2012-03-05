from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^$", "timesheet.views.clock"),
    url(r"^login/", "django.contrib.auth.views.login", {"template_name": "timesheet/login.html"}),
    url(r"^customer/(?P<customer_id>\d+)/report(\.(?P<format_identifier>\w+))?/", "timesheet.views.customer_report")
)
