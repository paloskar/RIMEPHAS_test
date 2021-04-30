# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""An example using `DetectionEngine` to perform object/face detection
with an image.

The following command runs this example for object detection using a
MobileNet model trained with the COCO dataset (it can detect 90 types
of objects). It saves a copy of the given image at the location specified by
`output`, with bounding boxes drawn around each detected object.

python3 object_detection.py \
--model models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
--label models/coco_labels.txt \
--input images/grace_hopper.bmp \
--output ${HOME}/object_detection_results.jpg

If you pass a model trained to detect faces, you can exclude the `label`
argument:

python3 object_detection.py \
--model models/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite \
--input images/grace_hopper.bmp \
--output ${HOME}/face_detection_results.jpg

Note: Currently this only supports SSD model with postprocessing operator.
Other models such as YOLO won't work.
"""

import argparse

from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils
from PIL import Image
from PIL import ImageDraw

import cv2
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True,
      help='Detection SSD model path (must have post-processing operator).')
    parser.add_argument('--label', help='Labels file path.')
    parser.add_argument('--keep_aspect_ratio', action='store_true',
      help=(
          'keep the image aspect ratio when down-sampling the image by adding '
          'black pixel padding (zeros) on bottom or right. '
          'By default the image is resized and reshaped without cropping. This '
          'option should be the same as what is applied on input images during '
          'model training. Otherwise the accuracy may be affected and the '
          'bounding box of detection result may be stretched.'))
    args = parser.parse_args()

    # Initialize engine.
    engine = DetectionEngine(args.model)
    labels = dataset_utils.read_label_file(args.label) if args.label else None

    res1 = (320,240)
    res4 = (480, 320)
    res2 = (640,480)
    res3 = (1280,720)
    res5 = (320,320)
    res6 = (480,480)
    res7 = (640,640)
    res = 2
    cap = cv2.VideoCapture(-1)
    cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
    while True:
        _, frame = cap.read()
        img = cv2.rotate(frame, cv2.ROTATE_180)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Open image.
        #img = Image.open(args.input).convert('RGB')
        
        imgPIL = Image.fromarray(imgRGB)
        #draw = ImageDraw.Draw(img)
        # Run inference.
        objs = engine.detect_with_image(imgPIL,
                                      threshold=0.05,
                                      keep_aspect_ratio=args.keep_aspect_ratio,
                                      relative_coord=False,
                                      top_k=10)
        
        # Print and draw detected objects.
        for obj in objs:
            print('-----------------------------------------')
            print('score =', obj.score)
            box = obj.bounding_box.flatten().tolist()
            print('box =', box)
            #draw.rectangle(box, outline='red')
            print(box[0], box[1])
            print(box[2], box[3])
            cv2.rectangle(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)

        if not objs:
            print('No objects detected.')
        
        #imgout = np.asarray(img)
        cv2.imshow("image", img)
        
        # Save image with bounding boxes.
        #if args.output:
        #img.save(args.output)
        
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()
    exit(0)

if __name__ == '__main__':
  main()
