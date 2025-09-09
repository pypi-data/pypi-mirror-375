import streamlit as st
import os
import yaml
from pathlib import Path
from datetime import datetime

# 读取配置文件
def load_probe_config(config_path):
    if not Path(config_path).exists():
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

# 保存配置文件
def save_probe_config(config_path, config_data):
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_data, f, allow_unicode=True)

# 可视化编辑配置
def show_sys_manage_page():
    st.header("项目管理")
    probe_home = os.environ.get("PROBE_HOME", "未设置")
    st.text(f"测试项目地址: {probe_home}")
    config_path = os.path.join(probe_home, "config", "probe_config.yaml")
    st.text(f"配置文件路径: {config_path}")

    # 只在首次加载时初始化 session_state
    if "yaml_content" not in st.session_state:
        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                st.session_state["yaml_content"] = f.read()
        else:
            st.session_state["yaml_content"] = ""
            st.warning("未找到配置文件或配置为空！")

    st.subheader("配置文件内容（可直接编辑原始YAML）")
    st.markdown("<style>.yaml-box textarea {background:#f7f7fa;font-family:monospace;font-size:15px;border-radius:8px;border:1px solid #d3d3e7;}</style>", unsafe_allow_html=True)

    # 使用 form 保证在提交时处理逻辑原子执行，避免交互导致选中页面丢失
    with st.form(key="config_form"):
        with st.container():
            st.markdown('<div class="yaml-box">', unsafe_allow_html=True)
            # 避免与 session_state 键冲突，给 widget 使用不同的 key
            edited = st.text_area("probe_config.yaml", value=st.session_state["yaml_content"], height=500, label_visibility="visible", key="yaml_content_area")
            st.markdown('</div>', unsafe_allow_html=True)
        submit = st.form_submit_button("保存配置")

    if submit:
        if probe_home == "未设置" or not Path(probe_home).exists():
            st.error("PROBE_HOME 环境变量未设置或路径不存在，无法保存配置！")
        else:
            config_dir = os.path.dirname(config_path)
            if not Path(config_dir).exists():
                st.error(f"配置文件目录不存在: {config_dir}")
            else:
                try:
                    with open(config_path, "w", encoding="utf-8") as f:
                        f.write(edited)
                    # 更新保存的 session_state（widget 使用的是 yaml_content_area，因此可以安全更新 yaml_content）
                    st.session_state["yaml_content"] = edited  # 更新 session_state
                    st.success("配置已保存！")

                except Exception as e:
                    st.error(f"保存失败: {e}")
