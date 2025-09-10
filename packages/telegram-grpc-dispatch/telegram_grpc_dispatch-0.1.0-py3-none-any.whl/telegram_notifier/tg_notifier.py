from .notifier_utils.config import get_notifier_config
from .serve import serve


def tg_notifier():
    serve(config=get_notifier_config())
