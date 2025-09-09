
from probeX.framework.client.KubernetesClient import kc

class KubeService:

    def get_kube_config(self):
        """Get kube config

        Returns:
            _type_: _description_
        """
        return kc.get_kube_config()

    def get_gpu_resources(self, namespace):
        """Get availb resource in namespace

        Args:
            namespace (str): kubernetes namespace

        Returns:
            _type_: _description_
        """
        return kc.get_gpu_usage(namespace)


    def image_check(self, namespace):
        """Check microservice image in namespace

        Args:
            namespace (str): kubernetes namespace

        Returns:
            _type_: _description_
        """
        return kc.check_microservice_images(namespace)

    def image_diff_release(self, namespace):
        """Check microservice image in namespace

        Args:
            namespace (str): kubernetes namespace
            release (str): release version

        Returns:
            _type_: _description_
        """
        return kc.diff_release_images(namespace)
