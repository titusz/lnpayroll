from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class LnPayrollConfig(AppConfig):
    name = "lnpayroll"
    verbose_name = "LIGHTNING PAYROLL"


class LnPayrollAdminConfig(AdminConfig):
    default_site = "lnpayroll.admin_site.LnPayrollAdminSite"
