from apitizer import \
    fetch_image, \
    read_text, \
    preprocess_image

import cv2
import json


def main():
    img = fetch_image.url_to_cv2("https://covid19.saglik.gov.tr/img/1.jpg")
    img = preprocess_image.preprocess_image(img)

    with open('config/config.json') as f:
        config = json.load(f)

    for field in config["fields"]:
        up = field["bounds"]["up"]
        bottom = field["bounds"]["bottom"]
        left = field["bounds"]["left"]
        right = field["bounds"]["right"]
        number = read_text.read_number(img[up:bottom, left:right])
        if number is None:
            cv2.imshow("none", img[up:bottom, left:right])
            cv2.waitKey(0)
            exit(130)
        key = field['key']
        print(f"%s: %d " % (key, number))

if __name__ == "__main__":
    main()