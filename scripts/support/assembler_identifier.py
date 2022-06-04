
from enums import IdentifierType

class AssemblerIdentifier:
  def __init__(self, identifier_name: str, file_name: str, line: int, type: IdentifierType):
    self._identifier_name = identifier_name
    self._file_name = file_name
    self._line = line
    self._type = type

  @property
  def identifier_name(self) -> str:
    return self._identifier_name

  @property
  def file_name(self) -> str:
    return self._file_name

  @property
  def line(self) -> int:
    return self._line

  @property
  def type(self) -> IdentifierType:
    return self._type