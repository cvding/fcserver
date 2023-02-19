import sys

# sys.path.insert(0, '../src')

import cv2
import json
from fcserver import FalconClient

if __name__ == '__main__':
    c = FalconClient('http://127.0.0.1:8088/ding', None)

    c.push_file(cv2.imread('./demo.png'), 'aimg', is_img=False)
    c.push_file('./demo2.png', 'bimg')
    # print(files)

    c.send(query={'test': [1, 2, 3]}, data={'a': [4, 5, 6]})