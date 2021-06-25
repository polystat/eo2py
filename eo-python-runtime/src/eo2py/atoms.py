from abc import abstractmethod
from functools import partial
from typing import List, Union, Optional


class Object:
    @abstractmethod
    def dataize(self) -> "Atom":
        raise NotImplementedError()


class Atom(Object):
    @abstractmethod
    def dataize(self) -> "Atom":
        raise NotImplementedError()

    @abstractmethod
    def data(self) -> object:
        raise NotImplementedError()


class Attribute(Object):
    def __init__(self, obj: Object, name: str):
        self.obj = obj
        self.name = name
        self.args: List[Object] = []

    def __call__(self, *args: Object):
        self.args.extend(args)
        return self

    def __str__(self):
        return f"{self.obj}.{self.name}"

    def dataize(self) -> Object:
        attr: Optional[Object]
        if hasattr(self.obj, self.name):
            print(f"Found .{self.name} in {self.obj}.")
            attr = getattr(self.obj, self.name)
        elif hasattr(self.obj, "__PHI__"):
            print(
                f"Did not find .{self.name} in {self.obj}, searching for .{self.name} in {self.obj}'s "
                f"__PHI__ attribute: {self.obj.__PHI__}."
            )
            attr = Attribute(self.obj.__PHI__, self.name)
        else:
            print(f"Attribute .{self.name} was not found. Dataizing {self.obj}...")
            attr = None

        if attr is not None:
            if callable(attr):
                print(f"Dataizing {attr} applied to {[str(arg) for arg in self.args]}.")
                res = attr()
                for arg in self.args:
                    res = res(arg)
                return res.dataize()
            else:
                print(f"Dataizing {attr}, no args needed.")
                return attr.dataize()

        if hasattr(self.obj, "__PHI__") and hasattr(self.obj.__PHI__, "__PHI__"):
            return Attribute(self.obj.__PHI__, self.name).dataize()
        return getattr(self.obj.dataize(), self.name)(*self.args).dataize()


class DataizationError(Object):
    def dataize(self) -> None:
        raise NotImplementedError()


class ApplicationError(Exception):
    def __init__(self, arg):
        super().__init__(f"Object cannot be copied with {arg} as argument")


class Number(Atom):
    def __init__(self, value: Union[int, float]):
        self.value = value
        self.Add = partial(NumberAdd, self)
        self.Sub = partial(NumberSub, self)
        self.Pow = partial(NumberPow, self)
        self.Less = partial(NumberLess, self)
        self.Mul = partial(NumberMul, self)
        self.Leq = partial(NumberLeq, self)

    def dataize(self) -> "Number":
        return self

    def data(self) -> Union[int, float]:
        return self.value

    def __eq__(self, other) -> "Boolean":
        return Boolean("true" if self.data() == other.data() else "false")

    def __add__(self, other) -> "Number":
        return Number(self.value + other.value)

    def __lt__(self, other) -> "Boolean":
        return Boolean("true" if self.data() < other.data() else "false")

    def __le__(self, other) -> "Boolean":
        return self == other or self < other

    def __sub__(self, other) -> "Number":
        return Number(self.value - other.value)

    def __mul__(self, other) -> "Number":
        return Number(self.value * other.value)

    def __pow__(self, power, modulo=None) -> "Number":
        return Number(self.value ** power.value)

    def __str__(self):
        return f"Number({self.value})"


class Boolean(Atom):
    def __init__(self, value: Union[str, bool]):
        self.value: bool
        if isinstance(value, str):
            value = value.lower().strip()
            assert value == "true" or value == "false"
            self.value = value == "true"
        elif isinstance(value, bool):
            self.value = value
        else:
            raise AttributeError("Boolean: value should be either str or bool")

        self.If = partial(BooleanIf, self)

    def dataize(self) -> "Boolean":
        return self

    def data(self) -> bool:
        return self.value

    def __bool__(self):
        return self.data()

    def __str__(self):
        return f"Boolean({bool(self)})"

    def __eq__(self, other):
        return Boolean(bool(self) == bool(self))


