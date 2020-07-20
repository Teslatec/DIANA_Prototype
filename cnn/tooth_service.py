import tooth
import json
import os
import sys
import configparser
import pika
import functools

OUTPUT_DIR = "images_output"

def process_request(model, purity_config, workdir, json_object):
    if not isinstance(json_object, dict):
        print("JSON object should be a dict, got", type(json_object))
        sys.stdout.flush()
        return

    result = {}

    image_paths_in = []
    image_paths_out = []
    filenames_in = []
    filenames_out = []

    for filename in json_object["images"]:
        if ".." in filename:
            print("Invalid filename \"{}\"".format(filename))
            continue

        image_path_in = os.path.join(workdir, filename)
        basename = os.path.basename(filename)
        filename_out = os.path.splitext(basename)[0] + ".png"
        image_path_out = os.path.join(workdir, OUTPUT_DIR, filename_out)

        image_paths_in.append(image_path_in)
        image_paths_out.append(image_path_out)
        filenames_in.append(filename)
        filenames_out.append(os.path.join(OUTPUT_DIR, filename_out))

    purity_index, filenames_out = tooth.process_file_list(model, image_paths_in, image_paths_out,
                                                          purity_config)
    result =  {
        "id": json_object["id"],
        "image": filenames_out,
        "index": purity_index,
    }
    print("Finished processing. Results:", result)
    return result

def mq_callback(model, purity_config, image_dir,
                channel, method, properties, body):
    message = json.loads(body)
    
    print("New request:", message)  
    
    answer = process_request(model, purity_config, image_dir, message)
    
    queue = 'answer-image'
    channel.queue_declare(queue=queue)      
    channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(answer))
    
    channel.basic_ack(delivery_tag=method.delivery_tag)

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
    parser.add_argument('--rabbit', required=True,
                        metavar="RabbiMQ URL for getting images",)
    args = parser.parse_args()

    model = tooth.tooth_model_init(args.tooth, args.brace)

    purity_config = configparser.ConfigParser()
    purity_config.read(args.purity)

    os.makedirs(os.path.join(args.image, OUTPUT_DIR), exist_ok=True)
    
    params = pika.URLParameters(args.rabbit)                                 
    connection = pika.BlockingConnection(params)                                
    channel = connection.channel()
    queue="image-test"
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    callback = functools.partial(mq_callback, model,
                                 purity_config, args.image)
    channel.basic_consume(on_message_callback=callback, queue=queue)
    channel.start_consuming()

