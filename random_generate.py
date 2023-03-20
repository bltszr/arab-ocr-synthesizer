#!/usr/bin/env python

import os
import random
import glob
import sys
import signal
import argparse
import docx

font_sizes = range(17, 30)
backgrounds = glob.glob("Backgrounds/*")
fonts = glob.glob('fonts.d/**/*.ttf', recursive=True)

def generate(path, iters):
  if path.endswith('.txt'):
    docs = [path]
  elif os.path.isdir(path):
    docs = glob.glob(os.path.join(path, '**/*.txt'), recursive=True)
  
  for iter in range(iters):
    font_size = random.choice(font_sizes)
    spacing = random.uniform(0.8, 1.5) * docx.shared.Pt(font_size).inches
    cmd = f"./main.py \"{random.choice(docs)}\" --font-size {random.choice(font_sizes)} --background {random.choice(backgrounds)} --font \"{random.choice(fonts)}\" --spacing {spacing} --min-alpha {random.uniform(0.5, 0.8)} --margin {random.uniform(0.6, 0.8)}"
    # print(cmd)
    # print(spacing)
    ret = os.system(cmd)
    if ret == signal.SIGINT:
      raise KeyboardInterrupt

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Random generator")
  parser.add_argument('path', type=str, help='Path to docs')
  parser.add_argument('iters', type=int, help='Number of docs to generate')
  args = parser.parse_args()
  generate(args.path, args.iters)
