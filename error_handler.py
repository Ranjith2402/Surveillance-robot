import os
import time

strf_time_format = '%d-%b-%Y at %H:%M:%S'
path = '/storage/emulated/0/Robot/Error_log/'


def write_log(log: str, who: str = 'App'):
    with open(f'{path}{who} crashed on {time.strftime(strf_time_format)}.txt', 'w+') as file:
        file.write(log)


def list_logs():
    try:
        ls = os.listdir(f'{path}')
        return ls
    except PermissionError:
        return None


def remove_log(_path: str):
    if path in list_logs():
        os.remove(_path)
