#!/usr/bin/env python

import uno
import os
import argparse

from com.sun.star.beans import PropertyValue
from com.sun.star.awt import Rectangle


def get_bounding_boxes_and_text(path):
    # create the uno component context
    local_context = uno.getComponentContext()

    # create the uno service manager from the context
    resolver = local_context.ServiceManager

    # create a new instance of the desktop
    desktop = resolver.createInstanceWithContext("com.sun.star.frame.Desktop", local_context)

    # create the URL to the document
    url = uno.systemPathToFileUrl(path)

    # load the document
    document = desktop.loadComponentFromURL(url, "_blank", 0, ())

    # get the text document
    text_document = document.getText()

    # get the paragraphs
    paragraphs = text_document.createEnumeration()

    # create an empty list to store the bounding boxes and text
    bounding_boxes_and_text = []

    # loop through the paragraphs
    while paragraphs.hasMoreElements():
        # get the paragraph
        paragraph = paragraphs.nextElement()

        # get the text of the paragraph
        text = paragraph.getString()

        # get the text range of the paragraph
        text_range = paragraph.getEnd()

        # get the cursor for the text range
        cursor = text_document.createTextCursorByRange(text_range)

        # get the frame for the cursor
        frame = cursor.Frame

        # get the anchor for the frame
        anchor = frame.Anchor

        # get the position and size of the anchor
        position = anchor.getPosition()
        size = anchor.getSize()

        # create a rectangle object from the position and size
        rectangle = Rectangle(position.X, position.Y, size.Width, size.Height)

        # add the bounding box and text to the list
        bounding_boxes_and_text.append((rectangle, text))

    # close the document
    document.close(True)

    return bounding_boxes_and_text

def main(args):
    for i, (box, text) in enumerate(
            get_bounding_boxes_and_text(args.path)):
        print(f"Paragraph {i+1} text: {text}")
        print(f"Bounding box: x={box.X}, y={box.Y}, width={box.Width}, height={box.Height}")
if __name__ == "__main__":
    os.environ['UNO_PATH'] = '/usr/bin/libreoffice/program'
    os.environ['URE_BOOTSTRAP'] = '/usr/bin/libreoffice/program/fundamentalrc'
    parser = argparse.ArgumentParser(description="Synthesizer for OCR data")
    parser.add_argument("path", type=str, help="Path to pdf file")
    parser.add_argument("--start-page", type=int, help="Starter page to parse", default=0)
    parser.add_argument("--end-page", type=int, help="Starter page to parse", default=-1) 
    
    main(parser.parse_args())
