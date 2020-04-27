"""
Mask R-CNN
Train on the toy Tooth dataset and implement color splash effect.

Copyright (c) 2018 Matterport, Inc.
Licensed under the MIT License (see LICENSE for details)
Written by Waleed Abdulla

------------------------------------------------------------

Usage: import the module (see Jupyter notebooks for examples), or run from
       the command line as such:

    # Train a new model starting from pre-trained COCO weights
    python3 tooth.py train --dataset=/path/to/tooth/dataset --weights=coco

    # Resume training a model that you had trained earlier
    python3 tooth.py train --dataset=/path/to/tooth/dataset --weights=last

    # Train a new model starting from ImageNet weights
    python3 tooth.py train --dataset=/path/to/tooth/dataset --weights=imagenet

    # Apply color splash to an image
    python3 tooth.py splash --weights=/path/to/weights/file.h5 --image=<URL or path to file>

    # Apply color splash to video using the last weights you trained
    python3 tooth.py splash --weights=last --video=<URL or path to file>
"""

import os
import sys
import json
import datetime
import numpy as np
import skimage.draw
import re
import random

# Root directory of the project
ROOT_DIR = os.path.abspath("../../")

# Import Mask RCNN
sys.path.insert(0, ROOT_DIR)  # To find local version of the library
from mrcnn.config import Config
from mrcnn import model as modellib, utils
from mrcnn import visualize

from PIL import Image

# Path to trained weights file
COCO_WEIGHTS_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

# Directory to save logs and model checkpoints, if not provided
# through the command line argument --logs
DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")

############################################################
#  Configurations
############################################################


class ToothConfig(Config):
    """Configuration for training on the toy  dataset.
    Derives from the base Config class and overrides some values.
    """
    # Give the configuration a recognizable name
    NAME = "tooth"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    #NUM_CLASSES = 1 + 6  # Background + tooth, brace, wire, implant, root, front
    #NUM_CLASSES = 1 + 5  # Background + tooth, brace, wire, implant, root
    #NUM_CLASSES = 1 + 2  # Background + tooth, wire
    NUM_CLASSES = 1 + 1  # Background + tooth

    # Number of training steps per epoch
    STEPS_PER_EPOCH = 2000

    # Skip detections with < 90% confidence
    DETECTION_MIN_CONFIDENCE = 0.9

############################################################
#  Dataset
############################################################

