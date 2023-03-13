#!/usr/bin/env python

import uno
import os
import argparse

os.environ['UNO_PATH'] = '/usr/bin/libreoffice/program'
os.environ['URE_BOOTSTRAP'] = '/usr/bin/libreoffice/program/fundamentalrc'

def main(args):
    # Start the LibreOffice API
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", localContext)
    ctx = resolver.resolve(
        "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    smgr = ctx.ServiceManager

    # Open the document
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.loadComponentFromURL(
        f"file://{os.path.abspath(args.path)}", "_blank", 0, ())

    # Get the bounding boxes of each paragraph
    cursor = doc.Text.createTextCursor()
    paragraphs = doc.Text.createEnumeration()
    for i, paragraph in enumerate(paragraphs):
        # Move the cursor to the start of the paragraph
        cursor.gotoRange(paragraph.getStart(), False)
        
        # Get the bounding box of the paragraph
        frame = cursor.TextFrame
        if frame is not None:
            x, y, width, height = frame.Anchor.getPositionAndSize()
            print(f"Paragraph {i+1}: ({x}, {y}, {x+width}, {y+height})")
        else:
            print(f"Paragraph {i+1}: no bounding box")

    # Close the document
    doc.dispose()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthesizer for OCR data")
    parser.add_argument("path", type=str, help="Path to pdf file")
    parser.add_argument("--start-page", type=int, help="Starter page to parse", default=0)
    parser.add_argument("--end-page", type=int, help="Starter page to parse", default=-1) 
    
    main(parser.parse_args())
