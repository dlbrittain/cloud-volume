from six import StringIO, BytesIO

import gzip
import sys

import brotli

from .exceptions import DecompressionError, CompressionError
from .lib import yellow

COMPRESSION_TYPES = [ None, False, True, '', 'gzip', 'br' ]

def decompress(content, encoding, filename='N/A'):
  """
  Decompress file content. 

  Required: 
    content (bytes): a file to be compressed
    encoding: None (no compression) or 'gzip' or 'br'
  Optional:   
    filename (str:default:'N/A'): Used for debugging messages
  Raises: 
    NotImplementedError if an unsupported codec is specified. 
    compression.EncodeError if the encoder has an issue

  Return: decompressed content
  """
  try:
    encoding = (encoding or '').lower()
    if encoding == '':
      return content
    elif encoding == 'gzip':
      return gunzip(content)
    elif encoding == 'br':
      return brotli_decompress(content)
  except DecompressionError as err:
    print("Filename: " + str(filename))
    raise
  
  raise NotImplementedError(str(encoding) + ' is not currently supported. Supported Options: None, gzip')

def compress(content, method='gzip', compress_level=None):
  """
  Compresses file content.

  Required:
    content (bytes): The information to be compressed
    method (str, default: 'gzip'): None or gzip
  Raises: 
    NotImplementedError if an unsupported codec is specified. 
    compression.DecodeError if the encoder has an issue

  Return: compressed content
  """
  if method == True:
    method = 'gzip' # backwards compatibility

  method = (method or '').lower()

  if method == '':
    return content
  elif method == 'gzip': 
    return gzip_compress(content, compresslevel=compress_level)
  elif method == 'br':
    return brotli_compress(content, quality=compress_level)
  raise NotImplementedError(str(method) + ' is not currently supported. Supported Options: None, gzip')

def gzip_compress(content, compresslevel=None):
  if compresslevel is None:
    compresslevel = 9
  
  stringio = BytesIO()
  gzip_obj = gzip.GzipFile(mode='wb', fileobj=stringio, compresslevel=compresslevel)

  if sys.version_info < (3,):
    content = str(content)

  gzip_obj.write(content)
  gzip_obj.close()
  return stringio.getvalue()

def gunzip(content):
  """ 
  Decompression is applied if the first to bytes matches with
  the gzip magic numbers. 
  There is once chance in 65536 that a file that is not gzipped will
  be ungzipped.
  """
  gzip_magic_numbers = [ 0x1f, 0x8b ]
  first_two_bytes = [ byte for byte in bytearray(content)[:2] ]
  if first_two_bytes != gzip_magic_numbers:
    raise DecompressionError('File is not in gzip format. Magic numbers {}, {} did not match {}, {}.'.format(
      hex(first_two_bytes[0]), hex(first_two_bytes[1])), hex(gzip_magic_numbers[0]), hex(gzip_magic_numbers[1]))

  stringio = BytesIO(content)
  with gzip.GzipFile(mode='rb', fileobj=stringio) as gfile:
    return gfile.read()

def brotli_compress(content, quality=None):
  if quality is None:
    # 5/6 are good balance between compression speed and compression rate
    quality = 5
  return brotli.compress(content, quality=quality)

def brotli_decompress(content):
  return brotli.decompress(content)
