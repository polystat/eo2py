# This file was auto-generated by eo2py-maven-plugin
# on 2021.07.03 at 20:57:01. Don't edit it,
# your changes will be discarded on the next build.
# The sources were compiled to XML
# by the EO compiler v.0.1.25.

from eo2py.atoms import *
from functools import partial

"""
[] > array
  * > @
    "string"
    true
    *
      "another array"
      1
      2
      3
    4
    5


[] > app
  stdout > @
    sprintf
      "%s %s %s %s %s %s %s %s"
      array.get 0
      array.get 1
      (array.get 2).get 0
      (array.get 2).get 1
      (array.get 2).get 2
      (array.get 2).get 3
      array.get 3
      array.get 4

<EOF>
"""


class EOarray(ApplicationMixin, Object):
    def __init__(self):
        self.attr__self = self
        self.attr__parent = DataizationError()

        self.attributes = []

    @property
    def attr__phi(self):
        return Array()((String("string")))((Boolean("true")))(
            Array()((String("another array")))((Number(1)))((Number(2)))((Number(3)))
        )((Number(4)))((Number(5)))


class EOapp(ApplicationMixin, Object):
    def __init__(self):
        self.attr__self = self
        self.attr__parent = DataizationError()

        self.attributes = []

    @property
    def attr__phi(self):
        return Stdout()(
            Sprintf()((String("%s %s %s %s %s %s %s %s")))(
                Attribute((EOarray()), "get")((Number(0)))
            )(Attribute((EOarray()), "get")((Number(1))))(
                Attribute((Attribute((EOarray()), "get")((Number(2)))), "get")(
                    (Number(0))
                )
            )(
                Attribute((Attribute((EOarray()), "get")((Number(2)))), "get")(
                    (Number(1))
                )
            )(
                Attribute((Attribute((EOarray()), "get")((Number(2)))), "get")(
                    (Number(2))
                )
            )(
                Attribute((Attribute((EOarray()), "get")((Number(2)))), "get")(
                    (Number(3))
                )
            )(
                Attribute((EOarray()), "get")((Number(3)))
            )(
                Attribute((EOarray()), "get")((Number(4)))
            )
        )


def test_arrays(capsys):
    assert EOapp().dataize()
    assert "string True another array 1 2 3 4 5" in capsys.readouterr().out
