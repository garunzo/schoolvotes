import bjoern
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "surveys.settings")

application = get_wsgi_application()

bjoern.run(application, "127.0.0.1", 8000)
