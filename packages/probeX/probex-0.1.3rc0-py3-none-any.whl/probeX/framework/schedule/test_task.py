from prefect import Task, Flow


class TestTask(Task):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        print("Hello World")


if __name__ == "__main__":
    with Flow("test") as flow:
        t1 = TestTask(name="t1")()
        t2 = TestTask(name="t2")()

        # 设置task_2依赖于task_1
        t1 >> t2

    flow.run()
