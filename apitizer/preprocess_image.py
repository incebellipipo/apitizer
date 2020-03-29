import cv2


def preprocess_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    img = cv2.bitwise_not(img)
    img = cv2.GaussianBlur(img, (7, 7), 0)
    return img