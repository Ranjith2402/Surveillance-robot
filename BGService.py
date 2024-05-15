import time
import json
from android import PythonService


def background_thread(class_object):
    sleep_time = 5.0
    arguments = ()
    key_word_arguments = None

    kw_args = class_object.kw_args
    func = class_object.get_function
    class_object.toast = 'BGService running'

    if 'sleep_time' in kw_args:
        sleep_time = kw_args['sleep_time']
    if 'arguments' in kw_args:
        arguments = kw_args['arguments']
    if 'key_word_arguments' in kw_args:
        key_word_arguments = kw_args['key_word_arguments']

    while class_object.run:
        if key_word_arguments is not None:
            func(*arguments, **key_word_arguments)
        else:
            func(*arguments)
        if not class_object.run:
            break
        time.sleep(sleep_time)


intent = PythonService.mService.getIntent()

class_name = intent.getStringExtra('class_name')

cls = globals()[class_name]

cls_obj = cls()

while True:
    background_thread(cls_obj)
    time.sleep(5)
