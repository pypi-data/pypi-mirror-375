from collections import defaultdict, deque


class DependencyManager:
    def __init__(self, cases):
        """
        初始化依赖管理器
        :param cases: 测试用例列表，每个用例包含 'name', 'dependencies' 等信息
        """
        self.cases = cases
        self.graph = defaultdict(list)  # 依赖图
        self.in_degree = defaultdict(int)  # 入度记录
        self.case_names = set()  # 所有测试用例名称
        self.sorted_cases = None

    def build_dependency_graph(self):
        """
        构建依赖关系图
        """
        for case in self.cases:
            self.case_names.add(case['name'])
            # 处理每个依赖
            for dep in case['dependencies']:
                self.graph[dep].append(case['name'])  # 依赖关系：dep -> case
                self.in_degree[case['name']] += 1     # case 的入度增加
            if case['name'] not in self.in_degree:
                self.in_degree[case['name']] = 0  # 如果某个用例没有被其他用例依赖，入度为0

    def topological_sort(self):
        """
        执行拓扑排序，返回正确的执行顺序
        :return: 排序后的测试用例名称列表
        """
        queue = deque([case for case in self.case_names if self.in_degree[case] == 0])  # 入度为0的节点
        sorted_cases = []

        while queue:
            case = queue.popleft()
            sorted_cases.append(case)

            for neighbor in self.graph[case]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 如果排序后的节点数与所有用例数相等，则排序成功
        if len(sorted_cases) == len(self.case_names):
            self.sorted_cases = sorted_cases
            return sorted_cases
        else:
            raise ValueError("存在环依赖，无法进行拓扑排序")

    def draw_sequence_of_execution(self):
        print("测试用例执行顺序为:")
        print(" --> ".join(self.sorted_cases))


    def draw_dependency_graph(self):
        """
        使用 ASCII 字符绘制依赖关系图并打印到控制台
        """
        print("测试用例依赖拓扑图:")

        # 获取拓扑排序结果
        sorted_cases = self.topological_sort()
        # 构建一个反转的图（从用例到其依赖的节点）
        reverse_graph = defaultdict(list)
        for node, dependents in self.graph.items():
            for dependent in dependents:
                reverse_graph[dependent].append(node)
        visited = set()
        def print_case(case, level=0):
            """递归打印用例及其依赖关系"""
            if case in visited:
                return
            visited.add(case)
            print(" " * (level * 4) + f"--> {case}")
            for dependency in reverse_graph[case]:
                print_case(dependency, level + 1)

        # 按拓扑排序的顺序打印用例及其依赖
        for case in sorted_cases:
            if case not in visited:
                print_case(case)

# 示例测试用例
cases = [
    {
        "name": "test1",
        "action": "Model.create",
        "params": [{"modelname": "test"}, {"modeltype": "NLP"}],
        "return": ["model_res", "model_path"],
        "dependencies": ["test2", "test3"]
    },
    {
        "name": "test2",
        "action": "Model.load",
        "params": [{"modelname": "test"}],
        "return": ["model"],
        "dependencies": []
    },
    {
        "name": "test3",
        "action": "Data.prepare",
        "params": [{"dataset": "data"}],
        "return": ["prepared_data"],
        "dependencies": []
    },
]

if __name__ == "__main__":
    # 初始化依赖管理器
    manager = DependencyManager(cases)

    # 构建依赖关系图
    manager.build_dependency_graph()

    # 执行拓扑排序
    try:
        sorted_cases = manager.topological_sort()
        print("测试用例执行顺序：", sorted_cases)
    except ValueError as e:
        print("拓扑排序失败：", e)

    # 绘制依赖关系图
    manager.draw_dependency_graph()
