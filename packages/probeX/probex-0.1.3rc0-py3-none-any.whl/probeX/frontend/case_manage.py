import streamlit as st
import os
from pathlib import Path
import ast
import subprocess
import hashlib

# Case管理页面

def find_test_files(cases_dir: Path):
    """递归查找 pytest 测试文件（以 test_*.py 或 *_test.py 命名）。"""
    if not cases_dir.exists():
        return []
    files = []
    for p in cases_dir.rglob('*.py'):
        name = p.name
        if name.startswith('test_') or name.endswith('_test.py'):
            files.append(p)
    files.sort()
    return files


def parse_tests_from_file(file_path: Path):
    """解析单个文件，返回测试函数和类方法的节点ID列表（用于 pytest 运行提示）。
    返回格式: list of (nodeid, display_name)
    nodeid 例如: path/to/test_file.py::test_func 或 path/to/test_file.py::TestClass::test_method
    """
    results = []
    try:
        src = file_path.read_text(encoding='utf-8')
        tree = ast.parse(src)
    except Exception:
        return results

    for node in tree.body:
        # 顶层函数
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            nodeid = f"{file_path}::%s" % node.name
            results.append((nodeid, node.name))
        # 顶层类，查找含测试方法的类
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name.startswith('test_'):
                    nodeid = f"{file_path}::%s::%s" % (class_name, sub.name)
                    results.append((nodeid, f"{class_name}.{sub.name}"))
    return results


def make_relative_nodeid(file_path: Path, cases_dir: Path, label: str) -> str:
    """生成相对于 cases_dir 的 pytest nodeid。
    label 可能是 'test_func' 或 'TestClass.test_method'。
    返回格式：rel/path/to/file.py::test_func 或 rel/path/to/file.py::TestClass::test_method
    """
    try:
        rel = file_path.relative_to(cases_dir)
    except Exception:
        rel = file_path
    rel_str = str(rel)
    if '.' in label:
        parts = label.split('.', 1)
        node = f"{rel_str}::{parts[0]}::{parts[1]}"
    else:
        node = f"{rel_str}::{label}"
    return node


def show_case_manage_page():
    # 增宽主容器并减少左右留白，改善左右布局拥挤问题
    st.markdown(
        """
        <style>
        /* 扩展主内容区域宽度并减小左右内边距 */
        .main .block-container{max-width:1400px; padding-left:16px; padding-right:16px;}
        /* 减小 expander 内部间距 */
        .streamlit-expanderHeader {padding: 6px 8px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.header("Module Case管理")
    st.write("管理&运行 pytest 格式的测试用例。")

    # 决定测试用例目录：优先使用环境变量 PROBE_HOME 下的 cases/，否则使用仓库内 ./cases
    probe_home = os.environ.get('PROBE_HOME')
    if probe_home:
        default_dir = Path(probe_home).joinpath('cases')
    else:
        default_dir = Path.cwd().joinpath('cases')

    st.text(f"测试用例目录: {default_dir}")

    # 允许用户覆盖目录
    cases_dir_input = st.text_input('测试用例目录路径（可覆盖）', str(default_dir), key='cases_dir_input')
    cases_dir = Path(cases_dir_input.strip()) if cases_dir_input else default_dir

    # 找到所有测试文件并按相对目录分组
    files = find_test_files(cases_dir)
    if not files:
        st.warning('未找到任何 pytest 风格的用例文件（test_*.py 或 *_test.py）。')
        return

    groups = {}
    for f in files:
        try:
            rel = f.relative_to(cases_dir).parent
        except Exception:
            rel = f.parent
        rel_key = str(rel) if str(rel) != '.' else '.'
        groups.setdefault(rel_key, []).append(f)

    # 左右两列布局：左侧目录导航，右侧显示文件和用例
    # 使��更大比例让右侧内容区更宽
    left_col, right_col = st.columns([1, 5])

    # 左侧目录导航
    with left_col:
        st.subheader('case目录')
        dir_list = ['.'] + sorted(k for k in groups.keys() if k != '.')
        # 保持选中状态
        if 'selected_dir' not in st.session_state:
            st.session_state['selected_dir'] = dir_list[0]
        selected_dir = st.radio('选择目录', dir_list, index=dir_list.index(st.session_state['selected_dir']) if st.session_state['selected_dir'] in dir_list else 0, key='dir_radio')
        st.session_state['selected_dir'] = selected_dir
        if st.button('刷新用例列表', key='refresh_left'):
            st.experimental_rerun()

        st.markdown('---')
        st.write(f'共 {len(files)} 个测试文件，{len(groups)} 个目录')

    # 右侧显示选中目录或全部目录下的文件和测试
    with right_col:
        st.subheader('用例列表')
        show_files = []
        if selected_dir == '.' or selected_dir == '.':
            # 展示根目录
            key_dir = '.'
            show_files = sorted(groups.get(key_dir, []))
        else:
            show_files = sorted(groups.get(selected_dir, []))

        # 操作按钮放在右侧顶部
        run_all = st.button('运行全部用例', key='run_all_right')
        run_selected = st.button('运行选中用例', key='run_selected_right')

        selected_nodeids = []
        # 列出文件和测试（文件使用 expander）
        for idx_f, f in enumerate(show_files):
            tests = parse_tests_from_file(f)
            with st.expander(f.name, expanded=False):
                st.write(f"路径: {f}")
                if not tests:
                    st.error('未在此文件中找到 test_* 函数或类方法。')
                else:
                    for idx_t, (nodeid, label) in enumerate(tests):
                        cb_key = f"cb_{selected_dir}_{idx_f}_{idx_t}_" + hashlib.md5((str(f) + '::' + label).encode()).hexdigest()
                        checked = st.checkbox(label, key=cb_key)
                        if checked:
                            selected_nodeids.append(make_relative_nodeid(f, cases_dir, label))

        # 如果运行全部，则收集所有 nodeids（只针对选中目录）
        if run_all:
            all_nodeids = []
            for f in show_files:
                for _n, label in parse_tests_from_file(f):
                    all_nodeids.append(make_relative_nodeid(f, cases_dir, label))
            selected_nodeids = all_nodeids

        # 运行选中或全部
        if run_selected or run_all:
            if not selected_nodeids:
                st.warning('请先选择要运行的用例或确保目录中有用例。')
            else:
                st.info(f'开始运行 {len(selected_nodeids)} 个用例，可能需要一些时间...')
                try:
                    cmd = ['pytest', '-q'] + selected_nodeids
                    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(cases_dir))
                    output = proc.stdout
                    st.text_area('pytest 输出', value=output, height=400, key='pytest_output')
                    if proc.returncode == 0:
                        st.success('用例执行成功（全部通过）')
                    else:
                        st.error(f'用例执行结束，pytest 返回码 {proc.returncode}，请查看输出定位失败项。')
                except FileNotFoundError:
                    st.error('未找到 pytest 命令，请确保在运行环境中已安装 pytest 并可用。')
                except Exception as e:
                    st.error(f'运行用例时发生异常: {e}')

    st.write('提示：可以通过修改测试用例目录或在文件中添加 test_ 函数来扩展用例。')


# 兼容旧接口名
show_case_manage_page_alias = show_case_manage_page
