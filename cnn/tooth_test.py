import mrcnn.model
import mrcnn.config
import mrcnn.visualize

from purity_index import PurityIndex

import numpy as np
import skimage.draw
import os
import sys
import datetime

#TEST 
import cv2

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

def calculate_tooth_dirtyness_old(image, mask):
    shape = image.shape;
    dirty_count = 0
    all_count = 0
    splash = np.ndarray(image.shape, image.dtype)
    for row in range(shape[0]):
        for col in range(shape[1]):
            if mask[row, col]:
                r, g, b = image[row, col]
                if (3 < r < 186) and (17 < g < 75) and (37 < b < 160):
                    dirty_count += 1
                    splash[row, col] = (255, 102, 217)
                else:
                    splash[row, col] = (r, g, b)
                all_count += 1
            else:
                splash[row, col] = (255, 255, 255)
                
    return float(dirty_count) / float(all_count), splash

def calculate_jaw_dirtyness_old(image, masks, rois):
    results = []
    splashes = []
    for i in range(masks.shape[2]):
        tooth_image = image[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3]]
        tooth_mask = masks[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3], i]
        dirtyness, splash = calculate_tooth_dirtyness_old(tooth_image, tooth_mask)
        results.append(dirtyness)
        splashes.append(splash)
    return np.average(results), splashes

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
        area_before = np.sum(result[:,:,t])
        for b in range(brace_masks.shape[-1]):
            result[:,:,t] = np.logical_and(result[:,:,t],
                                           np.logical_not(brace_masks[:,:,b]))
        area_after = np.sum(result[:,:,t])
        total_cut_area += (area_before - area_after)
    return result, total_cut_area

def draw_purity_index(image, purity_index):
    index_str = "M: %3.0f%% W: %3.0f%% D: %3.0f%% %s %s" % \
                (purity_index['month'] * 100, purity_index['week'] * 100,
                    purity_index['day'] * 100, purity_index['color'],
                    str(purity_index['matrix']))
    cv2.putText(image, index_str, (0, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

def apply_color_splash2(image, rois, plaque_images, dirtyness, purity_index):
    result = np.copy(image)

    for i in range(rois.shape[0]):
        tooth = result[rois[i][0]:rois[i][2], rois[i][1]:rois[i][3]]

        plaque = plaque_images[i]

        mask = np.logical_or(np.all(plaque == (255, 255, 255), axis=2),
                             np.all(plaque == (255, 229, 204), axis=2))
        mask = mask.reshape(mask.shape + (1,));
        tooth[:] = np.where(mask, tooth, plaque)
    cv2.putText(result, "%.2f%%" % (dirtyness * 100), (0, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    if purity_index is not None:
        draw_purity_index(result, purity_index)

    return result

def combine_pictures(image1, image2, image3, image4):
    result = np.ndarray((image1.shape[0] * 2, image1.shape[1] * 2, image1.shape[2]),
                        image1.dtype)
    result[:image1.shape[0],:image1.shape[1],:] = image1
    result[:image1.shape[0],image1.shape[1]:,:] = image2
    result[image1.shape[0]:,:image1.shape[1],:] = image3
    result[image1.shape[0]:,image1.shape[1]:,:] = image4
    return result

def draw_braces(image, masks):
    image[np.any(masks, axis=2)] = (153, 255, 153)

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
    all_dirtyness_lists_2d = []
    splashes = []

    for image in images:
        image = prepare_image(image)
        tooth_result = model['tooth'].detect([image], verbose=0)[0]
        brace_result = model['brace'].detect([image], verbose=0)[0]

        if brace_result['masks'].shape[-1] >= 5:
            tooth_mask_cut, cut_area = cut_braces_from_teeth(tooth_result['masks'], brace_result['masks'])
            print("Cut area", cut_area)
        else:
            tooth_mask_cut, cut_area = tooth_result['masks'], 0
            print("Less than 5 braces detected")

        results_braces_applied = calculate_every_dirtyness(purity_class, image,
                                                           tooth_mask_cut, tooth_result['rois'])
        results_braces_sum = sum_purity_results(results_braces_applied)
        results_braces_sum['total'] += cut_area
        dirtyness_list_braces_applied = [((r['s'] + r['m'] + r['h'])) / r['total']
                                         for r in results_braces_applied
                                         if r['total'] != 0]
        dirtyness_braces_applied = np.average(dirtyness_list_braces_applied)
        index_braces_applied = purity_class.get_purity_index(results_braces_sum)
        splash_braces_applied = apply_color_splash2(image, tooth_result['rois'],
                                                    [r['image'] for r in results_braces_applied],
                                                    index_total(index_braces_applied),
                                                    index_braces_applied)
        draw_braces(splash_braces_applied, brace_result['masks'])

        results_braces_not_applied = calculate_every_dirtyness(purity_class, image,
                                                               tooth_result['masks'], tooth_result['rois'])
        dirtyness_list_braces_not_applied = [((r['s'] + r['m'] + r['h'])) / r['total']
                                            for r in results_braces_not_applied
                                            if r['total'] != 0]
        dirtyness_braces_not_applied = np.average(dirtyness_list_braces_not_applied)
        index_braces_not_applied = purity_class.get_purity_index(sum_purity_results(results_braces_not_applied))
        splash_braces_not_applied = apply_color_splash2(image, tooth_result['rois'],
                                                        [r['image'] for r in results_braces_not_applied],
                                                        index_total(index_braces_not_applied),
                                                        index_braces_not_applied)

        dirtyness_old, splashes_old = calculate_jaw_dirtyness_old(image, tooth_result['masks'], tooth_result['rois'])
        splash_old = apply_color_splash2(image, tooth_result['rois'],
                                         splashes_old, dirtyness_old,
                                         None)

        splashes.append(combine_pictures(image, splash_old,
                                         splash_braces_not_applied,
                                         splash_braces_applied))
        all_dirtyness_lists_2d.append(dirtyness_list_braces_applied)


        #if inspect:
            #save_tooth_images(image, tooth_mask_cut, tooth_result['rois']);

            #for i, t in enumerate(r['image'] for r in results):
            #    directory = "/images/output/inspection/"
            #    path = directory + str(i).zfill(2) + "t" + ".png"
            #    skimage.io.imsave(path, t, compress_level=1)

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
