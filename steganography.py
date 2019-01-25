#!/usr/bin/python3
from PIL import Image # sudo pip3 install Pillow
import getopt, sys

__author__ = "Samuel Rondeau"
__copyright__ = "Copyright 2015, steganography.py"
__credits__ = "Samuel Rondeau, DrapsTV"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Samuel Rondeau"
__email__ = "samuel.rondeau@polymtl.ca"
__status__ = "Prototype"
"""
This program is based on DrapsTV's Steganography Tutorial (https://youtu.be/q3eOOMx5qoo)
"""


# Delimiter
S_END_OF_MESSAGE = 'END'


def rgb2hex(r, g, b):
	"""Converts (r, g, b) values to hexadecimal string
    r, g and b are expected to be integers between 0 and 255
    Output will have the format '000000'
    such as rgb2hex(0, 255, 128) = '00ff80'
    """
	return '{:02x}{:02x}{:02x}'.format(r, g, b)


def hex2rgb(hex):
	"""Converts hexadecimal string to (r, g, b) int format
	Input is expected to be of format '000000' (3 bytes without '0x')
	Output will be a tuple (r, g, b)
	such as hex2rgb('00ff80') = (0, 255, 128)
	"""
	hex = -len(hex) % 6 * '0' + hex
	r = int(hex[-6:-4], 16)
	g = int(hex[-4:-2], 16)
	b = int(hex[-2:], 16)
	return r, g, b


def str2bin(message):
	"""Converts string to binary string
	Output will have the format '01011001'
	such as str2bin('test') = '01110100011001010111001101110100'
	"""
	s_bytes = bytes(message, 'ascii')
	s_bits = ['{:08b}'.format(byte) for byte in s_bytes]
	s_binary = ''.join(s_bits)
	return s_binary


def bin2str(binary):
	"""Converts binary string to string
	Input is expected to be of format '00000000' (without '0b')
	Output will have the format 'abcd'
	such as bin2str('01110100011001010111001101110100') = 'test'
	"""
	binary = -len(binary) % 8 * '0' + binary
	s_bits = [binary[byte : byte + 8] for byte in range(0, len(binary), 8)]
	s_chars = [chr(int(byte, 2)) for byte in s_bits]
	message = ''.join(s_chars)
	return message


def replace_last_bit(image_byte, message_bit):
	"""Replaces the last bit (LSB) of a byte string
	Input is expected to be of format '00' (without '0x')
	Output will have the format '01'
	such as replace_last_bit('ff', '0') = 'fe'
	"""
	message_bit = str(message_bit)
	s_byte = bytes(image_byte, 'ascii')
	s_bits = '{:08b}'.format(int(s_byte, 16))
	s_bits = s_bits[:-1] + message_bit
	s_byte = '{:02x}'.format(int(s_bits, 2))
	return s_byte

def get_last_bit(image_byte):
	"""Returns the last bit (LSB) of a byte string
	Input is expected to be of format '00' (without '0x')
	Output will have the format '0' (one char)
	such as get_last_bit('ff') = '1'
	"""
	s_byte = bytes(image_byte, 'ascii')
	s_bits = '{:08b}'.format(int(s_byte, 16))
	return s_bits[-1]


def hide_message(dest_img, msg):
	"""Hides a text string inside an image (numeric steganography)
	Image input should be a PNG image (currently the only supported format)
	Message input should be a regular text string (not another image)
	"""
	try:
		image_original = Image.open(dest_img)
	except (FileNotFoundError):
		print('Error: image not found')
		return

	binary = str2bin(msg) + str2bin(S_END_OF_MESSAGE)
	if image_original.mode in ('RGBA'):
		image_new = image_original.convert('RGBA')
		pixels_original = image_new.getdata()
		if len(binary) > len(pixels_original):
			print('The message is too long for the selected picture')
			return

		pixels_new = []
		nbBitsProcessed = 0
		for pixel in pixels_original:
			if nbBitsProcessed < len(binary):
				s_hex = rgb2hex(pixel[0], pixel[1], pixel[2])
				# TODO change 3 bytes instead of only 1 and support pattern
				s_pixel = replace_last_bit(s_hex, binary[nbBitsProcessed])
				r, g, b = hex2rgb(s_pixel)
				pixels_new.append((r, g, b, pixel[3]))

			else:
				pixels_new.append(pixel)

			nbBitsProcessed += 1

		image_new.putdata(pixels_new)
		s_new_image_path = dest_img.replace('.png', '') + '_s' + '.png'
		image_new.save(s_new_image_path, 'PNG')

		print('Success! ' + str(nbBitsProcessed // 8) + ' bytes processed.')
		print('New image saved as \"' + s_new_image_path + '\"')

	else:
		print('Source file incompatible.')


def hide_file(dest_img, filepath):
	"""Hides a text file inside an image (numeric steganography)
	Image input should be a PNG image (currently the only supported format)
	File input should be a regular text file (not another image)
	"""
	try:
		f = open(filepath, 'r')
		hide_message(dest_img, f.read())
	except (FileNotFoundError):
		print('Error: file not found')


def find_message(src_img):
	"""Finds a message hidden in an image (numeric steganography)
	Image input should be a PNG image (currently the only supported format)
	Message must end with S_END_OF_MESSAGE
	"""
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
			if binary[-len(str2bin(S_END_OF_MESSAGE)):] == str2bin(S_END_OF_MESSAGE):
				print('Message recovered!')
				return bin2str(binary[:-len(str2bin(S_END_OF_MESSAGE))])
		print('Message or delimiter not found')
		return ''
	else:
		print('Source file incompatible.')


def save_message(src_img, filepath):
	"""Finds a message hidden in an image (numeric steganography) and saves it to a text file
	Image input should be a PNG image (currently the only supported format)
	Message must end with S_END_OF_MESSAGE
	"""
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
		opts, args = getopt.getopt(argv,'hedi:f:m:',['help', 'encode', 'decode', 'image=', 'file=', 'message='])
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
		print('You must select a mode: --encode (-e) or --decode (-d)')
		sys.exit(1)
	if mode =='encode' and not message and not filepath:
		print('You must provide a message or a file to encode with --message (-m) or --file (-f)')
		sys.exit(1)
	if mode == 'decode' and message:
		print('--decode cannot be used with --message')
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

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	except (KeyboardInterrupt):
		print()
		sys.exit(1)
