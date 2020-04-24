import mrcnn.model
import mrcnn.config
import mrcnn.visualize
import numpy as np
import skimage.draw
import os
import sys
import datetime

sys.path.append("PurityClass")
from purity_index import PurityIndex

def apply_color_splash(image, mask, rois):
    """Apply color splash effect.
    image: RGB image [height, width, 3]
    mask: instance segmentation mask [height, width, instance count]

    Returns result image.
    """
    # Make a grayscale copy of the image. The grayscale copy still
    # has 3 RGB channels, though.
    gray = skimage.color.gray2rgb(skimage.color.rgb2gray(image)) * 255
    # Copy color pixels from the original color image where mask is set
    if mask.shape[-1] > 0:
        # We're treating all instances as one, so collapse the mask into one layer
        mask = (np.sum(mask, -1, keepdims=True) >= 1)
        splash = np.where(mask, image, gray).astype(np.uint8)
    else:
        splash = gray.astype(np.uint8)

    for i in range(0, rois.shape[0]):
        mrcnn.visualize.draw_box(splash, rois[i], (0, 192, 0))
    return splash

def calculate_tooth_dirtyness(image, mask):
    shape = image.shape;
    dirty_count = 0
    all_count = 0
    for row in range(shape[0]):
        for col in range(shape[1]):
            if mask[row, col]:
                r, g, b = image[row, col]
                if (3 < r < 186) and (17 < g < 75) and (37 < b < 160):
                    dirty_count += 1
                all_count += 1
    return float(dirty_count) / float(all_count)

def calculate_every_dirtyness(configuration, image, masks, rois):
    dirtyness_list = []
    for i in range(masks.shape[2]):
        tooth_image = image[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3]]
        tooth_mask = masks[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3], i]
        purity_class = PurityIndex(configuration)
        dirtyness = purity_class.get_index(tooth_image, tooth_mask);
        dirtyness_list.append(dirtyness)
    return dirtyness_list

def prepare_image(image):
    result = {}

    #Resize the image to speed things up
    shape = image.shape
    maxdim = max(shape)
    if maxdim > 1024:
        factor = 1024.0 / float(maxdim)
        new_shape = (min(1024, int(factor * float(shape[0]))),
                     min(1024, int(factor * float(shape[1]))),
                     shape[2])
        image = skimage.transform.resize(image, new_shape)
        image = (image * 255.0).astype(np.uint8)
    return image

def filter_outliers(dirtyness_list, n_removed):
    dirtyness_list.sort()

    if 2 * n_removed > len(dirtyness_list):
        return []

    return dirtyness_list[n_removed:len(dirtyness_list) - n_removed]

def calculate_overall_dirtyness(all_dirtyness_lists_2d, n_outliers):
    dirtyness_list_total = []

    for dirtyness_list in all_dirtyness_lists_2d:
        dirtyness_list_filtered = filter_outliers(dirtyness_list, n_outliers)
        dirtyness_list_total += dirtyness_list_filtered

    return np.mean(dirtyness_list_total)

def save_tooth_images(source_image, masks, rois):
    for i in range(masks.shape[2]):
        tooth_image = source_image[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3]]
        tooth_mask = masks[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3], i]

        saved_image = np.ndarray((tooth_image.shape[0], tooth_image.shape[1], 4),
                                 np.uint8)

        for row in range(tooth_image.shape[0]):
            for col in range(tooth_image.shape[1]):
                if tooth_mask[row, col]:
                    r, g, b = tooth_image[row, col]
                    a = 255
                else:
                    r, g, b, a = 0, 255, 0, 0
                saved_image[row, col] = r, g, b, a

        directory = "/images/output/inspection/"
        path = directory + str(i).zfill(2) + ".png"

        skimage.io.imsave(path, saved_image, compress_level=1)
        skimage.io.imsave(directory + "original.png", source_image, compress_level=1)
            

def process_images(model, images, configuration, inspect):
    all_dirtyness_lists_2d = []
    splashes = []

    for image in images:
        image = prepare_image(image)
        r = model.detect([image], verbose=0)[0]
        splash = apply_color_splash(image, r['masks'], r['rois'])
        dirtyness_list = calculate_every_dirtyness(configuration, image, r['masks'], r['rois'])
        splashes.append(splash)
        all_dirtyness_lists_2d.append(dirtyness_list)

        if inspect:
            save_tooth_images(image, r['masks'], r['rois']);

    dirtyness = calculate_overall_dirtyness(all_dirtyness_lists_2d, 0)
    return (splashes, dirtyness)

def load_images(paths_in, paths_out):
    images = []
    valid_paths_out = []
    for (path_in, path_out) in zip(paths_in, paths_out):
        try:
            image = skimage.io.imread(path_in)

            # Ignore alpha channel if it exists
            if len(image.shape) == 3 and image.shape[2] == 4:
                image = image[:,:,0:3]

            images.append(image)
            valid_paths_out.append(path_out)
        except:
            # Image decoding fail: print error
            print("Failed to read {}".format(path))
    return images, valid_paths_out

def process_file_list(model, image_paths_in, image_paths_out,
                      configuration, inspect):
    images, image_paths_out = load_images(image_paths_in, image_paths_out)
    if len(images) == 0:
        print("No images to process")
        return None

    splashes, dirtyness = process_images(model, images, configuration, inspect)
    for splash, image_path_out in zip(splashes, image_paths_out):
        skimage.io.imsave(image_path_out, splash, compress_level=1)
    return dirtyness

def tooth_model_init(weights_path):
    # Configurations
    class InferenceConfig(mrcnn.config.Config):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        NAME = "tooth"
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        NUM_CLASSES = 1 + 1  # Background + tooth
    config = InferenceConfig()

    model = mrcnn.model.MaskRCNN(mode="inference", config=config,
                                 model_dir=".")

    # Load weights
    print("Loading weights ", weights_path)
    model.load_weights(weights_path, by_name=True)
    return model
