import argparse
import numpy as np
import cv2
import pytesseract


def get_numbers_from_text(text):
    number = [s for s in text if s.isdigit()]
    return "".join(number)


def parse_hp(image, debug=False):
    h, w, _ = image.shape
    if w == 1920 and h == 1080:
        cropped = image[82:116, 896:1053]
    elif w == 2160 and h == 1440:
        cropped = image[221:259, 1008:1180]
    elif w == 2280 and h == 1080:
        cropped = image[82:116, 1117:1271]
    elif w == 2960 and h == 1440:
        cropped = image[110:154, 1397:1601]
    if debug:
        cv2.imwrite("1 cropped.png", cropped)

    lower_color = np.array([160, 160, 160])
    upper_color = np.array([255, 255, 255])
    mask = cv2.inRange(cropped, lower_color, upper_color)
    if debug:
        cv2.imwrite("2 mask.png", mask)
    thres = cv2.bitwise_not(mask)
    if debug:
        cv2.imwrite("5 thres.png", thres)

    ocr_text = pytesseract.image_to_string(thres, config='-l eng --oem 1 --psm 7')
    if debug:
        print(f"raw Tesseract text: {ocr_text}")
    ocr_text = get_numbers_from_text(ocr_text)
    return ocr_text


def parse_image(image, debug=True):
    image = cv2.imread(image)
    if image is None:
        return f"OpenCV can't read {image}"
    return parse_hp(image, debug)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--image", required=True, help="Input image")
    arg_parser.add_argument("-d", "--debug", action='store_true', help="Write debug images")
    args = arg_parser.parse_args()
    result = parse_image(args.image, args.debug)
    print(result)
