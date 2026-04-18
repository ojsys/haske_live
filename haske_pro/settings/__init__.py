import os
import pymysql
pymysql.install_as_MySQLdb()


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