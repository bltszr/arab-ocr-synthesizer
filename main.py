#!/usr/bin/env python

from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display

from PIL import Image, ImageDraw, ImageFont

import docx
from docx.shared import Length, Inches, Pt, Mm, Emu

import math

# from pdfminer.high_level import extract_pages
# from pdfminer.layout import LTTextContainer, LTChar, LTTextLine 

import argparse
import os
import json
import random
import glob

import time
from datetime import datetime

DPI = 200

to_px = lambda length, dpi=DPI : int((length.inches * dpi))
from_px = lambda pxs, dpi=DPI : Inches(pxs / dpi)

line_spacing_rules = {
  docx.enum.text.WD_LINE_SPACING.ONE_POINT_FIVE: 1.5,
  docx.enum.text.WD_LINE_SPACING.SINGLE: 1,
  docx.enum.text.WD_LINE_SPACING.AT_LEAST: 1,
  docx.enum.text.WD_LINE_SPACING.DOUBLE: 2,
}

DEFAULT = {
  "spacing": Inches(0.5),
  "spacing rule": 1,
  "font": "Calibri",
  "font size": Pt(12),
  "page height": Mm(297),
  "page width": Mm(210),
  "left margin": Inches(1),
  "right margin": Inches(1),
  "top margin": Inches(1),
  "bottom margin": Inches(1),
}

to_project_dir = lambda path : os.path.join('outputs', f"{os.path.basename(path)}.{int(time.mktime(datetime.now().timetuple()))}.d")

def save(img, bboxes, dest_folder, page_number):
  img_filename = os.path.join(dest_folder,  f'{page_number}.png')
  json_filename = os.path.join(dest_folder,  f'{page_number}.json')
  img.save(img_filename)
  with open(json_filename, 'w') as f:
    json.dump(bboxes, f)
  print(f'Saved \'{img_filename}\'')

def create_page(page_width, page_height, bg=None):
  if bg != None:
    img = Image.open(random.choice(glob.glob(os.path.join(bg, '*'))))\
               .resize((page_width, page_height))\
               .convert("RGBA")
  else:
    img = Image.new("RGBA",
                    tuple(map(int,
                              (page_width,
                               page_height))),
                    color="white")
  draw = ImageDraw.Draw(img)
  return img, draw, []

# from https://stackoverflow.com/a/67203353
def get_wrapped_text(text: str,
                     font: ImageFont.ImageFont,
                     line_length: int):
  lines = ['']
  for word in text.split():
    # print(lines)
    line = f'{lines[-1]} {word}'.strip()
    if font.getlength(line, direction="rtl") <= line_length:
      lines[-1] = line
    else:
      lines.append(word)
  return lines


def get_font_size(style):
    if style.font.size == None:
        if style.base_style != None:
            return get_font_size(style.base_style)
        else:
            return None
    else:
        return style.font.size

def get_font_name(style):
  if style.font.name == None:
    if style.base_style != None:
      return get_font_size(style.base_style)
    else:
      return None
  else:
    return style.font.name
      
def get_font(run, font_dict):
  # Get the font size of the run
  try:
    run_font_size = get_font_size(run.style)
  except (TypeError, AttributeError):
    run_font_size = DEFAULT["font size"]

  try:
    run_font_name = get_font_name(to_px(run.style))
  except (TypeError, AttributeError):
    run_font_name = DEFAULT["font"]
    
  return ImageFont.truetype(font_dict[run_font_name],
                            to_px(run_font_size))

def get_spacing(paragraph):
  try:
    if type(paragraph.paragraph_format.line_spacing) == float:
      try:
        spacing = from_px(get_font_size(paragraph.style) * paragraph.paragraph_format.line_spacing)
      except (TypeError, AttributeError, IndexError) as e:
        spacing = Emu(DEFAULT["spacing"] * DEFAULT["spacing rule"])
    else:
      spacing = paragraph.paragraph_format.line_spacing * line_spacing_rules[
        paragraph.paragraph_format.line_spacing_rules
      ]
  except (TypeError, AttributeError) as e:
    spacing = Emu(DEFAULT["spacing"] * DEFAULT["spacing rule"])
  return spacing

