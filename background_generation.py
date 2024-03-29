#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Background Generation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EU0qgtIc2FsVx_iM7jwXWOsnXE0HKslD
"""

from torchvision.utils import save_image
from datetime import datetime
import os

root = "./backgrounds"
folder = "parchment-2"
dest = os.path.join(root, folder)
iters=40

from texturize import api, commands, io

# The input could be any PIL Image in RGB mode.
image = io.load_image_from_file(os.path.join(dest, "input.png"))

# Coarse-to-fine synthesis runs one octave at a time.
for iter_ in range(iters):
  remix = commands.Remix(image)
  for result in api.process_octaves(remix, octaves=5,size=(1080,1080), quality=10):
    pass
  # save_image(result.images, os.path.join(dest, f"out-{datetime.now()}.png"))

  # The output can be saved in any PIL-supported format.
  save_image(result.images, os.path.join(dest, f"out-{datetime.now()}.png"))

