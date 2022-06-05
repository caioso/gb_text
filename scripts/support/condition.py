from support.assembler_identifier import AssemblerIdentifier

class Condition:
  def __init__(self, left_op: str, right_op: str, boolean_op: str, logic_op: str):
    self._left_operand = left_op
    self._right_operand = right_op
    self._bool_operand = boolean_op
    self._logic_operand = logic_op

  @property
  def left_operand(self) -> str:
    return self._left_operand

  @property
  def right_operand(self) -> str:
    return self._right_operand

  @property
  def bool_operand(self) -> str:
    return self._bool_operand

  @property
  def logic_operand(self) -> str:
    return self._logic_operand

  def validate_conditin(self) -> None:
    return