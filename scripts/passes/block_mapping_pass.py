from asyncio import constants
import os
import re
from typing import List, Tuple

from numpy import block

from constants import *
from enums import (
  BlockMarkerType,
  BlockType
)
from support.block import (
  Block,
  BlockMarker
)
from utils import Utils

class BlocksMappingPass:
  def __init__(self, input_file: str, source: List[str]):
    self._raw_source = source
    self._input_file = input_file

  def process(self) -> Tuple[List[str], List[Block]]:
    self._processed_source = self._raw_source
    self._detect_blocks()
    self._validate_blocks()
    blocks = self._generate_blocks()
    return self._processed_source, blocks

  def _detect_blocks(self) -> None:
    self._block_list = []
    self._block_type_list = []

    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)
      if re.match(BLOCK_HEADER_BLK_REGEX, clear_line) or \
         re.match(BLOCK_HEADER_PRG_REGEX, clear_line) or \
         re.match(BLOCK_HEADER_LP_REGEX, clear_line) or \
         re.match(BLOCK_HEADER_IF_REGEX, clear_line) or \
         re.match(BLOCK_HEADER_FN_REGEX, clear_line) or \
         re.match(BLOCK_HEADER_DS_REGEX, clear_line):
        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_DECL))
        self._block_type_list.append(self._detect_block_type(clear_line, idx))
      elif re.match(BGN_REGEX, clear_line) or \
           (KEYWORD_BGN[0] in clear_line or \
            KEYWORD_BGN[1] in clear_line):
          tokens = Utils.split_tokens(clear_line)
          if len(tokens) != 1:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: keyword '{KEYWORD_BGN[0]}' and "+
                               f"'{KEYWORD_BGN[1]}' must be the only token in the line")
          self._processed_source[idx] = f"; {line}"
          self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_BGN))
          self._block_type_list.append(self._detect_block_type(clear_line, idx))
      elif re.match(END_REGEX, clear_line)  or \
           (KEYWORD_END[0] in clear_line or \
            KEYWORD_END[1] in clear_line):
        tokens = Utils.split_tokens(clear_line)
        if len(tokens) != 1:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                              f"{idx + 1}: keyword '{KEYWORD_END[0]}' and "+
                              f"'{KEYWORD_END[1]}' must be the only token in the line")

        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_END))
        self._block_type_list.append(self._detect_block_type(clear_line, idx))

  def _detect_block_type(self, line: str, idx: int) -> BlockType:
    # This function assumes a clear line as input (no comments)
    tokens = Utils.split_tokens(line)

    if len(tokens) == 1:
      return BlockType.GENERIC_BLOCK
    elif len(tokens) == 2:
      if tokens[1] == KEYWORD_LOOP:
        return BlockType.LP_BLOCK
      elif tokens[1] == KEYWORD_IF:
        return BlockType.IF_BLOCK
      elif tokens[1] == KEYWORD_FUNCTION:
        return BlockType.FNC_BLOCK
      elif tokens[1] == KEYWORD_DATA_STRUCT:
        return BlockType.DS_BLOCK
      elif tokens[1] == KEYWORD_PROGRAM:
        return BlockType.PRG_BLOCK
      else:
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: invalid block type")
    else:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: invalid block structure")

  def _validate_blocks(self) -> None:
    block_stack = []
    for block in self._block_list:
      if block.type == BlockMarkerType.BLOCK_DECL:
        block_stack.append(1)
      elif block.type == BlockMarkerType.BLOCK_BGN:
        block_stack.append(2)
      elif block.type == BlockMarkerType.BLOCK_END:
        if len(block_stack) <= 1:
          if len(block_stack) != 0:
            stack_value = block_stack.pop()
            if stack_value == 1:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{block.position + 1}: 'bgn' or '{{' expected")
            elif stack_value == 2:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{len(self._processed_source)}: 'blk' expected")
          else:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{block.position + 1}: unexpected 'end' or '}}'")

        else:
          first_value = block_stack.pop()
          second_value = block_stack.pop()

          if first_value != 2:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{len(self._processed_source)}: 'bgn' or '{{' expected")

          if second_value != 1:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{len(self._processed_source)}: 'blk' expected")

    if len(block_stack) != 0:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{len(self._processed_source)}: 'end' or '}}' expected")

  def _generate_blocks(self) -> List[Block]:
    blocks = []
    blocks_start = []
    block_start = []
    blocks_type = []
    block_end = 0

    for idx, block in enumerate(self._block_list):
      if block.type == BlockMarkerType.BLOCK_DECL:
        blocks_start.append(block.position)
        blocks_type.append(self._block_type_list[idx])
      elif block.type == BlockMarkerType.BLOCK_END:
        block_start = blocks_start.pop()
        block_type = blocks_type.pop()
        block_end = block.position

        new_block = Block(block_start, block_end, block_type, len(blocks))
        blocks.append(new_block)

    for block in blocks:
      if (block.type == BlockType.IF_BLOCK or \
          block.type == BlockType.GENERIC_BLOCK or \
          block.type == BlockType.LP_BLOCK) and \
         (block.start == 0 or \
         Utils.find_parent_block_id(block.start - 1, blocks) == -1):
        block_type = "if" if block.type == BlockType.IF_BLOCK else ("blk" if block.type == BlockType.GENERIC_BLOCK else "lp")
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                           f"{block.start + 1}: unexpected '{block_type}' block found")

    return blocks
