import os
import re
import sys
from typing import List

from constants import *
from enums import LabelOperation
from utils import Utils
from support.alias import Alias
from support.assembler_identifier import AssemblerIdentifier
from support.block import (
  Block
)

class RegisterAliasPass:
  def __init__(self,
               input_file: str,
               source: List[str],
               blocks: List[Block],
               identifiers: List[AssemblerIdentifier],
               functions: List[Block]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks
    self._identifiers = identifiers
    self._functions = functions

  @property
  def processed_source(self) -> List[str]:
    return self._processed_source

  def process(self) -> None:
    aliasses = self._locate_alias_operations()

    self._process_source(aliasses)
    self._correct_remaining_aliases(aliasses)

    return self._processed_source

  def _locate_alias_operations(self) -> List[Alias]:
    aliasses = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(ALIAS_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"

        proper_command = re.split(KEYWORD_ALIAS, clear_line)[1]
        target_alias = re.split(',', proper_command)[1].strip()
        target_register = re.split(',', proper_command)[0].strip()
        parent_block_id = Utils.find_parent_block_id(idx, self._blocks)

        if not Utils.is_valid_identifier(target_alias):
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                              f"{idx + 1}: Invalid identifier '{target_alias}' " +
                              f"detected")

        if not Utils.is_identifier_unique(self._identifiers, target_alias):
          identifier = [x for x in self._identifiers if x.identifier_name == target_alias][0]
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                              f"{idx + 1}: identifier '{target_alias}' " +
                              f"already defined in {identifier.file_name}, line {identifier.line + 1}")

        for alias in [x for x in aliasses if x.parent_block_id == parent_block_id]:
          if alias.name == target_alias:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: alias '{target_alias}' " +
                                "has already been defined in this scope")

        if parent_block_id == -1:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                              f"{idx + 1}: Aliasses must be declared inside of 'blk' scopes")

        aliasses.append(Alias(idx, target_alias,
                              target_register,
                              LabelOperation.DEF_LABEL, parent_block_id))
    return aliasses

  def _find_decendent_blocks(self, line_number: int) -> List[Block]:
    blocks = []
    for block in self._blocks:
      if line_number >= block.start and line_number <= block.end:
        blocks.append(block)

    return blocks

  def _process_source(self, aliasses: List[Alias]) -> None:
    self._processed_source = []
    names = [x.name for x in aliasses]
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)
      split_line = Utils.split_tokens(clear_line)

      for line_token in split_line:
        if line_token not in KEYWORDS and Utils.is_valid_identifier(line_token) and \
           not Utils.is_assembler_identifier(self._identifiers, line_token) and \
           line_token not in names and line_token not in self._functions:
            print (f"{os.path.basename(self._input_file)} line " +
                   f"{idx + 1}: Warning: Undeclared identifier '{line_token}'")

      line_text = line
      for line_token in split_line:
        for target_alias in [x for x in aliasses]:
          if re.search(r"\b" + (target_alias.name) + r"\b" , line_token):
            if target_alias.position > idx:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                f"{idx + 1}: Undeclared alias '{target_alias.name}'")
            line_text = line.replace(target_alias.name, target_alias.register)
            break

      self._processed_source.append(line_text)

  def _correct_remaining_aliases(self, aliasses: List[Alias]) -> None:
    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      for target_alias in aliasses:
        if re.search(r"\b" + (target_alias.name) + r"\b" , clear_line):
          decendent = [x.id for x in self._find_decendent_blocks(idx)]
          allowed_aliases = []
          for alias in aliasses:
            if idx >= alias.position and \
                alias.parent_block_id in decendent and \
                alias.name == target_alias.name:
                allowed_aliases.append(alias)

          if len(allowed_aliases) == 0:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                            f"{idx + 1}: Undeclared alias '{target_alias.name}'")
          else:
            candidate_alias = [x for x in allowed_aliases if x.name == target_alias.name]
            closest_index = -1
            min_diff = sys.maxsize
            for alias_index, alias in enumerate(candidate_alias):
              diff = abs(idx - alias.position)
              if min_diff >= diff:
                min_diff = diff
                closest_index = alias_index

            line_text = line.replace(target_alias.name, candidate_alias[closest_index].register)
            self._processed_source[idx] = line_text
