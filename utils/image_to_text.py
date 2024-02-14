from typing import List, Any, Sequence
import cv2
import numpy as np
import pandas as pd
import easyocr
from pathlib import Path


class ImageProcessor:

    def __init__(
            self,
            image_path: Path,  # noqa
            x_scale: int = 3,
            y_scale: int = 8,
            channel: int = 3) -> None:
        self.image_path = image_path
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.channel = channel

    def load_image(self) -> np.ndarray:
        image = cv2.imread(str(self.image_path))
        if self.channel == 1:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.resize(
            image,
            (image.shape[1] * self.x_scale, image.shape[0] * self.y_scale))

    def apply_kmeans(self, image: np.ndarray, k: int = 2) -> np.ndarray:
        pixels = np.float32(image.reshape((-1, self.channel)))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100,
                    0.2)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10,
                                        cv2.KMEANS_PP_CENTERS)
        centers = np.uint8(centers)
        return centers[labels.flatten()].reshape(image.shape)

    @staticmethod
    def combinator(segmented_image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGB2GRAY)
        _, binary_image = cv2.threshold(gray, 127, 255, cv2.THRESH_OTSU)
        return binary_image

    @staticmethod
    def find_contours(
        binary_image: np.ndarray
    ) -> Sequence[np.ndarray | np.ndarray[Any, np.dtype[np.generic
                                                        | np.generic]]
                  | Any]:
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        return contours

    @staticmethod
    def paint_contours(segmented_image: np.ndarray,
                       contours: List[np.ndarray]) -> np.ndarray:
        for contour in contours:
            cv2.fillPoly(segmented_image, pts=[contour], color=(255, 255, 255))
        return cv2.cvtColor(segmented_image, cv2.COLOR_RGB2GRAY)

    def process_diff(self, binary_image: np.ndarray,
                     image: np.ndarray) -> np.ndarray:
        diff = np.max(binary_image) - cv2.absdiff(binary_image, image)
        _, diff = cv2.threshold(diff, 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        diff = cv2.bitwise_not(diff)
        kernel = np.ones((3, 3), np.uint8)
        diff = cv2.dilate(diff, kernel, iterations=2)
        diff = cv2.erode(diff, kernel, iterations=2)
        diff = cv2.normalize(diff, kernel, 0, 255, cv2.NORM_MINMAX)
        return cv2.resize(
            diff,
            (diff.shape[1] // self.x_scale, diff.shape[0] // self.y_scale))

    @staticmethod
    def read_text(diff: np.ndarray) -> pd.DataFrame:
        reader = easyocr.Reader(lang_list=["en"],
                                model_storage_directory="./model_path",
                                download_enabled=True,
                                recog_network="english_g2")
        text = reader.readtext(diff,
                               decoder="wordbeamsearch",
                               workers=0,
                               batch_size=100,
                               allowlist="ABCX027")
        return pd.DataFrame(text)

    @staticmethod
    def valuation(df: pd.DataFrame) -> None:
        list_of_words = df[1].str.split(" ", expand=True).values.flatten()
        list_of_words = list_of_words[~pd.isnull(list_of_words)]
        list_of_words = list_of_words[list_of_words != ""]
        accepted_words = ["C07", "X", "A02", "B07"]
        wrong_words = list(
            filter(lambda x: x not in accepted_words, list_of_words))
        print(wrong_words[:5])
        print(len(wrong_words))

    def process_image(self) -> None:
        image = self.load_image()
        segmented_image = self.apply_kmeans(image)
        binary_image = self.combinator(segmented_image)
        contours = self.find_contours(binary_image)
        image = self.paint_contours(segmented_image, contours)
        diff = self.process_diff(binary_image, image)
        df = self.read_text(diff)
        self.valuation(df)


if __name__ == "__main__":
    image_path = Path("data/feb_test.png")
    processor = ImageProcessor(image_path)
    processor.process_image()
