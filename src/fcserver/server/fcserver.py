import os
import falcon
import requests
import cv2
from io import BytesIO
from PIL import Image
import numpy as np
from .multipart import MultipartMiddleware


class FalconServer:
    def __init__(self, chunk_size=4096, decode='pillow'):
        self.chunk_size = chunk_size
        self.__image_decode = FalconServer._decode_img2pil if decode == 'pillow' else FalconServer._decode_img2npy

    def get_binary(self, req):
        chunks = b''
        while True:
            chunk = req.bounded_stream.read(self.chunk_size)
            if not chunk:
                break
            chunks += chunk
        return chunks
    
    def decode_image(self, req, file_key):
        image_file = req.get_param(file_key)
        image = self.__image_decode(image_file.file.read())

        return image
    
    def decode_numpy(self, req, file_key):
        numpy_file = req.get_param(file_key)
        types = numpy_file.type.split(',')
        dtype = types[-1]
        shape = [int(s) for s in types[:-1]]
        numpy_byte = numpy_file.file.read()
        data = np.asarray(bytearray(numpy_byte), dtype=dtype).reshape(shape)

        return data
    
    @staticmethod
    def _decode_img2pil(inp_buf):
        if isinstance(inp_buf, bytes):
            img = np.asarray(bytearray(inp_buf), dtype='uint8')
            image = cv2.imdecode(img, cv2.IMREAD_COLOR)
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        elif isinstance(inp_buf, str) and os.path.exists(inp_buf):
            image = Image.open(inp_buf)
            image = image.convert('RGB')
        elif isinstance(inp_buf, str) and 'http' == inp_buf.strip()[:4]:
            resp = requests.get(inp_buf)
            image = Image.open(BytesIO(resp.content))
            image = image.convert('RGB')
        elif isinstance(inp_buf, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(inp_buf, cv2.COLOR_BGR2RGB))
        elif isinstance(inp_buf, Image.Image):
            image = inp_buf
        else:
            raise ValueError("Error: Not support this type image buffer(byte, str, np.ndarry, PIL.Image)")
        
        return image
    
    @staticmethod
    def _decode_img2npy(inp_buf):
        if isinstance(inp_buf, bytes):
            img = np.asarray(bytearray(inp_buf), dtype='uint8')
            image = cv2.imdecode(img, cv2.IMREAD_COLOR)
        elif isinstance(inp_buf, str) and os.path.isfile(inp_buf):
            image = cv2.imread(inp_buf, cv2.IMREAD_COLOR)
        elif isinstance(inp_buf, str) and 'http' == inp_buf.strip()[:4]:
            resp = requests.get(inp_buf)
            image = cv2.imdecode(np.fromstring(resp.content, np.unit8), 1)
        elif isinstance(inp_buf, np.ndarray):
            image = inp_buf
        elif isinstance(inp_buf, Image.Image):
            image = cv2.cvtColor(np.asarray(inp_buf), cv2.COLOR_RGB2BGR)
        else:
            image = None
            raise ValueError('Error: Not support this type image buffer(byte, str, np.ndarry, PIL.Image)')

        return image

    @staticmethod 
    def save_data(file_path, image):
        if isinstance(image, Image.Image):
            image.save(file_path)
        elif isinstance(image, np.ndarray):
            if file_path.endswith(('.npy')):
                np.save(file_path, image)
            elif len(image.shape) in [2, 3]:
                cv2.imwrite(file_path, image)
        else:
            pass

class App(falcon.App):
    def __init__(self,*args, **kwargs):
        super().__init__(middleware=MultipartMiddleware())
                
