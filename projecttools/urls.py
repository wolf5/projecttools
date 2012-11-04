from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^$", "timesheet.views.clock", name="clock"),
    url(r"^login/", "django.contrib.auth.views.login", {"template_name": "timesheet/login.html"}, name="login"),
    url(r"^logout/", "django.contrib.auth.views.logout_then_login", {"login_url": settings.LOGIN_URL}, name="logout"),
    url(r"^customer/(\d+)/report/(\d{4})/(\d{1,2})/", "timesheet.views.customer_report", {"format_identifier": "html"}, name="customer_report_year_month"),
    url(r"^customer/(\d+)/report/(\d{4})/", "timesheet.views.customer_report", {"month": None, "format_identifier": "html"}, name="customer_report_year"),
    url(r"^customer/(\d+)/report.csv/(\d{4})/(\d{1,2})/", "timesheet.views.customer_report", {"format_identifier": "csv"}, name="customer_report_year_month_csv"),
    url(r"^customer/(\d+)/report.csv/(\d{4})/", "timesheet.views.customer_report", {"month": None, "format_identifier": "csv"}, name="customer_report_year_csv"),
    url(r"^customer/(\d+)/report/", "timesheet.views.customer_report", {"year": None, "month": None, "format_identifier": "html"}, name="customer_report"),
    url(r"css/main.css", "timesheet.views.main_css", name="main_css"),
    url(r"^reports/monthly.csv/(\d{4})/(\d{1,2})/", "timesheet.views.monthly_report_csv", name="monthly_report_csv"),
    url(r"^reports/timestatistics.csv/(\d{4})/(\d{1,2})", "timesheet.views.monthly_time_statistics_csv", name="monthly_time_statistics_csv")
)
