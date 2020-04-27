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

def color_splash(image, masks, rois, classes):
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
        image_segment = image[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3]]       
        mask_segment = masks[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3], i]     
        mask_segment = mask_segment.reshape(mask_segment.shape + (1,))
        splash_segment = splash[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3]];
        splash_segment[:] = np.where(mask_segment, image_segment, splash_segment)

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
    parser.add_argument('--dataset', required=False,
                        metavar="/path/to/tooth/dataset/",
                        help='Directory of the Tooth dataset')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--image', required=False,
                        metavar="path or URL to image",
                        help='Image to apply the color splash effect on')
    parser.add_argument('--video', required=False,
                        metavar="path or URL to video",
                        help='Video to apply the color splash effect on')
    parser.add_argument('--output', required=False,
                        default=".",
                        metavar="<output_dir>",
                        help='Output directory')
    args = parser.parse_args()

    print("Weights: ", args.weights)
    print("Dataset: ", args.dataset)

    # Configurations
    config = ToothConfig()
    config.display()

    # Create model
    model = modellib.MaskRCNN(mode="inference", config=config,
                              model_dir=".")

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
    detect_and_color_splash(model, image_path=args.image,
                            video_path=args.video,
                            output_dir=args.output)
