import os
import datetime

from . import config as cfg


def get_new_data_dir(prefix=None, create_dir=True):
    """"""
    prefix = f'{prefix}_' if prefix is not None else ''

    # try several times to prevent collisions
    while True:
        time_str = str(datetime.datetime.now()).replace(':', '-').replace(' ', '_')
        path = os.path.join(cfg.ROOT_DIR, f'{prefix}{time_str}')

        if not os.path.exists(path):
            if create_dir:
                os.mkdir(path)
            return path
