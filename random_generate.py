#!/usr/bin/env python

import os
import random
import glob
import sys
import signal
import argparse
import docx
from tqdm import trange
from multiprocessing import Pool, cpu_count
import subprocess

font_sizes = range(17, 30)

def generate_command(path, output_dir, bg_path, fonts,
                     min_spacing, max_spacing, min_dpi, max_dpi,
                     warn, verbose):
  
  if path.endswith('.txt') or path.endswith('.chars'):
    docs = [path]
  elif os.path.isdir(path):
    docs = glob.glob(os.path.join(path, '**/*.txt'), recursive=True)
  backgrounds = glob.glob(os.path.join(bg_path, '*'))
  fonts = glob.glob(os.path.join(fonts, '**/*.ttf'), recursive=True)
  
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
  dpi = random.randint(min_dpi, max_dpi)
  scriptio_continuo = random.random() > 0.7
  cmd = f"./main.py \"{doc}\" --font-size {font_size} --background \"{background}\" --font \"{font}\" --spacing {spacing} --min-alpha {min_alpha} --margin {margin} --output-dir \"{output_dir}\" {'--warn' if warn else ''} {'--verbose' if verbose else ''} --dpi {dpi} {'-sc' if scriptio_continuo else ''}"
  return cmd

def run_command(command):
  try:
    subprocess.run(command, shell=True, check=True)
  except subprocess.CalledProcessError as e:
    if e.returncode == signal.SIGINT:
      print("Received KeyboardInterrupt. Stopping the program.")
      os.kill(os.getpid(), signal.SIGINT)  # Stop the program entirely

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
  
  parser.add_argument("--output-dir", "-o", type=str, help="Path to output directory", default='outputs')

  parser.add_argument("--warn", action="store_true", help="Emit warnings")
  parser.add_argument("--verbose", action="store_true", help="Set warnings and info to true")

  parser.add_argument('--min-dpi', type=int, default=72)
  parser.add_argument('--max-dpi', type=int, default=250)

  parser.add_argument('--batch-size', '-b', type=int, default=1)
  
  args = parser.parse_args()
  for it in trange(0, args.iters, args.batch_size, leave=False):
    commands = [generate_command(args.path, args.output_dir, args.bg_path, args.fonts,
                                 args.min_spacing, args.max_spacing, args.min_dpi, args.max_dpi,
                                 args.warn, args.verbose) for com in range(args.batch_size)]
    with Pool(processes=min(args.batch_size, cpu_count())) as pool:
      pool.map(run_command, commands)