def get_indents(paragraph):
  right_indent = paragraph.paragraph_format.right_indent
  left_indent = paragraph.paragraph_format.left_indent
  if left_indent == None:
    left_indent = Inches(0)
  if right_indent == None:
    right_indent = Inches(0)
  return right_indent, left_indent


def process_txt(args, font):
  dest_folder = to_project_dir(args.path)
  os.makedirs(dest_folder, exist_ok=True)
  
  page_width, page_height,\
    left_margin, right_margin,\
    top_margin, bottom_margin = map(to_px,
                                    (DEFAULT['page width'],
                                     DEFAULT['page height'],
                                     DEFAULT['left margin'],
                                     DEFAULT['right margin'],
                                     DEFAULT['top margin'],
                                     DEFAULT['bottom margin']))
  
  page_number = 1
  # print((page_width, page_height))
  # Iterate over each paragraph in the document
  img, draw, bboxes = create_page(page_width, page_height, args.background)
  cum_spacing = top_margin
  # Extract the text and style of the paragraph
  
  # print(paragraph.paragraph_format.line_spacing)
  # print(paragraph.paragraph_format.line_spacing_rule)
  par_spacing = to_px(Emu(DEFAULT['spacing'] * DEFAULT['spacing rule']))
  right_indent = 0
  left_indent = 0
  for j, run in enumerate(open(args.path, 'r')):
    if page_number > args.end_page:
      break
    text = get_wrapped_text(run,
                            font,
                            page_width \
                            - right_margin \
                            - left_margin \
                            - right_indent \
                            - left_indent)
    for k, line in enumerate(text):
      # middle part = page_width - right_indent - left_indent - right_margin - left_margin
      # x = left_margin + left_indent + (middle part - length of line)
      # x = page_width - right_indent - right_margin - length of line
      x = page_width \
        - right_margin - right_indent \
        - font.getlength(line)
      if cum_spacing + font.size > page_height - bottom_margin:
        save(img, bboxes, dest_folder, page_number)
        img, draw, bboxes = create_page(page_width, page_height, args.background)
        cum_spacing = top_margin
        page_number += 1
      if page_number > args.end_page:
        break
      y = cum_spacing
      if args.warn and y > page_height:
        print(f"[WARN] Ran off page at line {line}\n")
      alpha = int(random.uniform(args.min_alpha, args.max_alpha) * 255)
      txt_im = Image.new('RGBA', img.size,
                         (255,255,255,0))
      txt_d = ImageDraw.Draw(txt_im)
      txt_d.text((x, y), line,
                 font=font,
                 fill=(0, 0, 0, alpha),
                 direction="rtl")
      bbox = draw.textbbox((x, y), line,
                           font=font,
                           direction="rtl")
      img = Image.alpha_composite(img, txt_im)
      bboxes.append({"text": line,
                     "bbox": bbox})
      cum_spacing += par_spacing
  save(img, bboxes, dest_folder, page_number)
  with open(os.path.join(dest_folder, 'config.json'), 'w') as f:
    json.dump(vars(args), f)

