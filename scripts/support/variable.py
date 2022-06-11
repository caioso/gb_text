from enums import StorageType
from support.variable_storage import VariableStorage

class Variable:
  def __init__(self, position: int, name: str, type: str, storage: VariableStorage):
    self._position = position
    self._name = name
    self._type = type
    self._storage = storage

  @property
  def position(self) -> int:
    return self._position

  @property
  def name(self) -> str:
    return self._name

  @property
  def type(self) -> str:
    return self._type

  @property
  def storage(self) -> VariableStorage:
    return self._storage