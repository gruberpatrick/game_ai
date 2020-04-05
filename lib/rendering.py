import cv2
import numpy as np
import time


def initialize_canvas():

    cv2.namedWindow('image')
    img = np.zeros((512, 512, 3), np.uint8)
    return img


def reset_image(img):

    img[:, :, :] = 255


def show_image(img, timeout=1000):

    cv2.imshow('image', img)
    cv2.waitKey(timeout)


def destroy_image():

    cv2.destroyAllWindows()


if __name__ == "__main__":
    img = initialize_canvas()
    show_image(img)
    destroy_image()
