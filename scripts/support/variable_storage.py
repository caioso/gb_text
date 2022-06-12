from enums import StorageType

class VariableStorage:
  def __init__(self, storage: StorageType, address: str = ""):
    self._storage = storage
    self._address = address

  @property
  def storage(self) -> StorageType:
    return self._storage

  @property
  def address(self) -> str:
    return self._address