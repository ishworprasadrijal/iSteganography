from PIL import Image
import numpy as np
import sys
import os.path
import cv2

import PIL.ImageDraw as draw
import csv
import math



MAX_ARGUMENTS_LIMIT = 4
encode_arg = "-e"
decode_arg = "-d"
help_arg = "--help"
help_txt = "SteganoPy is a python script that does Steganography"
dataPixels = []
slope = 1

def valid_pixels(dim):
    height, width = dim
    for i in range(0,width):
        append_pixel([[i,0]])
        append_pixel([[i,-slope*(i)+height]])
    for j in range(0,height):
        append_pixel([[0,j]])
    
def append_pixel(np):
    if not np in dataPixels:
        dataPixels.extend(np)

def writeout(entries):
    np.savetxt('original.csv', entries, delimiter=',')

def get_image(image_path):
    im = Image.open(image_path)
    return im

def edges(img):
    try:
        image = Image.open(img, 'r')
        img = cv2.imread(img,0)
        edges = cv2.Canny(img,100,200)
        cv2.imwrite('00_white_edge.png',edges)
        
    except (FileNotFoundError):
        print('Error: image not found')
        return

def edge_coordinates():
    im = cv2.imread('00_white_edge.png')
    im[np.where((im == [255,255,255]).all(axis = 2))] = [255,0,0]
    cv2.imwrite('01_blue_edge.png', im)

    im = cv2.imread('00_white_edge.png')
    im[np.where((im == [255,255,255]).all(axis = 2))] = [0,255,0]
    cv2.imwrite('02_green_edge.png', im)

    im = cv2.imread('00_white_edge.png')
    im[np.where((im == [255,255,255]).all(axis = 2))] = [0,0,255]
    cv2.imwrite('03_red_edge.png', im)

    im = cv2.imread('input.png')
    im[np.where((im <= 10).all(axis = 2))] = [0,0,255]
    cv2.imwrite('04_mixed_edge.png', im)

    return 0
    
def get_slope(dim):
    height,width = dim
    slope= width/height

def get_yc(x,m,c):
    mx = m * x + c
    return (int(mx))

# encode method takes image, width, rgb value and message
def encode(im, wh_couple, pixels, text):
    written = 0
    char_index = 0
    bit_index = 0
    write_limit = len(text) * 7
    print("Best Write Capacity: ",int(wh_couple[0]+wh_couple[1]+math.sqrt(wh_couple[0]*wh_couple[0]+wh_couple[1]*wh_couple[1]))*3,' Characters')
    (width, height) = wh_couple
    get_slope(wh_couple)
    valid_pixels(wh_couple)
    writeout(dataPixels)
    for w in range(width):
        if(w):
            for h in range(height):
                if [w,h] in dataPixels:
                    r, g, b = 0, 0, 0
                    for i in range(3):
                        color = pixels[w, h][i]
                        if written < write_limit:
                            bit = '{0:07b}'.format(ord(text[char_index]))[bit_index]
                            if color % 2 == 0 and bit == "1":
                                color += 1
                            elif color % 2 == 1 and bit == "0":
                                color -= 1
                            bit_index += 1
                            written += 1
                            if bit_index == 7:
                                bit_index = 0
                                char_index += 1
                        else:
                            if color % 2 == 1:
                                color -= 1
                        if i == 0:
                            r = color
                        elif i == 1:
                            g = color
                        elif i == 2:
                            b = color
                    pixels[w, h] = (r, g, b)

    return np.asarray(im)

