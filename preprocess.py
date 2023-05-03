#!/usr/bin/env python
import re
import glob
import os

replacements = [
  (r"[^\u0600-\u06ff\u0750-\u077f\uFE70-\uFEFF\uFB50-\uFDFF\u0870-\u089F\W\n]+\b", ''),
  
  (r'\,', '،'),
  (r'\.', '۔\n'),
  
  (r'\t+', ' '),
  
  (r'\(', '﴾'),
  (r'\)', '﴿'),
  
  (r'\[', '﴾'),
  (r'\]', '﴿'),
  
  (r'"(\w+?)"', r'«\1»'),
  (r'\'(\w+?)\'', r'«\1»'),
  (r'“(\w+?)”', r'«\1»'),
  (r'‘(\w+?)’', r'«\1»'),
  (r'["\'“”‘’;]', ''),

  (r'[\-—=:\u00A0⇒]', ' '),
  
  # corrective assumption
  (r"(^|\n)[\u064e\u064f\u0650\u064b\u064c\u064d\u0674]", ''),
  (r"\b[\u0621\u0674]\b", ''),
  # (r"\W{4,}", ''),
  (r'(?<![«»\n])\W{4,}(?![«»\n])', ''),
  (r'\n+', '\n'),
  (r' +', ' '),

  # delete long strings of punctuation
  (r'\n[،۔«»﴾﴿ ]+\n', ''),
]

def preprocess_text(text):
  lines = []
  for line in text.split('\n'):
    line_count = len(line)
    # latin_count = len(re.sub(r'[^a-zA-z]', '', line))
    arab_count = len(re.sub(r'[^\u0600-\u06ff\u0750-\u077f\uFE70-\uFEFF\uFB50-\uFDFF\u0870-\u089F]', '', line))
    if line_count > 0 and (arab_count / line_count) > 0.9:
      continue
    else:
      lines.append(line)
  text = '\n'.join(lines)
  for pattern, rep in replacements:
    text = re.sub(pattern, rep, text)
  return text

if __name__ == '__main__':
  for d in glob.glob('sources/scraped/**/*.txt', recursive=True):
    d_new = d.replace('scraped', 'scraped-preprocessed')
    os.makedirs(os.path.dirname(d_new), exist_ok=True)
    with open(d_new, 'w') as f:
      f.write(preprocess_text(open(d).read()))
    with open(d_new.replace('.txt', '.metadata.json'), 'w') as f:
      f.write(open(d.replace('.txt', '.metadata.json')).read())
