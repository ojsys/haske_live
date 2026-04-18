import os
import pymysql
pymysql.install_as_MySQLdb()

# Load .env file into os.environ so get_secret() can read it via os.getenv
from pathlib import Path
_env_file = Path(__file__).resolve().parent.parent.parent / '.env'
if _env_file.exists():
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _, _val = _line.partition('=')
                _key = _key.strip()
                _val = _val.strip().strip('"').strip("'")
                os.environ.setdefault(_key, _val)


def get_secret(secret_id, backup=None, default=None, cast=None):
    val = os.getenv(secret_id, backup if backup is not None else default)
    if cast is not None and val is not None:
        if cast is bool:
            return str(val).lower() in ('true', '1', 'yes')
        return cast(val)
    return val


if get_secret('PIPELINE') == 'production':
    from .production import *
else:
    from .local import *