import pytesseract
import re


def read_number(img):
    custom_config = r'--oem 3 --psm 10 digits'
    d = pytesseract.image_to_data(img, lang="eng", config=custom_config, output_type=pytesseract.Output.DICT)
    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 40:
            if re.match('^[-+]?\d*\.?\d*$', d['text'][i]):
                s = d['text'][i].replace(".", "")
                # Şu ana kadar yaptığım en zor type cast
                return int(s)
    return None

