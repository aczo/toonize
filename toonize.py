import sys
import cv2
import os
import ffmpeg
from pathlib import Path

# add path to cartoonizer
sys.path.insert(0, './white_box_cartoonizer/')

from cartoonize import WB_Cartoonize
#initialize the cartoonizer
wb_cartoonizer = WB_Cartoonize(os.path.abspath("white_box_cartoonizer/saved_models/"), False)

def is_video(file_path):
    video_stream = ffmpeg.probe(file_path, select_streams='v')['streams']

    if video_stream:
        return True
    else:
        return False

def process_images(pattern):
    directory = Path(pattern).parent
    file_pattern = Path(pattern).name
    
    # Find all files matching the pattern in the specified directory
    for img_path in directory.glob(file_pattern):
        if img_path.is_file():
            img = cv2.imread(str(img_path)) # attempt opening image
            if not img is None:
                print("Processing image: {}".format(img_path))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                cartoon_image = wb_cartoonizer.infer(img)
                new_img_name = img_path.stem + '_toon' + img_path.suffix
                new_img_path = img_path.with_name(new_img_name)
                cv2.imwrite(str(img_path), cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
            else: # try to process video
                if is_video(str(img_path)):
                    print("Processing video: {}".format(img_path))
                    cap = cv2.VideoCapture(str(img_path))
                    fps = str(round(cap.get(cv2.CAP_PROP_FPS),2))
                    cap.release()
                    wb_cartoonizer.process_video(str(img_path), fps)
                else:
                    print("Unknown format of {}. Skipping".format(img_path))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cartoonize.py '<path/pattern>'")
    else:
        pattern = sys.argv[1]
        process_images(pattern)
