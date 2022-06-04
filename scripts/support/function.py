from .block import Block
from constants import *

class Function:
  def __init__(self, name: str, block: Block):
    self._name = name
    self._block = block
    self._label = f"fn__{self._name}"

  @property
  def name(self) -> str:
    return self._name

  @property
  def block(self) -> Block:
    return self._block

  @property
  def label(self) -> str:
    return self._label
