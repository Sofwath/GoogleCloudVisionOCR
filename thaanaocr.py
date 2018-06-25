import io
import os

import argparse
from enum import Enum

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

def draw_boxes(image, bounds, color):
  
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], None, color)
    return image

def do_documnet_ocr(image_file, feature):

	client = vision.ImageAnnotatorClient()

	with io.open(image_file, 'rb') as image_file:
	    content = image_file.read()

	image = types.Image(content=content)

	response = client.document_text_detection(image=image)
	document = response.full_text_annotation

	bounds = []
	doctext = []

	for page in response.full_text_annotation.pages:
	        for block in page.blocks:
	            block_words = []
	            for paragraph in block.paragraphs:
	                block_words.extend(paragraph.words)
	                print(u'Paragraph Confidence: {}\n'.format(paragraph.confidence))

	            block_text = ''
	            block_symbols = []
	            for word in block_words:
	                block_symbols.extend(word.symbols)
	                word_text = ''
	                for symbol in word.symbols:
	                    word_text = word_text + symbol.text
	                    print(u'\tSymbol text: {} (confidence: {})'.format(symbol.text, symbol.confidence))

	                print(u'Word text: {} (confidence: {})\n'.format(word_text, word.confidence))

	                block_text += ' ' + word_text

	            print(u'Block Content: {}\n'.format(block_text))
	            print(u'Block Confidence:\n {}\n'.format(block.confidence))
	            bounds.append(block.bounding_box)
	            doctext.append(block_text + "\n")


	return (bounds,doctext)

def render_doc_text(filein, fileout, imagefile):
    
    image = Image.open(filein)
  
    bounds,doctext = do_documnet_ocr(filein, FeatureType.WORD)
    draw_boxes(image, bounds, 'green')

    if imagefile is not 0:
        image.save(imagefile)
    else:
        image.show()

    if fileout is not 0:
    	with io.open(fileout, 'w', encoding="utf-8") as f:
    		outdoctext = ''.join(doctext)
    		f.write(outdoctext)

    print (u'Document Content: {}\n'.format(doctext))
  


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('detect_file', help='The image for text detection.')
    parser.add_argument('-out_image', help='Optional output image file', default=0)
    parser.add_argument('-out_file', help='Optional output text file', default=0)

    args = parser.parse_args()

    parser = argparse.ArgumentParser()
    render_doc_text(args.detect_file, args.out_file, args.out_image)
