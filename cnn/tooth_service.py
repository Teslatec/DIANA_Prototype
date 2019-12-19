import tooth
import socketserver
import json
import os
import sys

def process_request(model, workdir, json_object):
    if not isinstance(json_object, dict):
        print("JSON object should be a dict, got", type(json_object))
        return

    result = {}

    image_paths_in = []
    image_paths_out = []
    filenames_in = []
    filenames_out = []

    for image_desc in json_object["Images"]:
        if not isinstance(image_desc, dict):
            print("Image desc is not dict, but", type(image_desc))
            continue

        filename = image_desc.get("Name", None)
        if filename is None:
            print("Missing filename property")
            continue

        if "/" in filename or "\\" in filename or ".." in filename:
            print("Invalid filename \"{}\"".format(filename))
            continue

        image_path_in = os.path.join(workdir, filename)

        basename = os.path.splitext(filename)[0]
        filename_out = basename + "_out.png"
        image_path_out = os.path.join(workdir, filename_out)

        image_paths_in.append(image_path_in)
        image_paths_out.append(image_path_out)
        filenames_in.append(filename)
        filenames_out.append(filename_out)
        print("Image path: ", image_path_in)

    dirtyness = tooth.process_file_list(model, image_paths_in, image_paths_out)
    print("Dirtyness:", dirtyness)

    return {
        "dirtyness": dirtyness,
        "images": list(map(lambda finout: {"in": finout[0], "out": finout[1]},
                           zip(filenames_in, filenames_out)))
    }

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        model = self.server.model
        image_dir = self.server.image_dir
        json_object = None
        data = bytearray()

        while True:
            new_data = self.request.recv(4096)
            if len(new_data) == 0:
                print("Failed to parse JSON data")
                break

            data.extend(new_data)

            try:
                json_object = json.loads(data)
                break;
            except ValueError:
                continue

        result = process_request(model, image_dir, json_object)
        result_buf = json.dumps(result).encode()
        self.request.sendall(result_buf)

def run_server(model, port, image_dir):
    if not os.path.isdir(image_dir):
        print("\"{}\" is not a directory".format(image_dir))
        return

    server = socketserver.TCPServer(('', port), TCPHandler)
    server.model = model
    server.image_dir = image_dir

    print("Listening TCP port {}".format(port))
    server.serve_forever()

if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Detect teeth.')
    parser.add_argument('--weights', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--image', required=True,
                        metavar="path or URL to image",
                        help='Image to apply the color splash effect on')
    parser.add_argument('--output', required=False,
                        metavar="<output_dir>",
                        help='Output directory')
    args = parser.parse_args()

    model = tooth.tooth_model_init(args.weights)
    run_server(model, image_dir=args.image, port=8888)
