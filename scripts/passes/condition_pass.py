import os
from typing import List, Tuple

from enums import BlockType
from constants import *
from support.assembler_identifier import AssemblerIdentifier
from support.function import Function
from support.block import Block
from support.condition import Condition
from utils import Utils

class ConditionPass:
  def  __init__(self,
                input_file: str,
                source: List[str],
                blocks: List[Block],
                identifiers: List[AssemblerIdentifier],
                functions: List[Function]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks
    self._identifiers = identifiers

  def process(self) -> None:
      for block in self._blocks:
        if block.type == BlockType.IF_BLOCK:
          self._validate_condition_header(block)
          self._parse_conditions(block)
          print(f"If at line {block.start}")
          for line in range(block.start, block.end):
            clear_line = Utils.extract_line_no_comments(self._raw_source[line])
            if len(clear_line) != 0:
              print (f"\t{self._raw_source[line][:-1]}")

  def _parse_conditions(self, block: Block) -> None:
    conditions = []
    for line in range(block.start, block.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line]).strip()

      if len(clear_line) != 0 and self._is_condition_line(clear_line):
        tokens = Utils.split_tokens(clear_line)
        conditional_operator_position = self._conditional_operator_positions(tokens)
        left_operand = self._extract_left_operand(tokens, conditional_operator_position, line)
        right_operand = self._extract_right_operand(tokens, conditional_operator_position, line)
        logic_operator = self._extract_logical_operand(tokens)
        conditions.append(Condition(left_operand,
                                    right_operand,
                                    tokens[conditional_operator_position],
                                    logic_operator))

    for cnd in conditions:
      print (f"Conditional operator at {conditional_operator_position} ({cnd.bool_operand})")
      print (f" left operand: {cnd.left_operand}")
      print (f" right operand: {cnd.right_operand}")
      print (f" logical operand: {cnd.logic_operand}")

  def _extract_logical_operand(self, tokens: List[str]) -> int:
    operand = ""
    if tokens[-1] in LOGICAL_OPERATORS:
      operand = tokens[-1]
    return operand

  def _extract_left_operand(self, tokens: List[str], cnd_op_pos: int, line: int) -> int:
    if len(tokens) <= 1 or \
       tokens[cnd_op_pos - 1] == KEYWORD_CND:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                         f"{line + 1}: expected lhs operand in '{KEYWORD_CND}' statement")

    operand = ""
    for position in range(1, cnd_op_pos):
        operand += f"{tokens[position]} "
        if tokens[position] in LOGICAL_OPERATORS:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{line + 1}: unexpected '{tokens[position]}' in '{KEYWORD_CND}' statement")

    return operand[:-1]

  def _extract_right_operand(self, tokens: List[str], cnd_op_pos: int, line: int) -> int:
    if cnd_op_pos + 1 >= len(tokens) or \
       tokens[cnd_op_pos + 1] in LOGICAL_OPERATORS or \
       tokens[cnd_op_pos - 1] == KEYWORD_CND:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                         f"{line + 1}: expected rhs operand in '{KEYWORD_CND}' statement")

    operand = ""
    for position in range(cnd_op_pos + 1, len(tokens)):
        if tokens[position] not in LOGICAL_OPERATORS:
          operand += f"{tokens[position]} "
        elif tokens[position] in LOGICAL_OPERATORS and \
             position != len(tokens) -1:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{line + 1}: unexpected '{tokens[position]}' in '{KEYWORD_CND}' statement")

    return operand[:-1]

  def _conditional_operator_positions(self, tokens: List[str]) -> int:
    position = -1
    for idx, token in enumerate(tokens):
      if token in CONDITIONAL_OPERATORS:
        position = idx
        break

    return position

  def _validate_condition_header(self, block: Block) -> None:
    in_condition_list = False
    in_body = False
    condition_counter = 0
    first_condition_index = 0

    for line in range(block.start, block.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line]).strip()
      if len(clear_line) != 0:
        if in_condition_list == False and in_body == False:
          in_condition_list = self._is_condition_line(clear_line)
          in_body = not self._is_condition_line(clear_line)

          if in_condition_list == True:
            first_condition_index = line
        elif  in_condition_list == True and in_body == False:
          condition_counter += 1
          in_condition_list = self._is_condition_line(clear_line)
          in_body = not self._is_condition_line(clear_line)
        elif  in_condition_list == False and in_body == True:
          if self._is_condition_line(clear_line):
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: unexpected '{KEYWORD_CND}' found")

    self._validate_boolean_operators(block, condition_counter, first_condition_index)

  def _validate_boolean_operators(self, block: Block, condition_counter:int, first: int) -> None:
    if condition_counter == 0:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                          f"{block.start + 1}: '{KEYWORD_CND}' statement expected in blk '{KEYWORD_IF}'")

    if condition_counter == 1:
      clear_line = Utils.extract_line_no_comments(self._raw_source[first]).strip()
      tokens = Utils.split_tokens(clear_line)

      if tokens[-1] in LOGICAL_OPERATORS:
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                           f"{first + 1}: unexpected '{tokens[-1]}' found")
    else:
      for position in range(first, first + condition_counter):
        clear_line = Utils.extract_line_no_comments(self._raw_source[position]).strip()
        tokens = Utils.split_tokens(clear_line)

        if tokens[-1] not in LOGICAL_OPERATORS and position < first + condition_counter - 1:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                            f"{position + 1}: expected '{tokens[-1]}' found")
        elif tokens[-1] in LOGICAL_OPERATORS and position == first + condition_counter - 1:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{position + 1}: unexpected '{tokens[-1]}' found")

  def _is_condition_line(self, line:str) -> bool:
    tokens = Utils.split_tokens(line)

    if KEYWORD_CND in tokens[0]:
      return True
    else:
      return False