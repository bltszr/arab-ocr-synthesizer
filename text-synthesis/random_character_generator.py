#!/usr/bin/env python
import random
import numpy as np
import os
from tqdm import trange
from generators import NumberGenerator, PegonJawaGenerator
import datetime

filedir = '../sources/synthesized/'
# file_title = 'numbers'
file_title = 'pegon-jawa'
os.makedirs(filedir, exist_ok=True)

generator = PegonJawaGenerator()


generations = 10_000
iterations = 100
for it in trange(iterations, leave=False):
  filepath = os.path.join(filedir, f'{file_title}-{datetime.datetime.now().timestamp()}.txt')
  text = ''
  for i in trange(generations, leave=False):
    text += generator.generate()
    if text != generator.par_delimiter:
      text += ' '
  text = text.replace(' ' + generator.comma, generator.comma).replace(' ' + generator.full_stop, generator.full_stop)
  with open(filepath, 'w') as file:
    file.write(text)
