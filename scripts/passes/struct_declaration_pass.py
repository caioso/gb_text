import os
import re
from typing import List, Tuple

from enums import BlockType
from constants import *
from support.assembler_identifier import AssemblerIdentifier
from support.block import Block
from support.data_structure import (
  DataStructure,
  convert_str_to_enum,
  convert_type_to_size
)
from support.function import Function
from utils import Utils

class StructDeclarationPass:
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
    self._functions = functions

  def process(self) -> Tuple[List[DataStructure], List[str]]:
    self._processed_source = self._raw_source
    data_structure_blocks = self._find_data_structure_blocks()
    data_structures, name_lines = self._parse_data_structure_name(data_structure_blocks)
    data_structures = self._parse_data_structure_fields(data_structures, name_lines, data_structure_blocks)
    return data_structures, self._processed_source

  def _find_data_structure_blocks(self):
    return [x for x in self._blocks if x.type == BlockType.DS_BLOCK]

  def _parse_data_structure_fields(self, data_structures: List[DataStructure], lines: List[int], blocks: List[Block]) -> List[DataStructure]:
    for idx, block in enumerate(blocks):
      offset = 0
      print(lines)
      for line in range(lines[idx] + 1, block.end):
        clear_line = Utils.extract_line_no_comments(self._raw_source[line])

        if re.match(ATTRIBUTE_DECLARATION_REGEX, clear_line):
          clear_line = clear_line.replace(',', ' ')
          tokens = Utils.split_tokens(clear_line)

          type = convert_str_to_enum(tokens[2], line, self._input_file)

          if Utils.is_valid_identifier(tokens[1]) == False:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: invalid data structure attribute identifier '{tokens[1]}'")

          data_structures[idx].register_attribute(tokens[1], type, offset, self._input_file, line)
          offset += convert_type_to_size(type)

          self._processed_source[line] = f";{self._processed_source[line]}"
        elif re.match(r"\b" + KEYWORD_ATTRIBUTE + r"\b", clear_line):
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: invalid attribute declaration")


    return data_structures

  def _parse_data_structure_name(self, data_structures: List[Block]) -> Tuple[List[DataStructure], List[int]]:
    ds = []
    positions = []
    for block in data_structures:
      for line in range(block.start, block.end):
        clear_line = Utils.extract_line_no_comments(self._raw_source[line])

        if len(clear_line) != 0:
          # Expect DS name sa first valid line in the block
          if re.match(NAME_REGEX, clear_line):
            tokens = Utils.split_tokens(clear_line)

            data_structure_names = [x.name for x in ds]
            assembly_names = [x.identifier_name for x in self._identifiers]
            function_names = [x.name for x in self._functions]
            if tokens[1] in data_structure_names:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: multiple definitions of data structure '{tokens[1]}'")
            if tokens[1] in assembly_names:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: multiple definitions of identifier '{tokens[1]}'")
            if tokens[1] in function_names:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: multiple definitions of identifier '{tokens[1]}'")
            if Utils.is_valid_identifier(tokens[1]) == False:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: invalid data structure identifier '{tokens[1]}'")

            ds.append(DataStructure(tokens[1]))
            positions.append(line)
            self._processed_source[line] = f";{self._processed_source[line]}"
            break
          elif re.match(r"\b" + KEYWORD_NAME + r"\b", clear_line):
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: invalid data structure name declaration")
          else:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: data structure name expected")
    return ds, positions
