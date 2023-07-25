import unicodedata
import demoji
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display
import re

reshaper = ArabicReshaper(configuration = {
    'delete_harakat': False,
    'support_ligatures': True,
    'RIAL SIGN': True,  # Replace ر ي ا ل with ﷼
  })

def remove_character_blocks(s, blocks=['C', 'S']):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] not in blocks)


def real_preprocess(line):
  line = remove_character_blocks(line)
  line = line.replace('﴾', '(').replace('﴿', ')')
  line = demoji.replace(line, '')
  line = re.sub(r"[^\u0600-\u06ff\u0750-\u077f\uFE70-\uFEFF\uFB50-\uFDFF\u0870-\u089F\W\n]+\b", '' , line)
  line = re.sub(r"^[\u064e\u064f\u0650\u064b\u064c\u064d\u0674]", '', line)
  line = re.sub(r"\b[\u0621\u0674]\b", '', line)
  return line

def render_preprocess(line):
  return u'\u200f' + line
