from django.conf import settings


def admin_site_info(request):
    return {
        "ADMIN_SITE_HEADER": settings.ADMIN_SITE_HEADER,
        "ADMIN_SITE_TITLE": settings.ADMIN_SITE_TITLE,
    }
