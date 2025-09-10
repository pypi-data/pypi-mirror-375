import io
import os
import re

from collections import namedtuple
from pathlib import PurePath
from typing import List, Optional

from clipped.utils.lists import to_list
from clipped.utils.paths import unix_style_path

from polyaxon._config.manager import ConfigManager
from polyaxon._utils import cli_constants
from polyaxon.logger import logger


class Pattern(namedtuple("Pattern", "pattern is_exclude re")):
    @staticmethod
    def create(pattern: str) -> "Pattern":
        if pattern[0:1] == "!":
            is_exclude = False
            pattern = pattern[1:]
        else:
            if pattern[0:1] == "\\":
                pattern = pattern[1:]
            is_exclude = True
        return Pattern(
            pattern=pattern,
            is_exclude=is_exclude,
            re=re.compile(translate(pattern), re.IGNORECASE),
        )

    def match(self, path: str) -> bool:
        return bool(self.re.match(path))


def translate(pat: str) -> str:
    def _translate_segment():
        # pylint:disable=undefined-loop-variable
        if segment == "*":
            return "[^/]+"
        res = ""
        i, n = 0, len(segment)
        while i < n:
            c = segment[i : i + 1]
            i = i + 1
            if c == "*":
                res += "[^/]*"
            elif c == "?":
                res += "[^/]"
            elif c == "[":
                j = i
                if j < n and segment[j : j + 1] == "!":
                    j = j + 1
                if j < n and segment[j : j + 1] == "]":
                    j = j + 1
                while j < n and segment[j : j + 1] != "]":
                    j = j + 1
                if j >= n:
                    res += "\\["
                else:
                    stuff = segment[i:j].replace("\\", "\\\\")
                    i = j + 1
                    if stuff.startswith("!"):
                        stuff = "^" + stuff[1:]
                    elif stuff.startswith("^"):
                        stuff = "\\" + stuff
                    res += "[" + stuff + "]"
            else:
                res += re.escape(c)
        return res

    res = "(?ms)"

    if pat.startswith("**/"):
        pat = pat[2:]
        res += "(.*/)?"

    if pat.startswith("/"):
        pat = pat[1:]
    else:
        res += "(.*/)?"

    for i, segment in enumerate(pat.split("/")):
        if segment == "**":
            res += "(/.*)?"
            continue
        else:
            res += (re.escape("/") if i > 0 else "") + _translate_segment()

    if not pat.endswith("/"):
        res += "/?"

    return res + "\\Z"


class IgnoreConfigManager(ConfigManager):
    """Manages .polyaxonignore file in the current directory"""

    VISIBILITY = ConfigManager.Visibility.LOCAL
    CONFIG_FILE_NAME = ".polyaxonignore"

    @staticmethod
    def _is_empty_or_comment(line: str) -> bool:
        return not line or line.startswith("#")

    @staticmethod
    def _remove_trailing_spaces(line: str) -> str:
        """Remove trailing spaces unless they are quoted with a backslash."""
        while line.endswith(" ") and not line.endswith("\\ "):
            line = line[:-1]
        return line.replace("\\ ", " ")

    @classmethod
    def init_config(cls):
        cls.set_config(cli_constants.DEFAULT_IGNORE_LIST, init=True)

    @classmethod
    def find_matching(cls, path: str, patterns: List[Pattern]) -> List[Pattern]:
        """Yield all matching patterns for path."""
        for pattern in patterns:
            if pattern.match(path):
                yield pattern

    @classmethod
    def is_ignored(
        cls, path: str, patterns: List[Pattern], is_dir: bool = False
    ) -> bool:
        """Check whether a path is ignored. For directories, include a trailing slash."""
        status = None
        path = "{}/".format(path.rstrip("/")) if is_dir else path
        for pattern in cls.find_matching(path, patterns):
            status = pattern.is_exclude
        return status

    @classmethod
    def read_file(cls, ignore_file: List[str]) -> List[str]:
        for line in ignore_file:
            line = line.rstrip("\r\n")

            if cls._is_empty_or_comment(line):
                continue

            yield cls._remove_trailing_spaces(line)

    @classmethod
    def get_patterns(cls, ignore_file: List[str]) -> List[Pattern]:
        return [Pattern.create(line) for line in cls.read_file(ignore_file)]

    @staticmethod
    def get_push_patterns() -> List[Pattern]:
        return [
            Pattern.create("*.plx.json"),
            Pattern.create("*.plx.index"),
            Pattern.create("./.polyaxon"),
        ]

    @classmethod
    def get_config(cls) -> List[Pattern]:
        config_filepath = cls.get_config_filepath()

        if not os.path.isfile(config_filepath):
            # Return default patterns
            return cls.get_patterns(io.StringIO(cli_constants.DEFAULT_IGNORE_LIST))

        with open(config_filepath) as ignore_file:
            return cls.get_patterns(ignore_file)

    @classmethod
    def get_unignored_filepaths(
        cls,
        path: Optional[str] = None,
        addtional_patterns: Optional[List[Pattern]] = None,
    ) -> List[str]:
        config = to_list(cls.get_config(), check_none=True)
        config += to_list(addtional_patterns, check_none=True)
        unignored_files = []
        path = path or "."

        for root, dirs, files in os.walk(path):
            logger.debug("Root:%s, Dirs:%s", root, dirs)

            if cls.is_ignored(unix_style_path(root), config, is_dir=True):
                dirs[:] = []
                logger.debug("Ignoring directory : %s", root)
                continue

            for file_name in files:
                filepath = unix_style_path(os.path.join(root, file_name))
                if cls.is_ignored(filepath, config):
                    logger.debug("Ignoring file : %s", file_name)
                    continue

                unignored_files.append(os.path.join(root, file_name))

        return unignored_files

    @staticmethod
    def _matches_patterns(path: str, patterns: List[str]) -> bool:
        """Given a list of patterns, returns a if a path matches any pattern."""
        for glob in patterns:
            try:
                if PurePath(path).match(glob):
                    return True
            except TypeError:
                pass
        return False

    @classmethod
    def _ignore_path(
        cls,
        path: str,
        ignore_list: Optional[List[str]] = None,
        allowed_list: Optional[List[str]] = None,
    ) -> bool:
        """Returns a whether a path should be ignored or not."""
        ignore_list = ignore_list or []
        allowed_list = allowed_list or []
        return cls._matches_patterns(path, ignore_list) and not cls._matches_patterns(
            path, allowed_list
        )

    @classmethod
    def get_value(cls, key: str):
        pass
