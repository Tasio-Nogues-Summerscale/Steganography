from PIL import Image
import sys
import argparse
import numpy as np



def encode(image: Image, text: str) -> Image:
    text += chr(0)
    binary_text = [int(val) for val in "".join(format(ord(char), "08b") for char in text)]
    
    bin_len = len(binary_text)
    if bin_len > (image.width * image.height) * 3:
        raise ValueError("Text too large for this image")
    image_array = np.array(image)
    i = 0
    for x in range(image.width):
        for y in range(image.height):
            for j in range(3):
                binary_val = (image_array[y][x][j] & ~1) | binary_text[i]
                image_array[y][x][j] = binary_val
                i += 1
                if i == bin_len:
                    return Image.fromarray(image_array, "RGBA")


def decode(image: Image):
    binary_string = ""
    image_array = np.array(image)
    i = 0
    for x in range(image.width):
        for y in range(image.height):
            for j in range(3):
                binary_string += str(image_array[y][x][j] & 1)
                
                if (i+1) % 8 == 0:
                    if binary_string[-8:] == "00000000":
                        binary_int = int(binary_string[:-8], 2) #convert to integer
                        return binary_int.to_bytes((binary_int.bit_length() + 7) //8, "big").decode("iso-8859-1")
                i += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--encode", action="store_true", help="Use the encoding function")
    parser.add_argument("-d", "--decode", action="store_true", help="Use the decoding function")
    parser.add_argument("-if","--imagefile", type=argparse.FileType('r'), help="Name of image file", required=True)
    parser.add_argument("-tf","--textfile", type=argparse.FileType('r'), help="Name of text file")
    parser.add_argument("-t", "--text", type=str, help="manual text input")
    parser.add_argument("-of", "--outputfile", type=str, help="Name of output file")
    args = parser.parse_args()


    if not(any([(args.encode or args.decode), args.imagefile])):
        sys.exit()

    img = Image.open(args.imagefile.name).convert("RGBA")

    if args.encode:
        text = args.text
        if args.textfile:
            with open(args.textfile.name, "r") as f:
                text = f.read().rstrip()

        text = text.encode("iso-8859-1","ignore").decode("iso-8859-1")
        new_img = encode(img, text)
        if args.outputfile:
            new_img.save(args.outputfile)

    elif args.decode:
        text = decode(img)
        if args.outputfile:
            with open(args.outputfile, "w") as f:
                f.write(text)
        else:
            print(text)
