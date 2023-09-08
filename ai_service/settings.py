from pathlib import Path

from split_settings.tools import include, optional

include(
    'components/base.py',
    'components/database.py',
    optional('local_settings.py')
)
