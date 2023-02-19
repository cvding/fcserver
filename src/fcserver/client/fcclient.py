import os
import cv2
import requests
import numpy as np

class FalconClient:
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers
        self.files = {}
    
    def push_file(self, file, file_key, is_img=False):
        if isinstance(file, bytes):
            self.files[file_key] = (file)
        elif isinstance(file, str) and os.path.isfile(file):
            bname = os.path.basename(file)
            self.files[file_key] = open(file, 'rb')
        elif isinstance(file, np.ndarray):
            if is_img:
                bstr = cv2.imencode('.jpg', file)[1].tostring()
                self.files[file_key] = bstr
            else:
                bstr = file.tobytes()
                self.files[file_key] = ("numpy", bstr, ','.join([str(i) for i in file.shape])+','+file.dtype.name)
        else:
            raise ValueError(r"check your file:{} or file_key:{}.".format(file, file_key))
    
    def send(self, query=None, data=None):
        res = requests.post(self.url, params=query, files=self.files, data=data)

        return res
