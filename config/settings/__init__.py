from decouple import config
if config('ENV') == 'DEV':
    from .local import *
else:
    from .prod import *
