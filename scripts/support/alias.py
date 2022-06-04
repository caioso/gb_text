from enums import LabelOperation

class Alias:
  def __init__(self, position: int, name: str, register: str,
                 op: LabelOperation, parent_block_id: int):
    self._position = position
    self._name = name
    self._register = register
    self._op = op
    self._parent_block_id = parent_block_id

  @property
  def position(self) -> int:
    return self._position

  @property
  def parent_block_id(self) -> int:
    return self._parent_block_id

  @property
  def name(self) -> str:
    return self._name

  @property
  def register(self) -> str:
    return self._register

  @property
  def operation(self) -> LabelOperation:
    return self._op