class ToothDataset(utils.Dataset):
    def load_tooth(self, annotations):
        """Load a subset of the Tooth dataset.
        dataset_dir: Root directory of the dataset.
        subset: Subset to load: train or val
        """
        # Add classes. We have only one class to add.
        #self.add_class("tooth", 1, "tooth")
        #self.add_class("tooth", 2, "brace")
        #self.add_class("tooth", 3, "wire")
        #self.add_class("tooth", 4, "implant")
        #self.add_class("tooth", 5, "root")
        #self.add_class("tooth", 6, "front")

        #self.add_class("tooth", 1, "brace")
        #self.add_class("tooth", 2, "wire")

        self.add_class("tooth", 1, "tooth")

        # Add images
        for a in annotations:
            image_path = a['filename']
            if not os.path.isfile(image_path):
                continue

            #image = skimage.io.imread(image_path)
            #height, width = image.shape[:2]
            image = Image.open(image_path)
            width, height = image.size

            # Get the x, y coordinaets of points of the polygons that make up
            # the outline of each object instance. These are stores in the
            # shape_attributes (see json format above)

            polygons = a['regions']

            # Remove null regions (why are they here anyway???)
            polygons = [p for p in polygons if p]

            # Remove non-polygon regions
            polygons = [p for p in polygons if p['shape_attributes']['name'] == "polygon"]

            # Remove polygons with no vertices
            polygons = [p for p in polygons if len(p['shape_attributes']['all_points_x']) != 0]
            polygons = [p for p in polygons if len(p['shape_attributes']['all_points_y']) != 0]

            # Clip polygons that cross the image border
            for p in polygons:
                p['shape_attributes']['all_points_x'][:] = \
                        [min(width - 1, max(0, x)) for x in p['shape_attributes']['all_points_x']]
                p['shape_attributes']['all_points_y'][:] = \
                        [min(height - 1, max(0, y)) for y in p['shape_attributes']['all_points_y']]

            # load_mask() needs the image size to convert polygons to masks.
            # Unfortunately, VIA doesn't include it in JSON, so we must read
            # the image. This is only managable since the dataset is tiny.
            
            print("Loaded file", image_path, "shape", (height, width));

            self.add_image(
                "tooth",
                image_id=a['filename'],  # use file name as a unique image id
                path=image_path,
                width=width, height=height,
                polygons=polygons)

    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        # If not a tooth dataset image, delegate to parent class.
        image_info = self.image_info[image_id]
        if image_info["source"] != "tooth":
            return super(self.__class__, self).load_mask(image_id)

        # Convert polygons to a bitmap mask of shape
        # [height, width, instance_count]
        info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)
        types = np.zeros(len(info["polygons"]), np.int32)

        for i, p in enumerate(info["polygons"]):
            # Get indexes of pixels inside the polygon and set them to 1
            s = p['shape_attributes']
            rr, cc = skimage.draw.polygon(s['all_points_y'], s['all_points_x'])
            mask[rr, cc, i] = 1

            object_class = 0
            object_class_str = None
            if 'type' in p['region_attributes']:
                object_class_str = p['region_attributes']['type']
            elif 'Type' in p['region_attributes']:
                object_class_str = p['region_attributes']['Type']

            #class_map = {
            #    "tooth": 0,
            #    "brecket": 1,
            #    "wire": 2,
            #    "implant": 0,
            #    "tooth root": 0,
            #    "front": 0
            #}

            class_map = {
                "tooth": 1,
                "front": 1
            }

            if object_class_str is not None:
                object_class_str = object_class_str.strip()
                if object_class_str in class_map:
                    object_class = class_map[object_class_str]
            else:
                object_class = 1

            types[i] = object_class

        # Handle occlusions
        #occlusion = np.logical_not(mask[:, :, -1]).astype(np.uint8)
        #for i in range(count - 2, -1, -1):
        #    mask[:, :, i] = mask[:, :, i] * occlusion
        #    occlusion = np.logical_and(
        #            occlusion, np.logical_not(mask[:, :, i]))

        # Return mask, and array of class IDs of each instance. Since we have
        # one class ID only, we return an array of 1s
        return mask.astype(np.bool), types

    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "tooth":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)

def load_annotations(dataset_dir):
    # Load annotations
    # VGG Image Annotator (up to version 1.6) saves each image in the form:
    # { 'filename': '28503151_5b5b7ec140_b.jpg',
    #   'regions': {
    #       '0': {
    #           'region_attributes': {},
    #           'shape_attributes': {
    #               'all_points_x': [...],
    #               'all_points_y': [...],
    #               'name': 'polygon'}},
    #       ... more regions ...
    #   },
    #   'size': 100202
    # }

    # We mostly care about the x and y coordinates of each region
    # Note: In VIA 2.0, regions was changed from a dict to a list.

    filename_regex = re.compile(r'.*.json')

    annotations = []
    for root, dirs, files in os.walk(dataset_dir):
        found = False
        json_filename = ""

        for file in files:
            if filename_regex.match(file):
                json_filename = file
                found = True
                break
        if found:
            json_data = {}
            json_path = os.path.join(root, json_filename)
            try:
                json_data = json.load(open(json_path))
            except Exception as e:
                print("Failed to load \"{}\", exception {}".format(json_path, e))
                continue

            if not '_via_img_metadata' in json_data:
                continue

            print("Found file " + file)

            json_data = list(json_data['_via_img_metadata'].values()) 
            # The VIA tool saves images in the JSON even if they don't have any
            # annotations. Skip unannotated images.
            json_data = [a for a in json_data if a['regions']]
            for d in json_data:
                d['filename'] = os.path.join(root, d['filename'])
                annotations.append(d)
            continue
    return annotations

