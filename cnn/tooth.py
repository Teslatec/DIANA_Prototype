import mrcnn.model
import mrcnn.config
import mrcnn.visualize

from purity_index import PurityIndex

import numpy as np
import skimage.draw
import os
import sys
import datetime

# Used for white balancing
# and making test collages
import cv2

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

def prepare_image(image, white_balancer):
    result = {}

    #Resize the image to speed things up
    shape = image.shape
    maxdim = max(shape[0:2])
    if maxdim > 1024:
        factor = 1024.0 / float(maxdim)
        new_shape = (min(1024, int(factor * float(shape[0]))),
                     min(1024, int(factor * float(shape[1]))),
                     shape[2])
        image = skimage.transform.resize(image, new_shape)
        image = (image * 255.0).astype(np.uint8)

    if white_balancer is not None:
        cv2.cvtColor(image, cv2.COLOR_RGB2BGR, image)
        white_balancer.balanceWhite(image, image)
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)

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

def remove_false_braces(tooth_results, brace_results):
    if tooth_results['masks'].shape[2] == 0:
        return brace_results

    tooth_areas = np.sum(tooth_results['masks'], axis=(0,1))
    largest_tooth_area = np.max(tooth_areas)

    true_braces_mask = np.sum(brace_results['masks'], axis=(0,1)) < largest_tooth_area

    result = {
        'masks': brace_results['masks'][:,:,true_braces_mask],
        'rois': brace_results['rois'][true_braces_mask],
        # 'class_ids': ...
        # 'scores': ...
    }

    return result

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

def sum_purity_results(purity_results):
    return {
        'total': np.sum(r['total'] for r in purity_results),
        's': np.sum(r['s'] for r in purity_results),
        'm': np.sum(r['m'] for r in purity_results),
        'h': np.sum(r['h'] for r in purity_results),
    }

def index_total(purity_index):
    return purity_index['day']  + purity_index['week'] + purity_index['month']

