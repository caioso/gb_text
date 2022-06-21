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

class StackAllocationEntry:
  def __init__(self, variable: Variable, offset: int, size: int):
    self._variable = variable
    self._offset = offset
    self._size = size

  @property
  def variable(self) -> Variable:
    return self._variable

  @property
  def offset(self) -> int:
    return self._offset

  @property
  def size(self) -> int:
    return self._size

class HeapAllocationEntry:
  def __init__(self, variable: Variable, address: int, size: int):
    self._variable = variable
    self._address = address
    self._size = size

  @property
  def variable(self) -> Variable:
    return self._variable

  @property
  def address(self) -> int:
    return self._address

  @property
  def size(self) -> int:
    return self._size


class Block:
  def __init__(self, start: int, end: int,  type: BlockType, id: int):
    self._start = start
    self._end = end
    self._type = type
    self._id = id
    self._variables = []
    self._stack_allocation_map = []
    self._heap_allocation_map = []

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

  @property
  def stack_allocation_map(self) -> List[StackAllocationEntry]:
    return self._stack_allocation_map

  @property
  def heap_allocation_map(self) -> List[HeapAllocationEntry]:
    return self._heap_allocation_map

  def register_variable(self, var: Variable, structs: List[DataStructure], line: int, file: str) -> None:
    names = get_variable_names(self._variables)
    if var.name in names:
      first = [x for x in self._variables if x.name == var.name][0]
      raise RuntimeError(f"{os.path.basename(file)} line " +
                         f"{line + 1}: variable '{var.name}' defined multiple times under " +
                         f"the same scope (first found in line {first.position + 1})")

    if var.storage.storage == StorageType.HEAP_STORAGE:
      addresses = get_variable_address(self._variables)
      if var.storage.address in addresses:
        raise RuntimeError(f"{os.path.basename(file)} line " +
                          f"{line + 1}: multiple variable definitions at the same address '{var.storage.address}'")

    self._variables.append(var)

    if var.storage.storage == StorageType.STACK_STORAGE:
      self._generate_stack_allocation_map(structs)
    elif var.storage.storage == StorageType.HEAP_STORAGE:
      self._generate_heap_allocation_map(structs)

  def _generate_stack_allocation_map(self, structs: List[DataStructure]) -> None:
    self._stack_allocation_map = []

    stack_vars = [x for x in self._variables if x.storage.storage == StorageType.STACK_STORAGE]
    stack_offset = 0
    for var in stack_vars:
      size = 0

      if var.type in VARIABLE_BASIC_TYPES:
        size = get_basic_type_size(var.type, 0, "")
      else:
        struct_type = [x for x in structs if x.name == var.type][0]
        if struct_type != None:
          size = get_struct_type_size(struct_type, 0, "")

      self._stack_allocation_map.append(StackAllocationEntry(var, stack_offset, size))
      stack_offset += size

  def _generate_heap_allocation_map(self, structs: List[DataStructure]) -> None:
    self._heap_allocation_map = []

    stack_vars = [x for x in self._variables if x.storage.storage == StorageType.HEAP_STORAGE]
    for var in stack_vars:
      if var.type in VARIABLE_BASIC_TYPES:
        size = get_basic_type_size(var.type, 0, "")
      else:
        struct_type = [x for x in structs if x.name == var.type][0]
        if struct_type != None:
          size = get_struct_type_size(struct_type, 0, "")

      self._heap_allocation_map.append(HeapAllocationEntry(var, var.storage.address, size))

def get_stack_allocation_size(variables: List[Variable], structs: List[DataStructure], line: int, file: str) -> int:
  stack_vars = [x for x in variables if x.storage.storage == StorageType.STACK_STORAGE]
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

def get_heap_allocation_size(variables: List[Variable], structs: List[DataStructure], line: int, file: str) -> int:
  heap_vars = [x for x in variables if x.storage.storage == StorageType.HEAP_STORAGE]
  total_heap = 0
  for var in heap_vars:
    if var.type in VARIABLE_BASIC_TYPES:
      total_heap += get_basic_type_size(var.type, line, file)
    else:
      struct_type = [x for x in structs if x.name == var.type][0]
      if struct_type != None:
        total_heap += get_struct_type_size(struct_type, line, file)
      else:
        raise RuntimeError(f"{os.path.basename(file)} line " +
                        f"{line + 1}: invalid data type '{var.type}'")
  return total_heap

def get_variable_names(variables: List[Variable]) -> List[str]:
  return [x.name for x in variables]

def get_variable_address(variables: List[Variable]) -> List[str]:
  return [x.storage.address for x in variables if x.storage.storage == StorageType.HEAP_STORAGE]


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