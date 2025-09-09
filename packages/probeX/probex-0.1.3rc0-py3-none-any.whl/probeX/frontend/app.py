import streamlit as st
from kube_manage import show_kube_manage_page
from case_manage import show_case_manage_page
from system_manage import show_sys_manage_page
from env_manage import show_env_manage_page

st.sidebar.title("PROBEX")

# 使用 session_state 持久化页面选择，避免在点击页面内按钮时丢失选中页面
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = None

with st.sidebar.expander("系统管理", expanded=True):
    if st.button("项目管理"):
        st.session_state["selected_page"] = "项目管理"
    if st.button("kube管理"):
        st.session_state["selected_page"] = "kube管理"
    if st.button("env管理"):
        st.session_state["selected_page"] = "env管理"


with st.sidebar.expander("用例管理", expanded=True):
    if st.button("Module Case管理"):
        st.session_state["selected_page"] = "Module Case管理"
    # 可扩展更多用例管理页面


# 使用 session_state 中的值决定显示哪个页面
selected_page = st.session_state.get("selected_page")

if selected_page == "kube管理":
    show_kube_manage_page()
elif selected_page == "env管理":
    show_env_manage_page()
elif selected_page == "Module Case管理":
    show_case_manage_page()
elif selected_page == "项目管理":
    show_sys_manage_page()

# ...其他页面
