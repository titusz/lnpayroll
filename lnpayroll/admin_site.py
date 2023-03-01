# -*- coding: utf-8 -*-
from django.contrib.admin import AdminSite


class LnPayrollAdminSite(AdminSite):
    def get_app_list(self, request, app_label=None):
        """Customize admin app names and ordering"""
        applist = super().get_app_list(request, app_label)

        ordered = {
            "lnpayroll": "LnPayroll",
            "constance": "Configuration",
            "admin_interface": "Branding",
            "auth": "Users",
        }

        new_applist = []
        for app_label, name in ordered.items():
            for app in applist:
                if app.get("app_label") == app_label:
                    app["name"] = name
                    new_applist.append(app)

        return new_applist
