# fcserver
base on falcon framework， some useful tools
post image, numpy and json file or parameters

## install
`pip install git+https://github.com/cvding/fcserver.git`

## example
1. server(deploy model)
   ```python
    from fcserver import FalconServer, App
    from PIL import Image
    from wsgiref.simple_server import make_server


    class Server(FalconServer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            print('My server model loadding...')
        
        def on_post(self, req, resp):
            # pudb.set_trace()
            # print(req.params)
            # img_a = self.decode_image(req, 'aimg')
            img_a = self.decode_numpy(req, 'aimg')
            self.save_data('aimg.png', img_a)
            img_b = self.decode_image(req, 'bimg')
            self.save_data('bimg.png', img_b)

    s = Server('/ding')

    app = App()
    app.add_route('/ding', s)

    if __name__ == '__main__':
        with make_server('127.0.0.1', 8088, app) as httpd:
            httpd.serve_forever()
   ```
2. client(send data to server)
   ```python
    import cv2
    import json
    from fcserver import FalconClient

    if __name__ == '__main__':
        c = FalconClient('http://127.0.0.1:8088/ding', None)

        c.push_file(cv2.imread('./demo.png'), 'aimg', is_img=False)
        c.push_file('./demo2.png', 'bimg')
        # print(files)

        c.send(query={'test': [1, 2, 3]}, data={'a': [4, 5, 6]})
   ```
3. gunicorn(deploy the server)
`gunicorn --workers=2 --bind 0.0.0.0:8088 demo:app`
