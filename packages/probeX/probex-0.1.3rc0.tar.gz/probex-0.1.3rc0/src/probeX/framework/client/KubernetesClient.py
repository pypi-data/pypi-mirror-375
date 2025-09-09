from kubernetes import client, config, watch
from kubernetes.stream import stream
from kubernetes.client.exceptions import ApiException
from pathlib import Path
from collections import defaultdict
import csv

from probeX.framework.config.env import PROBE_HOME
from probeX.framework.config.Config import config as airs_config
from probeX.framework.utils.utils import print_table
from probeX.framework.utils.utils import get_now_time_str
from probeX.framework.config.environment import env_config
from probeX.framework.utils.log import test_logger as logger


class KubernetesClient:

    _DEFAULT_CONFIG_FILE_PATH = Path(PROBE_HOME).joinpath("config", "kube_config",
                                              env_config.kube_config_file).__str__()

    def __init__(self):
        config.kube_config.load_kube_config(config_file=self._DEFAULT_CONFIG_FILE_PATH)

    @property
    def core_api(self):
        return client.CoreV1Api()

    @property
    def batch_api(self):
        return client.BatchV1Api()

    @property
    def custom_api(self):
        return client.CustomObjectsApi()

    @property
    def events_api(self):
        return client.CoreV1Event()

    def get_namespaces(self):
        for ns in self.core_api.list_namespace().items:
            print(ns.metadata)

    def get_pytorch_job_detail(self, job_name, namespace="airs"):
        """
        Args:
            job_name:
            namespace:

        Returns:
            dict{
                metadata
                spec
                status
                    conditions
                    lastReconciliTime
                    startTime
            }
        """
        try:
            pytorch_job = self.custom_api.get_namespaced_custom_object(
                group="kubeflow.org",
                version="v1",
                namespace=namespace,
                plural="pytorchjobs",
                name=job_name
            )
            return pytorch_job
        except client.exceptions.ApiException as e:
            status = e.status
            logger.error(f"Exception when calling CustomObjectsApi->list_namespaced_custom_object.{status}")

    def delete_pods(self, pods_info):
        """
        pods_info: list.
        [
            {"namespace": namespace, "pod_name": pod_name}
        ]
        """
        for pod in pods_info:
            self.core_api.delete_namespaced_pod(name=pod['pod_name'], namespace=pod['namespace'])

    def get_airs_pod_restart(self):
        # 获取指定命名空间中的所有 Pod
        pods = self.core_api.list_namespaced_pod(namespace="airs-citest")
        result = {}
        # 遍历每个 Pod，提取重启次数
        for pod in pods.items:
            pod_name = pod.metadata.name
            for container_status in pod.status.container_statuses:
                container_name = container_status.name
                restart_count = container_status.restart_count
                result[f"{pod_name}-{container_name}"] = restart_count
        return result

    def exec_shell_in_pod(self,namespace, podname, shell_commond):
        return stream(self.core_api.connect_get_namespaced_pod_exec,
              podname,
              namespace,
              command=shell_commond,
              stderr=True, stdin=False,
              stdout=True, tty=False)
    
    def delete_compl_pod(self):
        try:
            # 获取所有 Pod
            pods = self.core_api.list_namespaced_pod(namespace="airs")
            # 遍历 Pod 并删除状态为 Succeeded 的
            for pod in pods.items:
                if pod.status.phase == "Succeeded":
                    name = pod.metadata.name
                    namespace = pod.metadata.namespace
                    self.core_api.delete_namespaced_pod(name=name, namespace=namespace)
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Namespace {namespace} not found.")
            else:
                logger.warning(f"Error occurred while listing Pods in namespace {namespace}: {e}")

    def update_pod_running_time(self, duration):
        try:
            resource = self.custom_api.get_cluster_custom_object(
                group="kwok.x-k8s.io",
                version="v1alpha1",
                plural="stages",
                name="pod-complete-airs-job",
            )
            # 修改 spec.delay.durationMilliseconds 的值
            resource["spec"]["delay"]["durationMilliseconds"] = duration
            
            # 更新资源
            updated_resource = self.custom_api.replace_cluster_custom_object(
                group="kwok.x-k8s.io",
                version="v1alpha1",
                plural="stages",
                name="pod-complete-airs-job",
                body=resource,
            )
            logger.info("kwok pod running time updated!")
        except client.exceptions.ApiException as e:
            print(f"发生错误: {e}")

    def get_job_creation_time(self, job_name):
        job = self.batch_api.read_namespaced_job(job_name, "default")
        return job.metadata.creation_timestamp

    def get_first_pod_creation_time(self, job_name):
        api_instance = client.CoreV1Api()
        pods = api_instance.list_namespaced_pod(namespace="default", label_selector=f"job-name={job_name}")
        if pods.items:
            first_pod = min(pods.items, key=lambda pod: pod.metadata.creation_timestamp)
            return first_pod.metadata.creation_timestamp
        return None

    def get_last_pod_completion_time(self, job_name):
        api_instance = client.CoreV1Api()
        pods = api_instance.list_namespaced_pod(namespace="default", label_selector=f"job-name={job_name}")
        pods = sorted(pods.items, key=lambda pod: pod.metadata.creation_timestamp, reverse=True)
        for pod in pods:
            for condition in pod.status.conditions:
                if condition.type == "ContainersReady" and condition.status == "True":
                    return condition.last_transition_time
        return None

    def get_last_pod_completion_time(self):
        # 获取与该 Job 相关的所有事件
        events = self.events_api.list_namespaced_event(namespace="airs-citest", field_selector=f"involvedObject.name={job_name}")
        pod_completion_events = [event for event in events.items if
                                 event.reason == "Completed" and "pod" in event.involved_object.name]
        if pod_completion_events:
            # 对事件按最后时间戳排序
            sorted_events = sorted(pod_completion_events, key=lambda event: event.last_timestamp, reverse=True)
            last_event = sorted_events[0]
            return last_event.last_timestamp
        else:
            return None

    def get_gpu_usage(self, namespace: str):
        # 查询命名空间下的所有 Pod
        result_list = [["pod_id", "gpu_type", "request_num"]]
        pods = self.core_api.list_namespaced_pod(namespace=namespace)
        for pod in pods.items:
            for container in pod.spec.containers:
                if container.resources and container.resources.requests:
                    resource = container.resources.requests
                    gpu_types = [key for key in resource if key not in {"cpu", "memory"}]
                    for gpu_type in gpu_types:
                        result_list.append([pod.metadata.name, gpu_type, int(container.resources.requests[gpu_type])])
        print(f"GPU 资源使用情况(命名空间: {namespace}):")
        print_table(result_list)
        return result_list

    def check_microservice_images(self, namespace, save_csv=True):
        """
        检查命名空间 'airs-citest' 下所有微服务的镜像、版本号及其 digest，并保存到 CSV 文件
        """
        try:
            pods = self.core_api.list_namespaced_pod(namespace=namespace)
            result_list = [["Container Name", "Image", "Digest"]]
            for pod in pods.items:
                if pod.status.phase != "Running":
                    result_list.append([pod.metadata.name, f"pod status {pod.status.phase}", "-"])
                    continue
                for container in pod.spec.containers:
                    container_name = container.name
                    image = container.image
                    # 获取镜像的 digest
                    image_digest = \
                    self.core_api.read_namespaced_pod(pod.metadata.name, namespace).status.container_statuses[
                        0].image_id
                    result_list.append([container_name, image, image_digest])

            if save_csv:
                # 保存到 CSV 文件
                image_check_result = Path(PROBE_HOME).joinpath("release",
                                                                      f"microservice_images_{get_now_time_str()}.csv").__str__()
                with open(image_check_result, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(result_list)
                print(f"检查结果已保存到 {image_check_result}")
            return result_list
        except ApiException as e:
            logger.error(f"获取命名空间 '{namespace}' 下的镜像信息时发生错误: {e}")


    def diff_release_images(self, namespace):
        """
        对比两个 CSV 文件中的镜像信息，找出新增、删除和版本变更的镜像
        """
        release_images_filt = Path(PROBE_HOME).joinpath("release", "release.csv").__str__()
        diff_result = [["Container Name", "Release_Image", "Release_Digest", "Env_Image", "Env_Digest", "Is_Same"]]
        # 读取旧数据
        old_data = {}
        with open(release_images_filt, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["Container Name"]
                old_data[key] = (row["Image"], row["Digest"])
        # 处理新数据（跳过表头）
        new_data = {}
        new_result_list = self.check_microservice_images(namespace=namespace, save_csv=False)
        for row in new_result_list[1:]:
            key = row[0]
            new_data[key] = (row[1], row[2])

        # 对比数据
        for k,v in old_data.items():
            if k not in new_data:
                diff_result.append([k, v[0], v[1], "N/A", "N/A", "No"])
            else:
                new_image, new_digest = new_data[k]
                if v[0] != new_image or v[1] != new_digest:
                    diff_result.append([k, v[0], v[1], new_image, new_digest, "No"])
                else:
                    diff_result.append([k, v[0], v[1], new_image, new_digest, "Yes"])
        # 保存到 CSV 文件
        image_diff_result = Path(PROBE_HOME).joinpath("release",
                                                       f"diff_images_{get_now_time_str()}.csv").__str__()
        with open(image_diff_result, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(diff_result)
        print(f"检查结果已保存到 {image_diff_result}")


kc = KubernetesClient()

if __name__ == "__main__":
    kc.monitor_pytorchjob_pods("job-775af08e-1641-46dc-8714-26754b1c9e45")
