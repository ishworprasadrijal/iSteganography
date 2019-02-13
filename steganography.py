""" 
	This program is based on DrapsTV's Steganography Tutorial (https://youtu.be/q3eOOMx5qoo)
	
	python steganography.py --encode --message "JPT message hiding ..." --image "edge.png"
	python steganography.py --decode --image "edge_s.png"
	python steganography.py --edge --image "edge.png"
	python steganography.py --ends --image "triangle.png"

"""

""" IMPORT LIBRARIES """

from PIL import Image
import getopt, sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
from pprint import pprint


""" GLOBAL VARIABLES """

s_terminate = 'END'


""" RGB TO HEX CONVERSION """

def rgb2hex(r, g, b):
	return '{:02x}{:02x}{:02x}'.format(r, g, b)

""" HEX TO RGB CONVERSION """

def hex2rgb(hex):
	hex = -len(hex) % 6 * '0' + hex
	r = int(hex[-6:-4], 16)
	g = int(hex[-4:-2], 16)
	b = int(hex[-2:], 16)
	return r, g, b

""" STRING TO BINARY CONVERSION """

def str2bin(message):
	s_bytes = bytes(message, 'ascii')
	s_bits = ['{:08b}'.format(byte) for byte in s_bytes]
	s_binary = ''.join(s_bits)
	return s_binary

""" BINARY TO STRING CONVERSION """

def bin2str(binary):
	binary = -len(binary) % 8 * '0' + binary
	s_bits = [binary[byte : byte + 8] for byte in range(0, len(binary), 8)]
	s_chars = [chr(int(byte, 2)) for byte in s_bits]
	message = ''.join(s_chars)
	return message

""" REPLACE LAST BIT WITH MESSAGE BIT """

def replace_last_bit(image_byte, message_bit):
	message_bit = str(message_bit)
	s_byte = bytes(image_byte, 'ascii')
	s_bits = '{:08b}'.format(int(s_byte, 16))
	print(s_bits[:-1] + message_bit)
	s_bits = s_bits[:-1] + message_bit
	s_byte = '{:02x}'.format(int(s_bits, 2))
	return s_byte

""" FIND LAST BIT """

def get_last_bit(image_byte):
	s_byte = bytes(image_byte, 'ascii')
	s_bits = '{:08b}'.format(int(s_byte, 16))
	return s_bits[-1]

""" HIDE MESSAGE """

