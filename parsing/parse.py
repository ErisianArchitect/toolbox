"""
Pronounced fmeat, not f-meat, not f-me-at, fmeat, rhymes with meat and feet.

This module is used for processing text into HTML.
It is a markup format that has similarities to markdown.
"""
from typing import *
from typing_extensions import *
from functools import partial, wraps
import re
import sys

from itertools import groupby

class regex:
    line = re.compile(r'(?m)(?:\A|(?<=\r\n)|(?<=\r)|(?<=\n)).*?(?=\Z|\r\n|\r|\n)')
    non_empty_lines = re.compile(r'(?m)(?:^|(?<=\r\n)|(?<=\r)|(?<=\n)).+?(?=$|\r\n|\r|\n)')
    line_split = re.compile(r'\r\n|\r|\n')
    block_split = re.compile(r'\r\n\r\n|\r\r|\n\n')
    line_break = re.compile(r'\r?\n|  \r?\n')
    testre = re.compile(r'(?m)(?:(\:!).*|(\:\?).*)')
    comma = re.compile(r',')
    dot = re.compile(r'.')
    indent = re.compile(r'^[\t ]*')
    indent_parts = re.compile(r'(^[\t ]*)(.*)')

def splitpositions(
        text: str,
        split: str | re.Pattern = ',',
        start: int = 0,
        end: int = sys.maxsize
    ):
    """A generator that splits a string by the given split expression and yields
    the spans of the splits.
    
    :split: Either a string or a regex expression pattern.
    :text:  The text you would like to split.
    :start: The index to start the search at.
    :end:   The index to end the search at.
    
    Example:
    ```py
    for part in splitpositions('this.is.a.test', '.'):
        print(repr(part))
    ```
    """
    if isinstance(split, str):
        split = re.compile(re.escape(split))
    while (m := split.search(text, start, end)):
        yield (start, m.start())
        start = m.end()
    yield (start, len(text))

def split(text: str, split: str | re.Pattern = regex.comma, start: int = 0, end: int = sys.maxsize):
    yield from (text[start:end] for start, end in splitpositions(text, split, start, end))

def splitlines(text: str, start: int = 0, end: int = sys.maxsize):
    yield from split(text, regex.line_split, start, end)

def splitblocks(text: str, start: int = 0, end: int = sys.maxsize):
    yield from split(text, regex.block_split, start, end)

def indent_parts(s: str)->Tuple[int, Tuple[int, int]]:
    """Returns the length of the indent as well as the span of rest of the text after the indent."""
    if s and (indent := regex.indent_parts.match(s)):
        _, end = indent.span(1)
        return (end, indent.span(2))
    return (0, (0, 0))

def after_indent(s: str)->str:
    if (indent := regex.indent_parts.match(s)):
        indent.group(2)
    return ''

def text_indent(s: str)->str:
    if not s or s[0] not in '\t ':
        return s[0:0]
    count = 1
    while count < len(s) and s[count] == s[0]:
        count += 1
    return s[:count]

def group_indentations(text: str):
    lines = splitlines(text)

content = """This is a line.
This is another line.

This is another "paragraph".  
This is another line in the third paragraph."""

"""
This is the first line of the first paragraph.
This is the second line.

This is the second paragraph.
This is the second line of the second paragraph.

This is the third paragraph.
This is the second line of the third paragraph.
"""