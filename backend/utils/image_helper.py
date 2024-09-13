import cv2
import numpy as np


WANTED_WIDTH = 1920
WANTED_HEIGHT = 1080


def resize_to_fhdish(img_array: np.ndarray):
    height, width = img_array.shape[:2]

    width_scaling_factor = WANTED_WIDTH / float(width)
    height_scaling_factor = WANTED_HEIGHT / float(height)

    scaling_factor = min(width_scaling_factor, height_scaling_factor)

    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    # Resize the image using the INTER_AREA interpolation for better quality on downscaling
    resized_img = cv2.resize(
        img_array, (new_width, new_height), interpolation=cv2.INTER_AREA
    )

    return resized_img, scaling_factor


if __name__ == "__main__":
    from gdrive_integration import download_file, create_drive_service

    # suur_pilt = download_file(create_drive_service(), "1ZiYpVSsuJATr8-eiWksL9QOYLhyFaI-l")
    # suur_pilt = cv2.imread("pilt.jpg")
    # print("kuvan suurt pilti")
    # cv2.namedWindow("img")
    # cv2.imshow("img", suur_pilt)

    # cv2.waitKey(1000)
    # cv2.destroyAllWindows()

    # print(type(suur_pilt))
    # vaike_pilt, _s = resize_to_fhdish(suur_pilt)

    # print("kuvan väikest pilti", _s)
    # cv2.namedWindow("img")

    # cv2.imshow("img", vaike_pilt)
    # cv2.waitKey(5000)
    # cv2.destroyAllWindows()
    ...
