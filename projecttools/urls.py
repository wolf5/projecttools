from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^$", "me.views.index", name = "index"),
    url(r"^timesheet/", "timesheet.views.clock", name = "clock"),
    url(r"^login/", "me.views.login", name = "login"),
    url(r"^logout/", "django.contrib.auth.views.logout_then_login", {"login_url": settings.LOGIN_URL}, name = "logout"),
    url(r"^customer/(?P<customer_id>\d+)/report(\.(?P<format_identifier>\w+))?/((?P<year>\d{4})(/(?P<month>\d{1,2}))?)?", "timesheet.views.customer_report", name = "customer_report"),
    url(r"^css/main.css", "timesheet.views.main_css"),
    url(r"^register/", "me.views.register", name = "register"),
    url(r"^me/activationSent/", "me.views.activationSent", name = "activation_sent"),
    url(r"^me/activate/(?P<activationKey>\w{64})", "me.views.activate", name = "activate"),
    url(r"^me/activationFailed/", "me.views.activationFailed", name = "activation_failed"),
    url(r"^me/subscribe/", "me.views.subscribe", name = "subscribe"),
    url(r"^me/mail_success/", "me.views.mail_success", name = "me_mail_success"),
    url(r"^me/mail_failed/", "me.views.mail_failed", name = "me_mail_failed"),
)
