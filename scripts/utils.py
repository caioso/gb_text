import os
import re
import sys

from constants import *
from support.assembler_identifier import AssemblerIdentifier
from support.block import Block
from typing import List

class Utils:
  @staticmethod
  def extract_line_no_comments(line: str) -> str:
    index = line.find(';')
    return line if index == -1 else line[:index]

  @staticmethod
  def extract_code_fragment_no_comment(lines: List[str], start: int, end: int) -> str:
    fragment = ""

    for line in range(start, end):
      fragment += Utils.extract_line_no_comments(lines[line])
    return fragment

  @staticmethod
  def get_flat_text(text: List[str]) -> str:
    flat_text = ""
    for line in text:
      flat_text += line

    return flat_text

  @staticmethod
  def split_tokens(text: str) -> List[str]:
    tokens = re.split('\s+', text)
    tokens = [x for x in tokens if len(x) != 0]
    return tokens

  @staticmethod
  def get_alignment(line: str) -> str:
    alignment = ""
    for char in range(0,len(line) - 1):
      if line[char:char+1].isspace():
        alignment += line[char:char+1]
    return alignment

  @staticmethod
  def load_file_source(file_path: str, include_path: List[str]) -> List[str]:
    contents = []
    os_path = ""
    try:
      os_path = os.path.abspath(file_path)
      with open(os_path) as f:
        contents = f.readlines()
    except:
      raise RuntimeError(f"Unable to open file {os_path}")

    return contents

  @staticmethod
  def locate_file(include_path: str,
                  cmd_include_path: List[str],
                  source: str,
                  line: int) -> str:
    os_path = ""
    for path in cmd_include_path:
      os_path = os.path.join(os.path.abspath(path), include_path)
      if os.path.exists(os_path):
        return os_path

    raise RuntimeError(f"Unable to locate file {os_path} found in '{source}' line {line}")

  @staticmethod
  def is_identifier_unique(identifier_list: List[AssemblerIdentifier],
                           target_identifier: str) -> bool:
    for id in identifier_list:
      if id.identifier_name == target_identifier:
        return False
    return True

  @staticmethod
  def is_assembler_identifier(identifier_list: List[AssemblerIdentifier],
                           target_identifier: str) -> bool:
    for id in identifier_list:
      if id.identifier_name == target_identifier:
        return True
    return False

  @staticmethod
  def is_valid_identifier(identifier: str) -> bool:
    if identifier in KEYWORDS:
      return False
    elif not re.match(IDENTIFIER_NAME_REGEX, identifier):
      return False

    return True

  @staticmethod
  def find_parent_block_id(line_number: int, blocks: List[Block]) -> int:
    min_diff = sys.maxsize
    min_id = -1

    for block in blocks:
      if line_number >= block.start and line_number <= block.end:
        diff = abs(block.start - line_number)
        if min_diff >= diff:
          min_diff = diff
          min_id = block.id

    return min_id