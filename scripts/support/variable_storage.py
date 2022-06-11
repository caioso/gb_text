from enums import StorageType

class VariableStorage:
  def __init__(self, storage: StorageType, address: int = -1, offset = -1):
    self._storage = storage
    self._address = address
    self._offset = offset

  @property
  def storage(self) -> StorageType:
    return self._storage

  @property
  def address(self) -> int:
    return self._address

  @property
  def offset(self) -> int:
    return self._offset