import os
import re
from typing import List, Tuple

from constants import *
from enums import IdentifierType
from support.assembler_identifier import AssemblerIdentifier
from utils import Utils

class FindIncludesPass:
  def __init__(self, input_file: str, source: List[str], include_path: List[str]):
    self._input_file = input_file
    self._raw_source = source
    self._cmd_include_path = include_path
    self._identifier_list = []

  def process(self) -> Tuple[List[str], List[AssemblerIdentifier]]:
    top_level_source = Utils.locate_file(self._input_file,
                                         self._cmd_include_path,
                                         self._input_file,
                                         1)
    print(f"Top level include {top_level_source}")
    self._include_list = [top_level_source]

    self._extract_includes(self._raw_source)
    self._extract_memory_aliasses()
    self._extract_macros()
    self._extract_labels()

    return [self._include_list, self._identifier_list]

  def _extract_memory_aliasses(self) -> None:
    for file in self._include_list:
      source = Utils.load_file_source(file, self._cmd_include_path)
      for idx, line in enumerate(source):
        clear_line = Utils.extract_line_no_comments(line)

        if re.match(MEMORY_ALIAS_REGEX, clear_line):
          tokens = Utils.split_tokens(line)

          if tokens[0].upper() == KEYWORD_DEF:
            self._identifier_list.append(AssemblerIdentifier(tokens[1],
                                                        file,
                                                        idx,
                                                        IdentifierType.NAMED_CONSTANT))
          else:
            self._identifier_list.append(AssemblerIdentifier(tokens[0],
                                                        file,
                                                        idx,
                                                        IdentifierType.NAMED_CONSTANT))

  def _extract_macros(self) -> None:
    for file in self._include_list:
      source = Utils.load_file_source(file, self._cmd_include_path)
      for idx, line in enumerate(source):
        clear_line = Utils.extract_line_no_comments(line)

        if re.match(MACRO_REGEX, clear_line):
          tokens = Utils.split_tokens(line)

          if ':' in tokens[0]:
            id = tokens[0].split(':')[0]
            self._identifier_list.append(AssemblerIdentifier(id,
                                                            file,
                                                            idx,
                                                            IdentifierType.MACRO))
          else:
            self._identifier_list.append(AssemblerIdentifier(tokens[0],
                                                            file,
                                                          idx,
                                                          IdentifierType.MACRO))

  def _extract_labels(self) -> None:
    for file in self._include_list:
      source = Utils.load_file_source(file, self._cmd_include_path)
      for idx, line in enumerate(source):
        clear_line = Utils.extract_line_no_comments(line)

        if re.match(LABEL_REGEX, clear_line):
          tokens = Utils.split_tokens(line)

          id = tokens[0]
          if ':' in id:
            id = id.split(':')[0]
          if '.' in id:
            id = id.split('.')[1]

          self._identifier_list.append(AssemblerIdentifier(id,
                                                           file,
                                                           idx,
                                                           IdentifierType.LABEL))

  def _extract_includes(self, source : List[str]) -> None:
    local_includes = []
    for idx, line in enumerate(source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(INCLUDE_REGEX, clear_line):
        include_path = self._extract_included_path(clear_line)
        os_included_path = Utils.locate_file(include_path,
                                             self._cmd_include_path,
                                             self._input_file,
                                             idx)

        if not self._path_already_exist(os_included_path):
          self._include_list.append(os_included_path)
          local_includes.append(os_included_path)

    self._extract_sub_includes(local_includes)

  def _extract_sub_includes(self, input_local_includes: List[str]) -> None:
    if len(input_local_includes) != 0:
      local_includes = []
      for include in input_local_includes:
        source = Utils.load_file_source(include, self._cmd_include_path)

        for idx, line in enumerate(source):
          clear_line = Utils.extract_line_no_comments(line)

          if re.match(INCLUDE_REGEX, clear_line):
            include_path = self._extract_included_path(clear_line)
            os_included_path = Utils.locate_file(include_path,
                                                  self._cmd_include_path,
                                                  self._input_file,
                                                  idx)

            if not self._path_already_exist(os_included_path):
              self._include_list.append(os_included_path)
              local_includes.append(os_included_path)

      self._extract_sub_includes(local_includes)

  def _path_already_exist(self, path: str) -> bool:
    for include_path in self._include_list:
      if (os.path.samefile(path, include_path)):
        return True

    return False

  def _extract_included_path(self, clear_line: str) -> str:
    include_path = ""
    path_started = False
    for char in clear_line:
      if path_started == False and char == '\"':
        path_started = True
        continue
      elif path_started == True and char == '\"':
        break

      if path_started == True:
        include_path += char

    return include_path