def draw_purity_index(image, purity_index):
    index_str = "M: %3.0f%% W: %3.0f%% D: %3.0f%% %s %s" % \
                (purity_index['month'] * 100, purity_index['week'] * 100,
                    purity_index['day'] * 100, purity_index['color'],
                    str(purity_index['matrix']))
    cv2.putText(image, index_str, (0, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

def make_test_collage_image(image, rois, plaque_images, dirtyness, purity_index):
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

def make_test_collage(purity_class, image, tooth_result, brace_result, tooth_mask_cut,
                      with_braces_result, with_braces_plaque_images):
    with_braces_index = purity_class.get_purity_index(with_braces_result)
    with_braces_image = np.copy(image)
    draw_braces(with_braces_image, brace_result['masks'])
    with_braces_image = make_test_collage_image(with_braces_image, tooth_result['rois'],
                                                with_braces_plaque_images,
                                                index_total(with_braces_index),
                                                with_braces_index)

    no_braces_results = calculate_every_dirtyness(purity_class, image,
                                                  tooth_result['masks'], tooth_result['rois'])
    no_braces_index = purity_class.get_purity_index(sum_purity_results(no_braces_results))
    no_braces_image = make_test_collage_image(image, tooth_result['rois'],
                                              [r['image'] for r in no_braces_results],
                                              index_total(no_braces_index),
                                              no_braces_index)

    old_algorithm_dirtyness, old_algorithm_plaque = calculate_jaw_dirtyness_old(image, tooth_result['masks'],
                                                                                tooth_result['rois'])
    old_algorithm_image = make_test_collage_image(image, tooth_result['rois'],
                                                  old_algorithm_plaque, old_algorithm_dirtyness,
                                                  None)
    return combine_pictures(image, old_algorithm_image, no_braces_image, with_braces_image)

def is_horizontally_oriented(tooth_rois):
    num_excluded = 2

    if tooth_rois.shape[0] >= 2*num_excluded:
        # Filter teeth furthest from their center

        s = np.sum(tooth_rois, axis=0)
        count = tooth_rois.shape[0]
        center = ((s[2] + s[0]) // (2 * count), (s[3] + s[1]) // (2 * count))
        diffs = tooth_rois.reshape((tooth_rois.shape[0],2,2)) - center
        diffs_sums = np.sum(diffs, axis=1)

        # Manhattan metric
        distances = np.sum(np.absolute(diffs_sums), axis=1)

        indexes = np.argsort(distances)
        indexes = indexes[num_excluded//2:-((num_excluded+1)//2)]

        rois_filtered = tooth_rois[indexes]
    else:
        rois_filtered = tooth_rois

    rois_filtered = rois_filtered.reshape(2*rois_filtered.shape[0],2)
    y1, x1 = np.min(rois_filtered, axis=0)
    y2, x2 = np.max(rois_filtered, axis=0)
    h = y2 - y1
    w = x2 - x1
    return w >= h

def split_detection_result(result, class_id):
    print(result['class_ids'])
    indexes = [i for i, c in enumerate(result['class_ids']) if c == class_id]
    return {
        'rois': result['rois'][indexes],
        'masks': result['masks'][:,:,indexes]
    }

def detection_generator(model, images):
    tooth_model = model['tooth']
    batch_size = tooth_model.config.GPU_COUNT * tooth_model.config.IMAGES_PER_GPU

    num_batches = (len(images) + (batch_size - 1)) // batch_size

    for batch in range(0, num_batches):
        prepared_images = []
        for image in images[batch_size * batch : batch_size * (batch + 1)]:
            prepared_images.append(prepare_image(image, model['white_balancer']))

        actual_batch_size = len(prepared_images)

        # Fill the batch with the same image
        for i in range(0, batch_size - actual_batch_size):
            prepared_images.append(prepared_images[0])

        results = model['tooth'].detect(prepared_images, verbose=0)
        for prepared_image, result in zip(prepared_images[0:actual_batch_size], results[0: actual_batch_size]):
            yield prepared_image, result

def process_images(model, images, purity_class, inspect, make_test_image = False):
    splashes = []
    results = []

    for image, result in detection_generator(model, images):
        tooth_result = split_detection_result(result, 1)
        brace_result = split_detection_result(result, 2)

        if tooth_result['masks'].shape[-1] <= 2:
            splashes.append(None)
            continue

        horizontal = is_horizontally_oriented(tooth_result['rois'])

        brace_result = remove_false_braces(tooth_result, brace_result)

        if brace_result['masks'].shape[-1] >= 5:
            tooth_mask_cut, cut_area = cut_braces_from_teeth(tooth_result['masks'], brace_result['masks'])
        else:
            tooth_mask_cut, cut_area = tooth_result['masks'], 0

        per_tooth_results = calculate_every_dirtyness(purity_class, image,
                                                      tooth_mask_cut, tooth_result['rois'])

        current_image_result = sum_purity_results(per_tooth_results)
        current_image_result['total'] += cut_area
        results.append(current_image_result)

        if not make_test_image:
            splash = apply_color_splash(image, tooth_result['masks'], tooth_result['rois'])
            if not horizontal:
                splash = np.rot90(splash, axes=(0,1))
        else:
            splash = make_test_collage(purity_class, image, tooth_result, brace_result,
                                       tooth_mask_cut, current_image_result,
                                       [r['image'] for r in per_tooth_results])

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
    image_paths_out_final = []

    splashes, dirtyness = process_images(model, images, purity_class, inspect, inspect)
    for splash, image_path_out in zip(splashes, image_paths_out):
        if splash is None:
            continue
        skimage.io.imsave(image_path_out, splash, compress_level=1)
        image_paths_out_final.append(image_path_out)
    return dirtyness, image_paths_out_final

def tooth_model_init(tooth_weights_path, white_balance_enabled=False):
    # Configurations
    class ToothConfig(mrcnn.config.Config):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        NAME = "tooth"
        GPU_COUNT = 1
        IMAGES_PER_GPU = 6
        NUM_CLASSES = 1 + 2  # Background + tooth + brace
    tooth_config = ToothConfig()

    tooth_model = mrcnn.model.MaskRCNN(mode="inference", config=tooth_config,
                                       model_dir=".")

    # Load weights
    print("Loading weights ", tooth_weights_path)
    tooth_model.load_weights(tooth_weights_path, by_name=True)

    if white_balance_enabled:
        white_balancer = cv2.xphoto.createGrayworldWB()
        white_balancer.setSaturationThreshold(0.99)
    else:
        white_balancer = None

    return {'tooth': tooth_model,
            'white_balancer': white_balancer}
