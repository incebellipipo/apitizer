import requests
import numpy as np
import cv2
import pytesseract
import re
from datetime import datetime
from bs4 import BeautifulSoup

from apitizer.month_conversion import MONTHS


class ImageParser:
    def __init__(self, config):
        self.url = config["url"]
        self.image = None
        self.resp_data = None
        self.config = config
        self.value = dict()
        self.last_update = None

    def find_image_in_page(self):
        resp = requests.get(self.url)
        txt = resp.text
        soup = BeautifulSoup(txt, 'lxml')
        img_tags = soup.find_all('img')
        for i in img_tags:
            if re.match('^.*-1.jpg$', i["src"]):
                return i["src"]

        return None

    def fetch_image(self):

        img_url = self.find_image_in_page()
        resp = requests.get(self.url + img_url, stream=True).raw
        resp_data = resp.read()

        if self.resp_data == resp_data:
            return False
        self.last_update = datetime.now().isoformat()
        self.resp_data = resp_data
        image = np.asarray(bytearray(self.resp_data), dtype="uint8")
        self.image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return True

    @staticmethod
    def scale_image(img):
        width = img.shape[1]
        height = img.shape[0]
        scale = 40.0 / height
        dim = (int(width * scale), int(height * scale))
        return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    @staticmethod
    def read_number(img, _type=int):
        img = ImageParser.scale_image(img)
        custom_config = r'--oem 3 --psm 10 digits -c tessedit_char_whitelist=01234567890'
        d = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
        for i in range(len(d['text'])):
            if int(d['conf'][i]) > 40:
                if re.match('^[-+]?\d*\.?\d*$', d['text'][i]):
                    s = d['text'][i]
                    if _type == int:
                        s = s.replace(".", "")
                    # Şu ana kadar yaptığım en zor type cast
                    return _type(s)
        return None

    @staticmethod
    def read_text(img, _type=str):
        custom_config = r'--oem 3 --psm 10'
        d = pytesseract.image_to_data(img, lang="tur", config=custom_config, output_type=pytesseract.Output.DICT)
        for i in range(len(d['text'])):
            if int(d['conf'][i]) > 40:
                if re.match('^[a-zA-Z]+$', d['text'][i]):
                    s = d['text'][i]
                    # Şu ana kadar yaptığım en zor type cast
                    return _type(s)
        return None

    def preprocess_image(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.threshold(self.image, 245, 255, cv2.THRESH_TRUNC)[1]
        self.image = cv2.threshold(self.image, 185, 255, cv2.THRESH_TOZERO)[1]
        self.image = cv2.bitwise_not(self.image)
        kernel = np.ones((3, 3), np.uint8)
        self.image = cv2.dilate(self.image, kernel, iterations=1)
        self.image = cv2.GaussianBlur(self.image, (3, 3), 0)

    def parse_image(self, config):
        value = dict()
        for field in config["fields"]:
            if "fields" in field:
                sub_val = self.parse_image(field)
                if "type" not in field:
                    value[field["key"]] = sub_val
                else:
                    if field["type"] == "date":
                        month = MONTHS[sub_val["month"].lower()]
                        value[field["key"]] = f"%d-%d-%d" % (sub_val["year"], month, sub_val["day"])
                continue
            up = field["bounds"]["up"]
            bottom = field["bounds"]["bottom"]
            left = field["bounds"]["left"]
            right = field["bounds"]["right"]
            if field["type"] != "string":
                val = self.read_number(self.image[up:bottom, left:right], int)
            else:
                val = self.read_text(self.image[up:bottom, left:right])

            if val is None:
                print(f"cant read key: %s" % field['key'])

            key = field['key']
            value[key] = val
        return value

    def get_results(self):
        if self.fetch_image():
            self.preprocess_image()
            self.value = self.parse_image(self.config)
        self.value["last_update"] = self.last_update
        return self.value
