#!/usr/bin/env python

# use this to clean up data that was generated but wasn't supposed to
# i.e. the image likely contains blank characters

import os
import json
import glob

from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode

# https://stackoverflow.com/a/53829424
def has_glyph(font, glyph):
  for table in font['cmap'].tables:
    if ord(glyph) in table.cmap.keys():
      return True
  return False

class ConfigNotFoundException(Exception):
    "Raised when a config file cannot be found for a specific dataset"
    pass

class FontNotFoundException(Exception):
    "Raised when a config file cannot be found for a specific dataset"
    pass

def check_font_on_text(font_path, source_text_path):
  missing_chars = []
  font = TTFont(font_path)
  source_alphabet = set(open(source_text_path, encoding='utf-8').read())
  for char in source_alphabet:
    if has_glyph(font, char) or char == '\n':
      continue
    else:
      missing_chars.append(char)
  return missing_chars

def check_dir(dir_path):
  try:
    config_path = os.path.join(dir_path, 'config.json')
    config = json.load(open(config_path, 'r'))
  except FileNotFoundError:
    raise ConfigNotFoundException

  resave = False
  
  try:
    source_alphabet = set(open(config['path'], encoding='utf-8').read())
  except FileNotFoundError:
    config['path'] = os.path.join('sources', config['path'])
    source_alphabet = set(open(config['path'], encoding='utf-8').read())
    resave = True
  try:
    font_path = config['font']
  except KeyError:
    font_path = config['default_font']
  
  if not os.path.exists(font_path):
    if 'NotoNaskh' in font_path:
      font_path = 'fonts.d/Noto_Naskh_Arabic/NotoNaskhArabic-VariableFont_wght.ttf'
      config['font'] = font_path
      resave = True
    elif 'MarkaziText' in font_path:
      font_path = 'fonts.d/Markazi_Text/MarkaziText-VariableFont_wght.ttf'
      config['font'] = font_path
      resave = True
    else:
      raise FontNotFoundException
      
  if resave:
    with open(config_path, 'w') as f:
      json.dump(config, f)

  return (check_font_on_text(font_path, config['path']),
          config['font'], config['path'])

if __name__ == '__main__':
  outputs = glob.glob('outputs/*')
  
  report = {'incompatible': [], 'marked': []}
  
  for dir_ in outputs:
    try:
      missing_chars, font, source_path = check_dir(dir_)
      if len(missing_chars) > 0:
        report['marked'].append(dir_)
        report['incompatible'].append({
          'font': font,
          'text': source_path,
          'missing': list(missing_chars)
        })
    except ConfigNotFoundException:
      report['marked'].append(dir_)
    except FontNotFoundException:
      report['marked'].append(dir_)
    print(f'Done with "{dir_}"')
    
  with open('data-report.json', 'w') as f:
    json.dump(report, f)
