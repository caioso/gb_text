from enum import Enum

class LabelOperation(Enum):
  DEF_LABEL = "DEF_LABEL"
  UNDEF_LABEL = "UNDEF_LABEL"

class BlockMarkerType(Enum):
  BLOCK_DECL = "BLOCK_DECL"
  BLOCK_BGN = "BLOCK_BGN"
  BLOCK_END = "BLOCK_END"

class BlockType(Enum):
  GENERIC_BLOCK = "GENERIC_BLOCK"
  IF_BLOCK = "IF_BLOCK"
  LP_BLOCK = "LP_BLOCK"
  FNC_BLOCK = "FNC_BLOCK"
  DS_BLOCK = "DS_BLOCK"
  PRG_BLOCK = "PRG_BLOCK"
  NONE_BLOCK = "NONE_BLOCK" # Used to mark an 'end' token

class FunctionArgumentType(Enum):
  IN_ARG = "IN_ARG"
  OUT_ARG = "OUT_ARG"

class IdentifierType(Enum):
  NAMED_CONSTANT = "NAMED_CONSTANT"
  MACRO = "MACRO"
  LABEL = "LABEL"

class ConditionalOperand(Enum):
  REGISTER = "REGISTER"
  MEMORY_ALIAS = "MEMORY_ALIAS"
  NUMBER = "NUMBER"
  INVALID = "INVALID"

class StorageType(Enum):
  STACK_STORAGE = "STACK_STORAGE"
  HEAP_STORAGE = "HEAP_STORAGE"