def train(model):
    annotations = load_annotations(args.dataset)

    # Randomy assign 70% of annotations as train and remaining 30% as validataion
    # Also use fixed seed to make reproducible datasets
    random.Random(5757).shuffle(annotations)
    train_len = len(annotations) * 7 // 10 

    train_annotations = annotations[:train_len]
    val_annotations = annotations[train_len:]

    print("Train annotations:", len(train_annotations))
    print("Validation annotations:", len(val_annotations))

    """Train the model."""
    # Training dataset.
    dataset_train = ToothDataset()
    dataset_train.load_tooth(train_annotations)
    dataset_train.prepare()

    # Validation dataset
    dataset_val = ToothDataset()
    dataset_val.load_tooth(val_annotations)
    dataset_val.prepare()

    # *** This training schedule is an example. Update to your needs ***
    # Since we're using a very small dataset, and starting from
    # COCO trained weights, we don't need to train too long. Also,
    # no need to train all layers, just the heads should do it.
    print("Training network heads")
    model.train(dataset_train, dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=30,
                layers='heads')


def color_splash(image, mask, rois, classes):
    """Apply color splash effect.
    image: RGB image [height, width, 3]
    mask: instance segmentation mask [height, width, instance count]

    Returns result image.
    """
    # Make a grayscale copy of the image. The grayscale copy still
    # has 3 RGB channels, though.
    gray = skimage.color.gray2rgb(skimage.color.rgb2gray(image)) * 255
    # Copy color pixels from the original color image where mask is set
    #if mask.shape[-1] > 0:
    #    # We're treating all instances as one, so collapse the mask into one layer
    #    mask = (np.sum(mask, -1, keepdims=True) >= 1)
    #    splash = np.where(mask, image, gray).astype(np.uint8)
    #else:
    #    splash = gray.astype(np.uint8)

    splash = gray.astype(np.uint8)

    print("Clases:", classes)

    for i in range(0, rois.shape[0]):
        color = (0, 0, 0)
        if classes[i] == 1:
            color = (0, 192, 0)
        elif classes[i] == 2:
            color = (255, 0, 0)
        elif classes[i] == 3:
            color = (0, 0, 255)
        elif classes[i] == 4:
            color = (255, 255, 255)
        elif classes[i] == 5:
            color = (0, 0, 0)
        else:
            continue
        visualize.draw_box(splash, rois[i], color)
    return splash

def apply_image_splash(model, image_path, output_dir):
    # Run model detection and generate the color splash effect
    print("Running on {}".format(image_path))
    # Read image
    try:
        image = skimage.io.imread(image_path)
    except ValueError:
        # Not an image - do nothing
        return
    except:
        # Image decoding fail: print error
        print("Failed to read {}".format(image_path))
        return
    
    #Resize the image to speed things up
    shape = image.shape
    print("Original shape {}, original type {}".format(str(shape), str(image.dtype)))
    maxdim = max(shape)
    if maxdim > 1024:
        factor = 1024.0 / float(maxdim)
        new_shape = (min(1024, int(factor * float(shape[0]))),
                     min(1024, int(factor * float(shape[1]))),
                     shape[2])
        image = skimage.transform.resize(image, new_shape)
        image = (image * 255.0).astype(np.uint8)
        print("New shape {}, new type {}".format(str(new_shape), str(image.dtype)))
        #test_fname = "test_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
        #skimage.io.imsave(test_fname, image)

    # Detect objects
    r = model.detect([image], verbose=1)[0]
    
    # Color splash
    splash = color_splash(image, r['masks'], r['rois'], r['class_ids'])
    # Save output
    file_name = "splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
    out_path = os.path.join(output_dir, file_name)
    skimage.io.imsave(out_path, splash)
    print("Saved to ", out_path)

