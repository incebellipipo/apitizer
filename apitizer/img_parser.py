import requests
import numpy as np
import cv2
import pytesseract
import re


class ImageParser:
    def __init__(self, config, url):
        self.url = url
        self.image = None

        self.config = config
        self.value = dict()

    def fetch_image(self):
        resp = requests.get(self.url, stream=True).raw
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        self.image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    @staticmethod
    def read_number(img, _type=int):
        custom_config = r'--oem 3 --psm 10 digits'
        d = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
        for i in range(len(d['text'])):
            if int(d['conf'][i]) > 40:
                if re.match('^[-+]?\d*\.?\d*$', d['text'][i]):
                    s = d['text'][i].replace(".", "")
                    # Şu ana kadar yaptığım en zor type cast
                    return _type(s)
        return None

    def preprocess_image(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        self.image = cv2.bitwise_not(self.image)
        self.image = cv2.GaussianBlur(self.image, (7, 7), 0)

    def parse_image(self):
        for field in self.config["fields"]:
            up = field["bounds"]["up"]
            bottom = field["bounds"]["bottom"]
            left = field["bounds"]["left"]
            right = field["bounds"]["right"]
            number = self.read_number(self.image[up:bottom, left:right], int)
            if number is None:
                print(f"cant read key: %s" % field['key'])
            key = field['key']
            self.value[key] = number