class NumberAdd(Number):
    def __init__(self, parent: Number):
        super().__init__(0)
        self.parent = parent

        self.attributes = ["other"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self) -> Number:
        return self.parent.dataize() + self.other.dataize()


class NumberSub(Number):
    def __init__(self, parent: Number):
        super().__init__(0)
        self.parent = parent

        self.attributes = ["other"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self) -> Number:
        return self.parent.dataize() - self.other.dataize()


class NumberMul(Number):
    def __init__(self, parent: Number):
        super().__init__(0)
        self.parent = parent
        self.attributes = ["other"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self) -> Number:
        return self.parent.dataize() * self.other.dataize()


class BooleanIf(Boolean):
    def __init__(self, parent: Boolean):
        super().__init__("false")
        self.parent = parent

        # Free attributes
        self.attributes = ["if_true", "if_false"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self) -> Object:
        return (
            self.if_true.dataize() if self.parent.dataize() else self.if_false.dataize()
        )


class NumberLess(Boolean):
    def __init__(self, parent: Number):
        super().__init__("false")
        self.parent = parent

        self.attributes = ["other"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self):
        return self.parent.dataize() < self.other.dataize()


class NumberLeq(Boolean):
    def __init__(self, parent: Number):
        super().__init__("false")
        self.parent = parent

        self.attributes = ["other"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self):
        return self.parent.dataize() <= self.other.dataize()


class NumberPow(Number):
    def __init__(self, parent: Number):
        super().__init__(0)
        self.parent = parent

        self.attributes = ["other"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self):
        return self.parent.dataize() ** self.other.dataize()


class Array(Atom):
    def __init__(self):
        self.Get = partial(ArrayGet, self)
        self.attributes = ["elements"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter == 0:
            setattr(self, self.attributes[self.application_counter], [])
            self.application_counter += 1
        getattr(self, self.attributes[0]).append(arg)
        return self

    def dataize(self) -> "Array":
        return self

    def data(self) -> List:
        return [elem.dataize().data() for elem in self.elements]

    def __getitem__(self, item: Object):
        if isinstance(item, Number):
            assert isinstance(item.value, int)
            index = item.dataize().data()
            assert isinstance(index, int)
            return self.elements[index]
        else:
            raise AttributeError(f"{item} is not an instance of Number!")


class ArrayGet(Object):
    def __init__(self, arr):
        self.arr = arr

        self.attributes = ["i"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self):
        return self.arr[self.i]


class String(Atom):
    def __init__(self, value: str):
        self.value = value

    def dataize(self) -> "String":
        return self

    def data(self) -> str:
        return self.value

    def __str__(self):
        return self.value


class Sprintf(String):
    def __init__(self):
        super().__init__("")
        self.attributes = ["fmt", "args"]
        self.application_counter = 0

    def __call__(self, arg: Object):
        if self.application_counter == 1:
            getattr(self, self.attributes[1]).append(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
            setattr(self, self.attributes[self.application_counter], [])
        return self

    def dataize(self) -> Object:
        print(self.args)
        return String(str(self.fmt) % tuple(arg.dataize().data() for arg in self.args))


class Stdout(Atom):
    def __init__(self):
        # Free attributes
        self.attributes = ["text"]
        self.application_counter = 0

    def __call__(self, arg: String):
        if self.application_counter >= len(self.attributes):
            raise ApplicationError(arg)
        else:
            setattr(self, self.attributes[self.application_counter], arg)
            self.application_counter += 1
        return self

    def dataize(self) -> Object:
        print(self.text.dataize())
        return self

    def data(self):
        return None


def lazy_property(fn):
    attr = "_lazy__" + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr):
            value = fn(self)
            setattr(self, attr, value)
        return getattr(self, attr)

    return _lazy_property
