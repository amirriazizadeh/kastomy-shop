from django.contrib import admin
from django.utils.html import format_html

# admin.py


# Customize admin site header, title, and index title
admin.site.site_header = "Kastomy Shop Admin"
admin.site.site_title = "Kastomy Shop Admin Portal"
admin.site.index_title = "Welcome to Kastomy Shop Admin"

# To customize logo, color, and footer, override admin templates.
# Create a folder: your_app/templates/admin/
# Copy and edit these templates:
# - base_site.html (for logo, title, footer)
# - base.html (for colors)

# Example: In base_site.html, add your logo and footer:
# {% extends "admin/base.html" %}
# {% block branding %}
#   <img src="{% static 'images/logo.png' %}" alt="Logo" height="40">
#   <h1 id="site-name">{{ site_header|default:_('Django administration') }}</h1>
# {% endblock %}
# {% block footer %}
#   <div class="footer">© 2024 Kastomy Shop</div>
# {% endblock %}

# Example: In base.html, add custom CSS for colors:
# <link rel="stylesheet" type="text/css" href="{% static 'css/custom_admin.css' %}">

# In custom_admin.css, override colors:
# .module h2 { background: #4CAF50; color: white; }
# .header { background: #333; color: #fff; }

# Don't forget to collect static files and configure STATICFILES_DIRS.