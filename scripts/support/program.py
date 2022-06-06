class Program:
  def __init__(self, name: str, file: str):
    self._name = name
    self._file = file

  @property
  def name(self) -> str:
    return self._name

  @property
  def file(self) -> str:
    return self._file
