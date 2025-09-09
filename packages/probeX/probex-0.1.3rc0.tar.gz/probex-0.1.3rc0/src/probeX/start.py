import argparse
import sys
from probeX.framework.service.swagger_service import SwaggerService
from probeX.framework.service.kube_service import KubeService
from probeX.framework.service.case_service import CaseService
from probeX.framework.service.report_serve_service import start_report_server
from probeX.framework.service.report_serve_service import stop_report_server
from probeX.framework.service.report_serve_service import status_report_server
from probeX.framework.utils.log import test_logger as logger
from probeX.framework.config.env import PROBE_HOME
from probeX.framework.utils.OTP import gen_secret_key_from_pic

kube_service = KubeService()
swagger_service = SwaggerService()
case_service = CaseService()


def init_system():
    if PROBE_HOME not in sys.path:
        sys.path.insert(0, PROBE_HOME)


def parse_swagger(args):
    logger.info("ProbeX will parse swagger2.0 doc.")
    swagger_service.parse_swagger()


def list_swagger(args):
    print("list")


def kube_resources(args):
    kube_service.get_gpu_resources("airs")


def kube_image_check(args):
    kube_service.image_check(namespace=args.namespace)

def kube_image_diff(args):
    kube_service.image_diff_release(namespace=args.namespace)


def execute_test_flow(args):
    case_service.execute_case(args.file)


def gen_otp(args):
    gen_secret_key_from_pic(args.file)


def parser_commands():
    # 创建主解析器
    parser = argparse.ArgumentParser(description="ProbeX测试平台.",
                                     epilog="示例用法：")
    subparsers = parser.add_subparsers(dest="command", required=True, help="可用的子命令")

    # 创建用户操作解析
    user_parser = subparsers.add_parser("user", help="用户操作")
    user_subparsers = user_parser.add_subparsers(dest="action", required=True, help="用户操作管理")
    user_subparsers_otp = user_subparsers.add_parser("otp", help="用户OTP生成.")
    user_subparsers_otp.add_argument("-f", "--file", type=str, help="otp二维码文件")
    user_subparsers_otp.set_defaults(func=gen_otp)

    # 创建swagger解析
    swagger_parser = subparsers.add_parser("swagger", help="swagger2.0接口文档管理")
    swagger_subparsers = swagger_parser.add_subparsers(dest="action", required=True, help="swagger 文档操作")
    # swagger parse
    swagger_subparsers_parse = swagger_subparsers.add_parser("parse", help="解析swagger2.0文档, 文档路径见配置文件中\
                                                                                    swagger_api_dir字段(系统路径);")
    swagger_subparsers_parse.set_defaults(func=parse_swagger)
    # swagger list
    swagger_subparsers_list = swagger_subparsers.add_parser("list", help="swagger2.0 API列表")
    swagger_subparsers_list.set_defaults(func=list_swagger)

    # 创建kube操作解析
    kube_parser = subparsers.add_parser(name="kube", help="kube工具.")
    kube_subparsers = kube_parser.add_subparsers(dest="action", required=True, help="kube集群操作")
    # 统计kube集群中GPU资源占用
    kube_subparsers_resource = kube_subparsers.add_parser(name="resource", help="查询kubernetes集群资源统计")
    kube_subparsers_resource.set_defaults(func=kube_resources)
    # 检查kube集群中微服务镜像
    kube_subparsers_image = kube_subparsers.add_parser(name="image_check", help="检查kubernetes集群中微服务镜像")
    kube_subparsers_image.add_argument("-n", "--namespace", type=str, help="命名空间, 默认为airs-citest",
                                       required=False, default="airs-citest")
    kube_subparsers_image.set_defaults(func=kube_image_check)
    # kube image diff
    kube_subparsers_image_diff = kube_subparsers.add_parser(name="image_diff", help="检查kubernetes集群中微服务镜像")
    kube_subparsers_image_diff.add_argument("-n", "--namespace", type=str, help="命名空间, 默认为airs-citest",
                                       required=False, default="airs-citest")
    kube_subparsers_image_diff.set_defaults(func=kube_image_diff)

    # 创建case执行解析
    case_parser = subparsers.add_parser(name="case", help="case执行.")
    case_parser.add_argument("-f", "--file", help="测试文件")
    case_parser.set_defaults(func=execute_test_flow)

    # report一级命令 report
    report_parser = subparsers.add_parser("report", help="测试报告工具")
    report_sub = report_parser.add_subparsers(dest="action", required=True)
    # report二级命令 server
    server_parser = report_sub.add_parser("server", help="报告服务")
    server_cmd = server_parser.add_subparsers(dest="server_cmd", required=True)
    # report server start
    start = server_cmd.add_parser("start", help="启动报告服务")
    start.set_defaults(func=start_report_server)
    # report server stop
    stop = server_cmd.add_parser("stop", help="停止报告服务")
    stop.set_defaults(func=stop_report_server)
    # report server status
    status = server_cmd.add_parser("status", help="查看服务状态")
    status.set_defaults(func=status_report_server)

    # 解析命令行参数
    args = parser.parse_args()
    # 调用对应的处理函数
    args.func(args)


def main():
    init_system()
    parser_commands()


    
 
if __name__ == "__main__":
    main()
