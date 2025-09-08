from injectq import InjectQ
from injectq.decorators.inject import inject


class A:
    def hello(self):
        return "Hello"


@inject
def check(a: A | None) -> str:
    print("Checking A:", type(a))
    print("A class:", a.__class__)
    if a:
        return a.hello()

    print(isinstance(a, A))

    if a is None:
        return "No A"

    if not a:
        print("Falsy A")

    return "Unexpected Type, what is this"


if __name__ == "__main__":
    container = InjectQ.get_instance()
    container.bind(A, None, allow_none=True)
    print("Graph:", container.get_dependency_graph())
    print(check())
