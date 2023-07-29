#!/usr/bin/env python
import random
import numpy as np
import os
from tqdm import trange
from generators import NumberGenerator, PegonJawaGenerator
import datetime

filedir = '../sources/synthesized/'
os.makedirs(filedir, exist_ok=True)

# generator = PegonJawaGenerator()
# file_title = 'pegon-jawa'
generator = NumberGenerator()
file_title = 'numbers'
iterations = 20

for it in trange(iterations, leave=False):
  generations = random.randint(1000, 5000)
  filepath = os.path.join(filedir, f'{file_title}-{datetime.datetime.now().timestamp()}.txt')
  text = ''
  for i in trange(generations, leave=False):
    text += generator.postprocess_word(generator.generate())
  text = generator.postprocess_text(text)
  with open(filepath, 'w') as file:
    file.write(text)
