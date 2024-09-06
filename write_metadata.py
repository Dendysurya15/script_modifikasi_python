# from tflite_support.metadata_writers import object_detector
# from tflite_support.metadata_writers import writer_utils
# from tflite_support import metadata

# ObjectDetectorWriter = object_detector.MetadataWriter
# _MODEL_PATH = "/home/grading/hasil_train_6_class/weights/best_saved_model/best_float16.tflite"
# _LABEL_FILE = "/home/grading/hasil_train_6_class/weights/classes.txt"
# _SAVE_TO_PATH = "/home/grading/hasil_train_6_class/weights/best_float16.tflite"

# writer = ObjectDetectorWriter.create_for_inference(
#     writer_utils.load_file(_MODEL_PATH), [127.5], [127.5], [_LABEL_FILE])
# writer_utils.save_file(writer.populate(), _SAVE_TO_PATH)

# # Verify the populated metadata and associated files.
# displayer = metadata.MetadataDisplayer.with_model_file(_SAVE_TO_PATH)
# print("Metadata populated:")
# print(displayer.get_metadata_json())
# print("Associated file(s) populated:")
# print(displayer.get_packed_associated_file_list())

import argparse
from tflite_support.metadata_writers import object_detector
from tflite_support.metadata_writers import writer_utils
from tflite_support import metadata

def main(model_path, label_file, save_to_path):
    ObjectDetectorWriter = object_detector.MetadataWriter

    writer = ObjectDetectorWriter.create_for_inference(
        writer_utils.load_file(model_path), [127.5], [127.5], [label_file])
    writer_utils.save_file(writer.populate(), save_to_path)

    # Verify the populated metadata and associated files.
    displayer = metadata.MetadataDisplayer.with_model_file(save_to_path)
    print("Metadata populated:")
    print(displayer.get_metadata_json())
    print("Associated file(s) populated:")
    print(displayer.get_packed_associated_file_list())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create metadata for TensorFlow Lite object detection model.")
    parser.add_argument("--model_path", required=True, help="Path to the TensorFlow Lite model file.")
    parser.add_argument("--label_file", required=True, help="Path to the label file.")
    parser.add_argument("--save_to_path", required=True, help="Path to save the metadata-populated TensorFlow Lite model file.")
    args = parser.parse_args()

    main(args.model_path, args.label_file, args.save_to_path)
