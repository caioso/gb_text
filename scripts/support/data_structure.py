import os
from typing import List

class Attribute:
  def __init__(self, name: str, offset: int):
    self._name = name
    self._offset = offset

  @property
  def name(self) -> str:
    return self._name

  @property
  def offset(self) -> int:
    return self._offset

class DataStructure:
  def __init__(self, name: str):
    self._name = name
    self._attributes = []

  @property
  def name(self) -> str:
    return self._name

  @property
  def attribures(self) -> List[Attribute]:
    return self._attributes

  def register_attribute(self, name: str, offset: int, file: str, line: int) -> None:

    for att in self._attributes:
      if att.name == name:
        raise RuntimeError(f"{os.path.basename(file)} line " +
                              f"{line + 1}: multiple definitions of attribute'{name}' " +
                              f"in data structu '{self._name}'")
    self._attributes.append(Attribute(name, offset))
