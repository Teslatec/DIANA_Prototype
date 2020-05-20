import tooth_test
import os
import configparser

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Detect teeth.')
    parser.add_argument('--tooth', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to tooth weights .h5 file or 'coco'")
    parser.add_argument('--brace', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to brace weights .h5 file or 'coco'")
    parser.add_argument("--purity", required=True,
                        metavar="/path/to/purity.ini",
                        help="Path to PurityClass settings")
    parser.add_argument('--image', required=True,
                        metavar="path or URL to image",
                        help='Image to apply the color splash effect on')
    parser.add_argument('--output', required=False,
                        metavar="<output_dir>",
                        help='Output directory')
    args = parser.parse_args()

    model = tooth_test.tooth_model_init(args.tooth, args.brace)

    paths_in_unfiltered = []
    paths_in = []
    paths_out = []

    if not os.path.isdir(args.image):
        #apply_image_splash(model, image_path, output_dir)
        paths_in_unfiltered.append(args.image)
    else:
        for file in os.listdir(args.image):
            paths_in_unfiltered.append(os.path.join(args.image, file))

    out_dir = args.output or "."

    print("Out dir == " + str(out_dir))
    
    for path_in in paths_in_unfiltered:
        basename, extension = os.path.splitext(os.path.split(path_in)[-1])
        extension = extension.casefold()
        if extension != ".jpg" and \
           extension != ".png" and \
           extension != ".jpeg":
            continue

        filename_out = basename + "_out.png"
        path_out = os.path.join(out_dir, filename_out)
        paths_in.append(path_in)
        paths_out.append(path_out)

    print("Input images: " + str(paths_in))
    print("Output images: " + str(paths_out))

    config = configparser.ConfigParser()
    config.read(args.purity)

    for path_in, path_out in zip(paths_in, paths_out):
        dirtyness = tooth_test.process_file_list(model, [path_in], [path_out],
                                                 config, inspect = True)
        print(path_in, dirtyness)
