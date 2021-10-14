import os

print(os.listdir('proyectoORT'))
print("Creating Firebase config file from env var FB_ADMIN_CONFIG")
with open('proyectoORT/fbAdminConfig.json', 'w') as fb_config_file:
    fb_config_file.write(os.environ['FB_ADMIN_CONFIG'])
print(os.listdir('proyectoORT'))

from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectoORT.settings')
print("Applying migrations")
execute_from_command_line(['manage.py', 'migrate'])

if os.environ['CREATE_SUPERUSER']:
    print("Creating superuser")
    execute_from_command_line(['manage.py', 'createsuperuser', '--no-input', '--username', os.environ['ADMIN_USERNAME'], '--email', 'noemail@example.com'])
else:
    print("Skipping superuser creation")