# Split SQL file using sqlparse with delimiter handling.
#
# The SQL string is pre-processed before handing it off to sqlparse.split:
# DELIMITER statements are removed, semicolons within non-standard
# delimiter blocks are replaced by the Unicode Object Replacement
# Character, and custom delimiters replaced with semicolons. After
# processing the string with sqlparse.split, the Object Replacement Characters
# are replaced with semicolons again.

import re
from typing import List

import sqlparse


_SQL_DELIMITER = ";"
_SQL_DELIMITER_RE = re.compile(r"^\s*delimiter\s*(.+)$", re.IGNORECASE)
_PLACEHOLDER = "\ufffc"


def split_sql(sql: str) -> List[str]:
    escaped = _escape_delimiters(sql)
    stmts = sqlparse.split(escaped)
    return [_unescape_delimiters(s) for s in stmts]


def _escape_delimiters(sql: str) -> str:
    if _PLACEHOLDER in sql:
        raise ValueError("unexpected placeholder character in SQL string")
    new_lines: List[str] = []
    delimiter = ""
    for line in sql.splitlines():
        m = _SQL_DELIMITER_RE.match(line)
        if m:
            if m.group(1) == _SQL_DELIMITER:
                delimiter = ""
            else:
                delimiter = m.group(1)
        else:
            if delimiter:
                line = line.replace(_SQL_DELIMITER, _PLACEHOLDER)
                line = line.replace(delimiter, _SQL_DELIMITER)
            new_lines.append(line)
    return "\n".join(new_lines)


def _unescape_delimiters(stmt: str) -> str:
    return stmt.replace(_PLACEHOLDER, _SQL_DELIMITER)
