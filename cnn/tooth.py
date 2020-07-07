import mrcnn.model
import mrcnn.config
import mrcnn.visualize

from purity_index import PurityIndex

import numpy as np
import skimage.draw
import os
import sys
import datetime

def apply_color_splash(image, mask, rois):
    result = np.copy(image)
    for i in range(0, rois.shape[0]):
        mrcnn.visualize.draw_box(result, rois[i], (0, 192, 0))
    return result

def calculate_every_dirtyness(purity_class, image, masks, rois):
    results = []
    for i in range(masks.shape[2]):
        tooth_image = image[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3]]
        tooth_mask = masks[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3], i]
        result = purity_class.get_index(tooth_image[:,:,::-1], tooth_mask);
        result['image'] = result['image'][:,:,::-1]
        results.append(result)
    return results

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


def cut_braces_from_teeth(tooth_masks, brace_masks):
    result = np.copy(tooth_masks)

    total_cut_area = 0

    for t in range(tooth_masks.shape[-1]):
        area_before = np.sum(results[:,:,t])
        for b in range(brace_masks.shape[-1]):
            result[:,:,t] = np.logical_and(result[:,:,t],
                                           np.logical_not(brace_masks[:,:,b]))
        area_after = np.sum(results[:,:,t])
        total_cut_area += (area_before - area_after)
    return result

def sum_purity_results(purity_results):
    return {
        'total': np.sum(r['total'] for r in purity_results),
        's': np.sum(r['s'] for r in purity_results),
        'm': np.sum(r['m'] for r in purity_results),
        'h': np.sum(r['h'] for r in purity_results),
    }

def index_total(purity_index):
    return purity_index['day']  + purity_index['week'] + purity_index['month']

def process_images(model, images, purity_class, inspect):
    splashes = []
    results = []

    for image in images:
        image = prepare_image(image)
        tooth_result = model['tooth'].detect([image], verbose=0)[0]
        brace_result = model['brace'].detect([image], verbose=0)[0]

        if brace_result['masks'].shape[-1] >= 5:
            tooth_mask_cut, cut_area = cut_braces_from_teeth(tooth_result['masks'], brace_result['masks'])
        else:
            tooth_mask_cut, cut_area = tooth_result['masks'], 0

        per_tooth_results = calculate_every_dirtyness(purity_class, image,
                                                      tooth_mask_cut, tooth_result['rois'])

        current_image_result = sum_purity_results(per_tooth_results)
        current_image_result['total'] += cut_area
        results.append(current_image_result)

        splash = apply_color_splash(image, tooth_result['masks'],
                                    tooth_result['rois'])
        splashes.append(splash)
        if inspect:
            save_tooth_images(image, tooth_mask_cut, tooth_result['rois']);
            #for i, t in enumerate(r['image'] for r in results):
            #    directory = "/images/output/inspection/"
            #    path = directory + str(i).zfill(2) + "t" + ".png"
            #    skimage.io.imsave(path, t, compress_level=1)

    purity_index = purity_class.get_purity_index(sum_purity_results(results))
    return (splashes, purity_index)

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
            print("Failed to read {}".format(path_in))
    return images, valid_paths_out

def process_file_list(model, image_paths_in, image_paths_out,
                      configuration, inspect=False):
    images, image_paths_out = load_images(image_paths_in, image_paths_out)
    if len(images) == 0:
        print("No images to process")
        return None

    purity_class = PurityIndex(configuration)

    splashes, dirtyness = process_images(model, images, purity_class, inspect)
    for splash, image_path_out in zip(splashes, image_paths_out):
        skimage.io.imsave(image_path_out, splash, compress_level=1)
    return dirtyness

def tooth_model_init(tooth_weights_path, brace_weights_path):
    # Configurations
    class ToothConfig(mrcnn.config.Config):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        NAME = "tooth"
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        NUM_CLASSES = 1 + 1  # Background + tooth
    tooth_config = ToothConfig()

    class BraceConfig(mrcnn.config.Config):
        NAME = "tooth"
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        NUM_CLASSES = 1 + 1 # Background + brace
    brace_config = BraceConfig()

    tooth_model = mrcnn.model.MaskRCNN(mode="inference", config=tooth_config,
                                       model_dir=".")
    brace_model = mrcnn.model.MaskRCNN(mode="inference", config=brace_config,
                                       model_dir=".")

    # Load weights
    print("Loading weights ", tooth_weights_path, brace_weights_path)
    tooth_model.load_weights(tooth_weights_path, by_name=True)
    brace_model.load_weights(brace_weights_path, by_name=True)
    
    return {'tooth': tooth_model, 'brace': brace_model}