def decode(wh_couple, pixels):
    bin_buffer = ""
    something_found = False
    broken = False
    bin_str = ""
    (width, height) = wh_couple
    calculate_psnr()
    get_slope(wh_couple)
    valid_pixels(wh_couple)
    for w in range(width):
        if(w):
            for h in range(height):
                if [w,h] in dataPixels:
                    r, g, b = pixels[w, h]

                    bit = "1" if r % 2 == 1 else "0"
                    bin_buffer += bit
                    if len(bin_buffer) == 7:
                        boolean, char = check_bin_buff(bin_buffer)
                        if boolean:
                            something_found = True
                            bin_str += char
                        else:
                            broken = True
                            break
                        bin_buffer = ""

                    bit = "1" if g % 2 == 1 else "0"
                    bin_buffer += bit
                    if len(bin_buffer) == 7:
                        boolean, char = check_bin_buff(bin_buffer)
                        if boolean:
                            something_found = True
                            bin_str += char
                        else:
                            broken = True
                            break
                        bin_buffer = ""
                    bit = "1" if b % 2 == 1 else "0"
                    bin_buffer += bit
                   
                    if len(bin_buffer) == 7:
                        boolean, char = check_bin_buff(bin_buffer)
                        if boolean:
                            something_found = True
                            bin_str += char
                        else:
                            broken = True
                            break
                        bin_buffer = ""

            if broken:
                break

    if something_found:
        return bin_str

    else:
        return None

def check_bin_buff(text):
    char_num = int(text, 2)
    if char_num == 0:
        return False, None
    else:
        return True, chr(char_num)

# encode function takes an arguement path, message and destination path
def encode_operation(path, text, save_path=None):
    original_image_path = path
    new_image_path = "en_"+path
    edges(original_image_path)

    new_image = get_image(original_image_path)
    pixels_rgb, wh = new_image.load(), new_image.size

    if wh[0] * wh[1] * 3 < len(text) * 7:
        print("Warning: Text too long for that image!")

    array = encode(new_image, wh, pixels_rgb, text)
    image = Image.fromarray(array)
    if save_path is None:
        image.save(new_image_path)
    else:
        image.save(save_path)


def decode_operation(path):
    edges(path)
    image = get_image(path)
    pixels_rgb, wh = image.load(), image.size
    text_found = decode(wh, pixels_rgb)
    print("Message: " + str(text_found))


def calculate_psnr():
    original = cv2.imread("input.png")
    contrast = cv2.imread("en_input.png",1)
    def psnr(img1, img2):
        mse = np.mean( (img1 - img2) ** 2 )
        if mse == 0:
            return 100
        PIXEL_MAX = 255.0
        return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))

    d=psnr(original,contrast)
    print("PSNR : ",d)    

def main():
    sys.stdout = sys.stderr
    if len(sys.argv) > MAX_ARGUMENTS_LIMIT + 1:
        print("ERROR: Max number of arguments exceeded!")
    elif len(sys.argv) == 1:
        print("ERROR: Too few arguments!")
        print("_"*100)
        print(help_txt)
    else:
        first_arg = sys.argv[1]
        if first_arg == encode_arg:
            second_arg = sys.argv[2]
            if second_arg == "" or second_arg is None:
                print("ERROR: Too few arguments!")
                return
            image_path = second_arg
            if not (image_path[-3:] != "png" or image_path[-4:] != "jpeg" or image_path[-3:] != "jpg"):
                print("ERROR: Only JPEG & PNG images allowed!")
                return
            elif not os.path.exists(image_path):
                print("ERROR: File not found!")
                return
            else:
                third_arg = sys.argv[3]
                text = third_arg
                if text == "" or text is None:
                    print("ERROR: No text to hide found!")
                    return
                if len(sys.argv) == 4:
                    encode_operation(image_path, str(text))
                elif len(sys.argv) == 5:
                    fourth_arg = sys.argv[4]
                    new_path = fourth_arg
                    if os.access(os.path.dirname(new_path), os.W_OK):
                        encode_operation(image_path, str(text), new_path)
                    else:
                        print("ERROR: Write restricted at '" + new_path + "' or it's a directory!")
                        return
                else:
                    print("ERROR: Too many arguments!")
                    return
        elif first_arg == decode_arg:
            second_arg = sys.argv[2]
            encoded_path = second_arg

            if second_arg == "" or second_arg is None:
                print("ERROR: Too few arguments!")
                return
            elif os.path.exists(encoded_path):
                decode_operation(encoded_path)
            else:
                print("ERROR: File not found!")
                return

        elif first_arg == help_arg:
            print(help_txt)
        else:
            print("ERROR: Unknown or no arguments! "+first_arg)
            return


main()
