#!/usr/bin/env python

import os
import random
import glob
import sys
import signal

hadiths = glob.glob("sources/sunnah_per_ch_preprocessed/sunnah*.txt")
font_sizes = range(17, 30)
backgrounds = glob.glob("Backgrounds/*")
fonts = glob.glob('fonts.d/**/*.ttf', recursive=True)
def generate(iters):
  for iter in range(iters):
    ret = os.system(f"./main.py {random.choice(hadiths)} --font-size {random.choice(font_sizes)} --background {random.choice(backgrounds)} --font \"{random.choice(fonts)}\" --spacing {random.uniform(0.3, 0.8)} --min-alpha {random.uniform(0.5, 0.8)} --margin {random.uniform(0.6, 0.8)}")
    if ret == signal.SIGINT:
      raise KeyboardInterrupt

if __name__ == '__main__':
  generate(int(sys.argv[1]))