def hide_message(dest_img, msg):
	try:
		image_original = Image.open(dest_img)
	except (FileNotFoundError):
		print('Error: image not found')
		return

	binary = str2bin(msg) + str2bin(s_terminate)
	print("Message to Binary : ")
	print(binary)
	print("CHARACTERS to be encoded : ")
	print(len(binary)/8 -3)
	print("=======================================================================")

	if image_original.mode in ('RGBA'):
		image_new = image_original.convert('RGBA')
		pixels_original = image_new.getdata()
		print("CHARACTERS that can be encoded in this image : ")
		print(len(pixels_original)/8 -3)
		print("=======================================================================")
		if len(binary) > len(pixels_original):
			print('The message is too long for the selected picture')
			return

		pixels_new = []
		nbBitsProcessed = 0

		for pixel in pixels_original:
			if nbBitsProcessed < len(binary):
				s_hex = rgb2hex(pixel[0], pixel[1], pixel[2])
				s_pixel = replace_last_bit(s_hex, binary[nbBitsProcessed])
				print(pixel)
				# print("(message_bit, x, y) : ("+binary[nbBitsProcessed]+", "+s_hex+","+s_pixel+") : ")
				r, g, b = hex2rgb(s_pixel)
				pixels_new.append((r, g, b, pixel[3]))

			else:
				pixels_new.append(pixel)

			nbBitsProcessed += 1

		image_new.putdata(pixels_new)
		s_new_image_path = dest_img.replace('.png', '') + '_s' + '.png'
		image_new.save(s_new_image_path, 'PNG')

		print('Success! ' + str(nbBitsProcessed // 8 -3) + ' bytes processed.')
		print('New image saved as \"' + s_new_image_path + '\"')

	else:
		print('Source file incompatible.')


def hide_file(dest_img, filepath):
	try:
		f = open(filepath, 'r')
		hide_message(dest_img, f.read())
	except (FileNotFoundError):
		print('Error: file not found')


def find_message(src_img):
	try:
		image = Image.open(src_img)
	except (FileNotFoundError):
		print('Error: image not found')
		return

	binary = ''
	if image.mode in ('RGBA'):
		image = image.convert('RGBA')
		pixels = image.getdata()

		for pixel in pixels:
			s_hex = rgb2hex(pixel[0], pixel[1], pixel[2])
			s_bit = get_last_bit(s_hex)
			binary += s_bit
			print(bin2str(binary[-len(str2bin(s_terminate)):]))
			if binary[-len(str2bin(s_terminate)):] == str2bin(s_terminate):
				print('Message recovered!')
				return bin2str(binary[:-len(str2bin(s_terminate))])
		print('Message or delimiter not found')
		return ''
	else:
		print('Source file incompatible.')


def find_edge(img):
	try:
		print("Finding edges in "+img+" :");
		print("============================")
		img = cv2.imread(img,0)
		# img = cv2.medianBlur(img, 1)
		edges = cv2.Canny(img,100,200)

		indices = np.where(edges != [0])
		print("The edge coordinates are :")
		print("============================")
		pprint(indices)
		print("============================")
		coordinates = zip(indices[0], indices[1])
		print(list(coordinates))
		np.savetxt("coordinates.csv", indices, delimiter=",")
		# print("Let an ant starts from P("+indices[0]+","+indices[1]+")")

		plt.subplot(121),plt.imshow(img,cmap = 'gray')
		plt.title('Original Image'), plt.xticks([]), plt.yticks([])
		plt.subplot(122),plt.imshow(edges,cmap = 'gray')
		plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
		plt.show()
	except (FileNotFoundError):
		print('Error: image not found')
		return

def resize_image(img):
	try:
		img = Image.open(img)
		img = img.resize((20, 20), Image.ANTIALIAS)
		img.save('resized.png')

	except (FileNotFoundError):
		print('Error: file not found')
		sys.exit(1)

def save_message(src_img, filepath):
	try:
		f = open(filepath, 'w')
		f.write(find_message(src_img))
	except (FileNotFoundError):
		print('Error: file not found')


def usage():
	print('Usage: ' + __file__ + ' [mode] [image] [text]')
	print()
	print('Mode:\t\t\ttest')
	print('-e, --encode\t\thide a message in an image')
	print('-d, --decode\t\trecover a message in an image')
	print()
	print('Image:')
	print('-i IMG, --image=IMG\tPNG image used as source and destination')
	print()
	print('Text:')
	print('-m, MSG --message=MSG\tmessage to hide (use quotation marks "" if necessary)')
	print('-f FILE, --file=FILE\tsource file for encoding or destination file for decoding')


def main(argv):
	try:
		opts, args = getopt.getopt(argv,'hedi:f:m:',['help', 'encode', 'decode', 'edge', 'ends', 'image=', 'file=', 'message='])
	except getopt.GetoptError:
		usage()
		sys.exit(1)

	mode = ''
	image = ''
	message = ''
	filepath = ''
	for opt, arg in opts:
		# Help
		if opt in ('-h', '--help'):
			usage()
			sys.exit(1)

		# Mode (mutually exclusive)

		# Encode
		if opt in ('-e', '--encode'):
			if mode:
				print('--encode cannot be used with --decode')
				sys.exit(1);
			mode = 'encode'

		# Decode
		elif opt in ('-d', '--decode'):
			if mode:
				print('--encode cannot be used with --decode')
				sys.exit(1);
			mode = 'decode'

		# Edge
		elif opt in ('-ed', '--edge'):
			if mode:
				print('--edge cannot be used')
				sys.exit(1);
			mode = 'edge'

		# End Points
		elif opt in ('-ep', '--ends'):
			if mode:
				print('--ends cannot be used')
				sys.exit(1);
			mode = 'ends'

		# Input (mutually exclusive)

		# Message
		if opt in ('-m', '--message'):
			if message or filepath:
				print('--message cannot be used with --file')
				sys.exit(1);
			message = arg

		# File
		if opt in ('-f', '--file'):
			if filepath or message:
				print('--message cannot be used with --file')
				sys.exit(1);
			filepath = arg

		# Image
		if opt in ('-i', '--image'):
			if image:
				print('You must provide only one image')
				sys.exit(1);
			image = arg


	
	# Validation
	if not mode:
		print('You must select a mode: --encode (-e) or --decode (-d) or --edge (-ed)')
		sys.exit(1)
	if mode =='encode' and not message and not filepath:
		print('You must provide a message or a file to encode with --message (-m) or --file (-f)')
		sys.exit(1)
	if mode == 'decode' and message:
		print('--decode cannot be used with --message')
		sys.exit(1)
	if mode == 'edge' and message:
		print('--edge cannot be used with --message')
		sys.exit(1)
	if mode == 'ends' and message:
		print('--ends cannot be used with --message')
		sys.exit(1)
	if not image:
		print('You must provide an image filepath with --image (-i)')
		sys.exit(1)

	# Execution
	if mode == 'encode':
		if message:
			hide_message(image, message)
		elif filepath:
			hide_file(image, filepath)
	elif mode == 'decode':
		if not filepath:
			print(find_message(image))
		else:
			save_message(image, filepath)
	elif mode == 'edge':
		if not message:
			print(find_edge(image))
		else:
			print('Finding edges ...')
			sys.exit(1)
	elif mode == 'ends':
		if not message:
			print(image)
			print(resize_image(image))
		else:
			print('Finding edges ...')
			sys.exit(1)

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	except (KeyboardInterrupt):
		print()
		sys.exit(1)
