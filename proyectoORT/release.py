import os
with open('proyectoORT/fbAdminConfig.json', 'w') as fb_config_file:
    fb_config_file.write(os.environ['FB_ADMIN_CONFIG'])

from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectoORT.settings')
execute_from_command_line(['manage.py', 'migrate'])
execute_from_command_line(['manage.py', 'createsuperuser', '--no-input', '--username', os.environ['ADMIN_USERNAME'], '--email', 'noemail@example.com'])