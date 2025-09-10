from typing import Callable, Generic, TypeVar

Fn = TypeVar("Fn", bound=Callable)

class slicer(Generic[Fn]):
  def __init__(self, fn: Fn):
    self.fn = fn

  __getitem__: Fn = lambda self, key: self.fn(key)  # type: ignore
