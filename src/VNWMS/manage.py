#!/usr/bin/env python
import os
import sys

from VNWMS.settings.base import DEBUG

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'VNWMS.settings.production')

    # from django.conf import settings
    # if DEBUG:
    #     if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
    #         import debugpy
    #         debugpy.listen(("0.0.0.0", 3000))
    #         print('Attached!')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
