import streamlit as st

from probeX.framework.config.environment import env_config




# Kubernetes管理页面
def show_env_manage_page():
    st.header("环境管理")

    envconfig_name = env_config.name if env_config and hasattr(env_config, "name") else "未知环境"
    envconfig_host = env_config.host if env_config and hasattr(env_config, "host") else "未知地址"
    st.write(f"当前环境: {envconfig_name} - {envconfig_host}")
