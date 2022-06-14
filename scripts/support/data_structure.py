import os

from enum import Enum
from typing import List
from constants import *

class AttributeType(Enum):
  BYTE = "BYTE"
  HALF = "HALF"
  WORD = "WORD"
  LONG = "LONG"

def convert_str_to_enum(type_text: str, line: int, file_name: str) -> AttributeType:
  text = type_text.upper()
  if text == AttributeType.BYTE.value:
    return AttributeType.BYTE
  elif text == AttributeType.HALF.value:
    return AttributeType.HALF
  elif text == AttributeType.WORD.value:
    return AttributeType.WORD
  elif text == AttributeType.LONG.value:
    return AttributeType.LONG
  else:
    raise RuntimeError(f"{os.path.basename(file_name)} line " +
                       f"{line + 1}: invalid data type '{type_text}'")


def convert_type_to_size(type: AttributeType) -> int:
  if type == AttributeType.BYTE:
    return 1
  elif type == AttributeType.HALF:
    return 2
  elif type == AttributeType.WORD:
    return 4
  elif type == AttributeType.LONG:
    return 8


class Attribute:
  def __init__(self, name: str, type: AttributeType, offset: int):
    self._name = name
    self._offset = offset
    self._type = type

  @property
  def name(self) -> str:
    return self._name

  @property
  def offset(self) -> int:
    return self._offset

  @property
  def type(self) -> AttributeType:
    return self._type

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

  def register_attribute(self, name: str, type: AttributeType, offset: int, file: str, line: int) -> None:

    for att in self._attributes:
      if att.name == name:
        raise RuntimeError(f"{os.path.basename(file)} line " +
                              f"{line + 1}: multiple definitions of attribute'{name}' " +
                              f"in data structu '{self._name}'")
    self._attributes.append(Attribute(name, type, offset))

def get_basic_type_size(type_name: str, line:int, file:str) -> int:
  size = 0
  if type_name.lower() == KEYWORD_BYTE:
    size = 1
  elif type_name.lower() == KEYWORD_HALF:
    size = 2
  elif type_name.lower() == KEYWORD_WORD:
    size = 4
  elif type_name.lower() == KEYWORD_LONG:
    size = 8
  else:
    raise RuntimeError(f"{os.path.basename(file)} line " +
                        f"{line + 1}: invalid type '{type_name}'")
  print(f"type_name {size}")
  return size

def get_struct_type_size(type: DataStructure, line:int, file:str) -> int:
  size = 0
  for att in type.attribures:
    size += get_basic_type_size(att.type.value, line, file)
  print(f"struct_type_name {size}")
  return size