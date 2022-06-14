import os

from numpy import var

from enums import (
  BlockMarkerType,
  BlockType,
  StorageType
)
from constants import *
from support.data_structure import (
  DataStructure,
  get_basic_type_size,
  get_struct_type_size
)
from support.variable import Variable
from typing import List

class Block:
  def __init__(self, start: int, end: int,  type: BlockType, id: int):
    self._start = start
    self._end = end
    self._type = type
    self._id = id
    self._variables = []

  @property
  def start(self) -> int:
    return self._start

  @property
  def end(self) -> int:
    return self._end

  @property
  def id(self) -> int:
    return self._id

  @property
  def type(self) -> BlockType:
    return self._type

  @property
  def variables(self) -> List[Variable]:
    return self._variables

  def register_variable(self, var: Variable, line: int, file: str) -> None:
    names = self._get_variable_names()
    if var.name in names:
      fisrt = [x for x in self._variables if x.name == var.name][0]
      raise RuntimeError(f"{os.path.basename(file)} line " +
                         f"{line + 1}: variable '{var.name}' defined multiple times under " +
                         f"the same scope (first found in line {fisrt.position + 1})")

    if var.storage.storage == StorageType.HEAP_STORAGE:
      addresses = self._get_variable_address()
      if var.storage.address in addresses:
        raise RuntimeError(f"{os.path.basename(file)} line " +
                          f"{line + 1}: multiple variable definitions at the same address '{var.storage.address}'")

    self._variables.append(var)

  def get_stack_allocation_size(self, structs: List[DataStructure], line: int, file: str) -> int:
    stack_vars = [x for x in self._variables if x.storage.storage == StorageType.STACK_STORAGE]
    stack_space = 0
    for var in stack_vars:
      if var.type in VARIABLE_BASIC_TYPES:
        stack_space += get_basic_type_size(var.type, line, file)
      else:
        struct_type = [x for x in structs if x.name == var.type][0]
        if struct_type != None:
          stack_space += get_struct_type_size(struct_type, line, file)
        else:
          raise RuntimeError(f"{os.path.basename(file)} line " +
                          f"{line + 1}: invalid data type '{var.type}'")
    return stack_space

  def _get_variable_names(self) -> List[str]:
    return [x.name for x in self._variables]

  def _get_variable_address(self) -> List[str]:
    return [x.storage.address for x in self._variables if x.storage.storage == StorageType.HEAP_STORAGE]


class BlockMarker:
  def __init__(self, position: int, type: BlockMarkerType):
    self._position = position
    self._type = type

  @property
  def position(self) -> int:
    return self._position

  @property
  def type(self) -> BlockMarkerType:
    return self._type