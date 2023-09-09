from pathlib import Path

from split_settings.tools import include, optional
from dotenv import load_dotenv

load_dotenv()

include(
    'components/base.py',
    'components/database.py',
    'components/rest_framework.py',
    optional('local_settings.py')
)
