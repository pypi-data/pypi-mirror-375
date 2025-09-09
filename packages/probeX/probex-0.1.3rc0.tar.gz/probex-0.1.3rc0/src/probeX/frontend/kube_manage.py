import streamlit as st

from probeX.framework.service.kube_service import KubeService
from probeX.framework.config.environment import env_config


kubeservice = KubeService()

# Kubernetes管理页面
def show_kube_manage_page():
    st.header("Kubernetes管理")

    envconfig_name = env_config.name if env_config and hasattr(env_config, "name") else "未知环境"
    envconfig_host = env_config.host if env_config and hasattr(env_config, "host") else "未知地址"
    st.write(f"当前环境: {envconfig_name} - {envconfig_host}")

    namespace = st.text_input("命名空间", "airs-citest")
    st.write(f"当前命名空间: {namespace}")

    # 在此处把二维列表打印到页面


    if st.button("查看GPU占用情况"):
        gpu_table = kubeservice.get_gpu_resources(namespace=namespace)
        st.subheader("GPU占用情况")
        st.table(gpu_table)
    if st.button("检查微服务镜像"):
        st.info("这里展示镜像检查结果（待接入后端）")
    # 可扩展更多K8s相关功能
