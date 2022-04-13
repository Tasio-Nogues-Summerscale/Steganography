from PIL import Image
import sys
import argparse
import numpy as np


def encode(image: Image, text: str) -> Image:
    """Encode text within an Image object"""
    #add stopping character to text
    text += chr(0)
    #convert text to a list of 1s,0s
    binary_text = [int(val) for val in 
                   "".join(format(ord(char), "08b") for char in text)]
   
    #cancel the operation if the text is too large for the image
    bin_len = len(binary_text)
    if bin_len > (image.width * image.height) * 3:
        raise ValueError("Text too large for this image")
    image_array = np.array(image)
    i = 0
    #iterate over x,y axes on the image
    for x in range(image.width):
        for y in range(image.height):
            #iterate over R,G,B values in a pixel
            for j in range(3):
                #alter least significant bit in binary value of r/g/b 
                #to match the value of binary_text[i]
                binary_val = (image_array[y][x][j] & ~1) | binary_text[i]
                image_array[y][x][j] = binary_val
                i += 1
                #return the image once done 
                if i == bin_len:
                    return Image.fromarray(image_array, "RGBA")


def decode(image: Image) -> str:
    """Extract hidden text from an Image object""" 
    binary_string = ""
    image_array = np.array(image)
    i = 0
    end_character = "0"*8
    #iterate over x,y axes on the image
    for x in range(image.width):
        for y in range(image.height):
            #iterate over R,G,B values in a pixel
            for j in range(3):
                #append least significant bit to binary_string
                binary_string += str(image_array[y][x][j] & 1)
                
                #check for the ending character every 8 bits
                if (i+1) % 8 == 0:
                    if binary_string[-8:] == end_character:
                        #decode binary string into uncovered text
                        binary_int = int(binary_string[:-8], 2) #convert to integer
                        return binary_int.to_bytes((binary_int.bit_length()+7)//8, "big").decode("iso-8859-1")
                i += 1


if __name__ == "__main__":
    #set up parser
    parser = argparse.ArgumentParser()
    #create mode_group to allow user to choose between encode and decode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-e", "--encode", action="store_true", help="Use the encoding function")
    mode_group.add_argument("-d", "--decode", action="store_true", help="Use the decoding function")
    parser.add_argument("-if","--imagefile", type=argparse.FileType('r'), help="Name of image file", required=True)
    parser.add_argument("-tf","--textfile", type=argparse.FileType('r'), help="Name of text file")
    parser.add_argument("-t", "--text", type=str, help="manual text input")
    parser.add_argument("-of", "--outputfile", type=str, help="Name of output file")
    args = parser.parse_args()

    img = Image.open(args.imagefile.name).convert("RGBA")
    #for encoding
    if args.encode:
        text = args.text
        if args.textfile:
            with open(args.textfile.name, "r") as f:
                text = f.read().rstrip() #remove trailing whitespace
        #remove non extended ascii characters - e.g. "♥" 
        text = text.encode("iso-8859-1","ignore").decode("iso-8859-1")
        new_img = encode(img, text)
        if args.outputfile: #save image to file
            new_img.save(args.outputfile)

    #for decoding
    elif args.decode: 
        text = decode(img)
        if args.outputfile: #save text to file
            with open(args.outputfile, "w") as f:
                f.write(text)
        else: #output to terminal
            print(text)