def process_doc(args, font_dict):
  dest_folder = to_project_dir(args.path)
  doc = docx.Document(doc_path)
  os.makedirs(dest_folder, exist_ok=True)

  section = doc.sections[0]
  page_width, page_height,\
    left_margin, right_margin,\
    top_margin, bottom_margin = map(to_px,
                                    (section.page_width,
                                     section.page_height,
                                     section.left_margin,
                                     section.right_margin,
                                     section.top_margin,
                                     section.bottom_margin))
  
  page_number = 1
  text_page_height = page_height - top_margin - bottom_margin
  # print((page_width, page_height))
  # Iterate over each paragraph in the document
  img, draw, bboxes = create_page(page_width, page_height, bg)
  cum_spacing = top_margin
  for i, paragraph in enumerate(doc.paragraphs):
    if page_number > args.end_page:
      break 
    # Extract the text and style of the paragraph
    right_indent, left_indent = get_indents(paragraph)
    style = paragraph.style.name
    
    # print(paragraph.paragraph_format.line_spacing)
    # print(paragraph.paragraph_format.line_spacing_rule)
    par_spacing = to_px(get_spacing(paragraph))
    for j, run in enumerate(paragraph.runs):
      if run._element.xpath('w:lastRenderedPageBreak'):
        save(img, bboxes, dest_folder, page_number)
        img, draw, bboxes = create_page(page_width, page_height)
        # draw.rectangle([0, 0, 500, 500], outline="Red")
        cum_spacing = top_margin
        page_number += 1
      if page_number > args.end_page:
        break
      # print(page_number)
      # print(run.text)
      font = get_font(run, font_dict)
      text = get_wrapped_text(run.text,
                              font,
                              page_width \
                              - right_margin \
                              - left_margin \
                              - right_indent \
                              - left_indent)
      for k, line in enumerate(text):
        # middle part = page_width - right_indent - left_indent - right_margin - left_margin
        # x = left_margin + left_indent + (middle part - length of line)
        # x = page_width - right_indent - right_margin - length of line
        x = page_width \
          - right_margin - right_indent \
          - font.getlength(line)
        if cum_spacing + font.size > text_page_height:
          save(img, bboxes, dest_folder, page_number)
          img, draw, bboxes = create_page(page_width, page_height)
          cum_spacing = top_margin
          page_number += 1
        if page_number > args.end_page:
          break
        y = cum_spacing
        if args.warn and y > page_height:
          print(f"[WARN] Ran off page at line {line}\n")
        # line = get_display(reshaper.reshape(line))
        draw.text((x, y), line,
                  font=font,
                  fill=(0, 0, 0),
                  direction="rtl")
        bbox = draw.textbbox((x, y), line,
                             font=font,
                             direction="rtl")
        bboxes.append({"text": line,
                       "bbox": bbox})
        cum_spacing += par_spacing

def main(args):
  DEFAULT.update({"font": args.default_font,
                  "font size": Pt(args.default_font_size),
                  "spacing": Inches(args.default_spacing)})
  if args.alpha:
    args.min_alpha = args.alpha
    args.max_alpha = args.alpha
  configuration = {
    'delete_harakat': False,
    'support_ligatures': True,
    'RIAL SIGN': True,  # Replace ر ي ا ل with ﷼
  }
  with open('fonts') as fp:
    font_dict = json.load(fp)
  WARN = args.warn
  reshaper = ArabicReshaper(configuration=configuration)
  if args.path.endswith(".docx"):
    process_doc(args, font_dict)
  elif args.path.endswith(".txt"):
    if os.path.exists(args.default_font):
      fontpath = args.default_font
    else:
      fontpath = font_dict[args.default_font]
    process_txt(args, ImageFont.truetype(fontpath,
                                         size=to_px(DEFAULT['font size'])))
          
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Synthesizer for OCR data")
  parser.add_argument("path", type=str,
                      help="Path to pdf or txt file")
  parser.add_argument("--start-page", type=int,
                      help="Starter page to parse",
                      default=0)
  parser.add_argument("--end-page", type=int,
                      help="Starter page to parse, will be ignored if file is txt",
                      default=math.inf)
  parser.add_argument("--default-font", type=str,
                      help="Override default font",
                      default=DEFAULT['font'])
  parser.add_argument("--default-font-size", type=int,
                      help="Override default font size in pt",
                      default=DEFAULT['font size'].pt)
  parser.add_argument("--default-spacing", type=float,
                      help="Override default spacing rules",
                      default=DEFAULT['spacing'].inches)
  parser.add_argument("--min-alpha", type=float, default=0.85,
                      help="Minimum alpha to choose for text")
  parser.add_argument("--max-alpha", type=float, default=1.0,
                      help="Maximum alpha to choose for text")
  parser.add_argument("--alpha", type=float, default=None,
                      help="Single alpha value for all text. Overrides min-alpha and max-alpha")
  parser.add_argument("--warn", action="store_true", help="Emit warnings")
  parser.add_argument("--background", type=str, help="Path to folder of backgrounds")
  
  main(parser.parse_args())
