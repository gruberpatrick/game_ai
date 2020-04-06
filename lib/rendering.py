import cv2
import numpy as np


class Rendering:

    def __init__(self):

        self._img = self.initialize_canvas()

    def initialize_canvas(self, width=512, height=512):

        cv2.namedWindow('image')
        return np.zeros((width, height, 3), np.uint8)

    def reset_image(self, img):

        img[:, :, :] = 255

    def show_image(self, img, timeout=1000):

        cv2.imshow('image', img)
        cv2.waitKey(timeout)

    def destroy_image(self):

        cv2.destroyAllWindows()
