from injector import Injector, inject, Inject


class A:
    def hello(self):
        return "Hello"


def check(a: A | None = Inject[A]) -> str:
    print(f"a type: {type(a)}")
    if a:
        return a.hello()
    elif a is None:
        return "No A"

    if not a:
        print("Falsy A")

    return "Unexpected Type, what is this"


if __name__ == "__main__":
    container = Injector()
    container.binder.bind(A, to=None)
    print(check())
