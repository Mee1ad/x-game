import functools
import traceback
import sys
import os
from django.http import JsonResponse


def try_except(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            type = sys.exc_info()[0].__name__
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            trace = {'Type': type, 'Description': f'{exc_obj}', 'File': fname, 'Line': exc_tb.tb_lineno}
            return JsonResponse(trace, status=500)
    return wrapper
