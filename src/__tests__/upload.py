import requests as rq
import argparse
import time
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

class Tester:
    def __init__(self, args) -> None:
        self.api_url = 'http://127.0.0.1:8888/predict'
        self.img_path = args.img_path

    def predict(self):
        files = [
            ('files', open(self.img_path, 'rb')),
        ]
        resp = rq.post(url=self.api_url, files=files)

        test_img_storage = os.path.join(dir_path, "test_imgs")
        if not os.path.exists(test_img_storage):
            os.mkdir(test_img_storage)

        with open(os.path.join(test_img_storage, f"{time.time()}.png"), "wb") as f:
            f.write(resp.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_path', type=str, required=True)
    args = parser.parse_args()

    tester = Tester(args=args)
    tester.predict()
