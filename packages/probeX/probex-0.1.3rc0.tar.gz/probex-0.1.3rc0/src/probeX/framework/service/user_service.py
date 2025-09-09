import importlib
from probeX.framework.utils.log import test_logger


class UserFactory:
    @staticmethod
    def get_user(user_class, *args, **kwargs):
        try:
            user_package = user_class.split('.')[:-1]
            user_class = user_class.split('.')[-1]
            user_module = importlib.import_module(user_package)
            user = getattr(user_module, user_class)
            return user(*args, **kwargs)
        except (ModuleNotFoundError, AttributeError) as e:
            test_logger.error(f"错误: {e}")
            raise e