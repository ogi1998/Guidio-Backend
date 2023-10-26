import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email constants
ACTIVATE_ACCOUNT_SUBJECT = 'Activate your account'

