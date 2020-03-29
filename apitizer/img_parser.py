import requests
import numpy as np
import cv2
import pytesseract
import re
from datetime import datetime

from apitizer.month_conversion import MONTHS


class ImageParser:
    def __init__(self, config):
        self.url = config["url"]
        self.image = None
        self.resp_data = None
        self.config = config
        self.value = dict()

    def fetch_image(self):
        resp = requests.get(self.url, stream=True).raw
        resp_data = resp.read()
        if self.resp_data == resp_data:
            return False
        self.resp_data = resp_data
        image = np.asarray(bytearray(self.resp_data), dtype="uint8")
        self.image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return True

    @staticmethod
    def read_number(img, _type=int):
        custom_config = r'--oem 3 --psm 10 digits'
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
        self.image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        self.image = cv2.bitwise_not(self.image)
        self.image = cv2.GaussianBlur(self.image, (7, 7), 0)

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
            self.value["last_update"] = datetime.now().isoformat()
        return self.value
