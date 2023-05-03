#!/usr/bin/env python

import os
import random
import glob
import sys
import signal
import argparse
import docx

font_sizes = range(17, 30)

def generate(path, iters, bg_path, fonts,
             min_spacing, max_spacing):
  if path.endswith('.txt'):
    docs = [path]
  elif os.path.isdir(path):
    docs = glob.glob(os.path.join(path, '**/*.txt'), recursive=True)
  backgrounds = glob.glob(os.path.join(bg_path, '*'))
  fonts = glob.glob(os.path.join(fonts, '**/*.ttf'), recursive=True)
  
  for iter in range(iters):
    font_size = random.choice(font_sizes)
    spacing = random.uniform(min_spacing, max_spacing) * docx.shared.Pt(font_size).inches
    try:
      doc = random.choice(docs)
    except IndexError as e:
      e.add_note(f'Empty document set from path {path}')
      raise
    try:
      background = random.choice(backgrounds)
    except IndexError as e:
      e.add_note(f'Empty background set from path {bg_path}')
      raise
    try:
      font = random.choice(fonts)
    except IndexError as e:
      e.add_note(f'Empty fonts set from path {fonts}')
      raise
    min_alpha = random.uniform(0.5, 0.8)
    margin = random.uniform(0.6, 0.8)
    
    cmd = f"./main.py \"{doc}\" --font-size {font_size} --background \"{background}\" --font \"{font}\" --spacing {spacing} --min-alpha {min_alpha} --margin {margin}"
    ret = os.system(cmd)
    if ret == signal.SIGINT:
      raise KeyboardInterrupt

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Random generator")
  parser.add_argument('path', type=str, help='Path to docs')
  parser.add_argument('iters', type=int, help='Number of docs to generate')
  parser.add_argument('--bg-path', type=str, help='Path to bg',
                      default='Backgrounds')
  parser.add_argument('--fonts', type=str, help='Path to fonts',
                      default='fonts.d')
  parser.add_argument('--min-spacing', type=int,
                      help='Minimum space', default=0.8)
  parser.add_argument('--max-spacing', type=float,
                      help='Maximum space', default=1.5)
  args = parser.parse_args()
  generate(args.path, args.iters, args.bg_path, args.fonts,
           args.min_spacing, args.max_spacing)
