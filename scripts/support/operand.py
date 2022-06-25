from enums import *
from utils import *
from support.block import Block

class Operand:
  def __init__(self, operand_code: str, block: Block, line: int, file: str):
    self._line = line
    self._file = file
    self._operand_type = OperandType.INVALID_OPERAND
    self._parse_operand(operand_code, block)

  def _parse_operand(self, operand_code: str, block: Block) -> None:
    operand = operand_code.replace(',','')
    self._operand_name = ""
    self._operand_attr_name = ""
    self._operand_data_type = ""

    if '.' in operand:
      self._operand_name = operand.split('.')[0]
      self._operand_attr_name = operand.split('.')[1]
    else:
      self._operand_name = operand

    if self._operand_name in TOKEN_REGISTER:
      self._operand_type = OperandType.REGISTER_OPERAND
    elif re.match(NUMBER_REGEX, self._operand_name):
      self._operand_type = OperandType.LITERAL_OPERAND
    elif self._find_variable_declaration_in_block(self._operand_name, block):
      self._operand_data_type = self._get_variable_type(self._operand_name, block)
      self._operand_type = OperandType.VARIABLE_OPERAND

  def _get_variable_type(self, name:str, block: Block) -> str:
    for var in block.variables:
      if var.name == name:
        return var.type
    raise RuntimeError(f"{os.path.basename(self._file)} line " +
                       f"{self._line + 1}: unknown variable '{name}'")

  def _find_variable_declaration_in_block(self, name:str, block: Block) -> bool:
    if name in [x.name for x in block.variables]:
      return True
    raise RuntimeError(f"{os.path.basename(self._file)} line " +
                       f"{self._line + 1}: unknown variable '{name}'")

  @property
  def operand_type(self) -> OperandType:
    return self._operand_type

  @property
  def operand_name(self) -> str:
    return self._operand_name

  @property
  def operand_atrt_name(self) -> str:
    return self._operand_attr_name

  @property
  def operand_data_type(self) -> str:
    return self._operand_data_type