def detect_and_color_splash(model, image_path=None,
                            output_dir=".", video_path=None):
    assert image_path or video_path

    # Image or video?
    if image_path:
        if not os.path.isdir(image_path):
            apply_image_splash(model, image_path, output_dir)
        else:
            for file in os.listdir(image_path):
                apply_image_splash(model, os.path.join(image_path, file),
                                   output_dir)

    elif video_path:
        import cv2
        # Video capture
        vcapture = cv2.VideoCapture(video_path)
        width = int(vcapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vcapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vcapture.get(cv2.CAP_PROP_FPS)

        # Define codec and create video writer
        file_name = "splash_{:%Y%m%dT%H%M%S}.avi".format(datetime.datetime.now())
        vwriter = cv2.VideoWriter(file_name,
                                  cv2.VideoWriter_fourcc(*'MJPG'),
                                  fps, (width, height))

        count = 0
        success = True
        while success:
            print("frame: ", count)
            # Read next image
            success, image = vcapture.read()
            if success:
                # OpenCV returns images as BGR, convert to RGB
                image = image[..., ::-1]
                # Detect objects
                r = model.detect([image], verbose=0)[0]
                # Color splash
                splash = color_splash(image, r['masks'])
                # RGB -> BGR to save image to video
                splash = splash[..., ::-1]
                # Add image to video writer
                vwriter.write(splash)
                count += 1
        vwriter.release()
        print("Saved to ", file_name)

############################################################
#  Training
############################################################

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Train Mask R-CNN to detect teeth.')
    parser.add_argument("command",
                        metavar="<command>",
                        help="'train' or 'splash'")
    parser.add_argument('--dataset', required=False,
                        metavar="/path/to/tooth/dataset/",
                        help='Directory of the Tooth dataset')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--logs', required=False,
                        default=DEFAULT_LOGS_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    parser.add_argument('--image', required=False,
                        metavar="path or URL to image",
                        help='Image to apply the color splash effect on')
    parser.add_argument('--video', required=False,
                        metavar="path or URL to video",
                        help='Video to apply the color splash effect on')
    parser.add_argument('--output', required=False,
                        metavar="<output_dir>",
                        help='Output directory')
    args = parser.parse_args()

    # Validate arguments
    if args.command == "train":
        assert args.dataset, "Argument --dataset is required for training"
    elif args.command == "splash":
        assert args.image or args.video,\
               "Provide --image or --video to apply color splash"

    print("Weights: ", args.weights)
    print("Dataset: ", args.dataset)
    print("Logs: ", args.logs)

    # Configurations
    if args.command == "train":
        config = ToothConfig()
    else:
        class InferenceConfig(ToothConfig):
            # Set batch size to 1 since we'll be running inference on
            # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
            GPU_COUNT = 1
            IMAGES_PER_GPU = 1
        config = InferenceConfig()
    config.display()

    # Create model
    if args.command == "train":
        model = modellib.MaskRCNN(mode="training", config=config,
                                  model_dir=args.logs)
    else:
        model = modellib.MaskRCNN(mode="inference", config=config,
                                  model_dir=args.logs)

    # Select weights file to load
    if args.weights.lower() == "coco":
        weights_path = COCO_WEIGHTS_PATH
        # Download weights file
        if not os.path.exists(weights_path):
            utils.download_trained_weights(weights_path)
    elif args.weights.lower() == "last":
        # Find last trained weights
        weights_path = model.find_last()
    elif args.weights.lower() == "imagenet":
        # Start from ImageNet trained weights
        weights_path = model.get_imagenet_weights()
    else:
        weights_path = args.weights

    # Load weights
    print("Loading weights ", weights_path)
    if args.weights.lower() == "coco":
        # Exclude the last layers because they require a matching
        # number of classes
        model.load_weights(weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])
    else:
        model.load_weights(weights_path, by_name=True)

    # Train or evaluate
    if args.command == "train":
        train(model)
    elif args.command == "splash":
        detect_and_color_splash(model, image_path=args.image,
                                video_path=args.video,
                                output_dir=args.output)
    else:
        print("'{}' is not recognized. "
              "Use 'train' or 'splash'".format(args.command))
