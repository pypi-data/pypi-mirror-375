import importlib
import yaml
class InstanceContext:
    def __init__(self):
        self._instance_cache = {}

    def get_or_create_instance(self, class_name, package_name="airstest.model", force_reinitialize=False, **kwargs):
        """ 获取实例，若实例不存在或需要强制重新初始化，则创建新实例 """
        if class_name in self._instance_cache and not force_reinitialize:
            print(f"Using cached instance of {class_name}")
            return self._instance_cache[class_name]
        else:
            print(f"Creating new instance of {class_name}")
            # 动态导入类所在模块
            try:
                module = importlib.import_module(f"{package_name}.{class_name.lower()}")
                cls = getattr(module, class_name)
                instance = cls(**kwargs)  # 使用参数初始化实例
                self._instance_cache[class_name] = instance  # 缓存实例
                return instance
            except ModuleNotFoundError:
                raise ValueError(f"Module {class_name} not found in package {package_name}")
            except AttributeError:
                raise ValueError(f"Class {class_name} not found in module {package_name}.{class_name.lower()}")


    def initialize_from_yaml_data(self, yaml_data, package_name):
        """ 从 YAML 文件初始化类实例并存入上下文 """
        # 存储每个对象的引用
        initialized_instances = {}

        for entry in yaml_data:
            name = entry["name"]
            class_name = entry["class"]
            values = entry["values"]
            # 处理 values 中的依赖
            resolved_values = {}
            for key, value in values.items():
                if isinstance(value, dict) and "{" in str(value):
                    ref_name = value.get("user")  # 获取依赖对象名称
                    resolved_values[key] = initialized_instances.get(ref_name)  # 获取依赖对象
                else:
                    resolved_values[key] = value

            # 初始化实例
            instance = self.get_or_create_instance(package_name, class_name, **resolved_values)
            initialized_instances[name] = instance

        return initialized_instances