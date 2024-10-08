"""
Internal code snippets were obtained from https://github.com/SystemErrorWang/White-box-Cartoonization/

For it to work tensorflow version 2.x changes were obtained from https://github.com/steubk/White-box-Cartoonization 
"""
import os
import uuid
import time
import subprocess
import sys

from tqdm import tqdm
import cv2
import numpy as np
import skvideo.io
try:
    import tensorflow.compat.v1 as tf
except ImportError:
    import tensorflow as tf

import network
import guided_filter
from pathlib import Path

class WB_Cartoonize:
    def __init__(self, weights_dir, gpu):
        if not os.path.exists(weights_dir):
            raise FileNotFoundError("Weights Directory not found, check path")
        self.load_model(weights_dir, gpu)
        print("Weights successfully loaded")
    
    def resize_crop(self, image):
        h, w, c = np.shape(image)
        if min(h, w) > 1080:
            if h > w:
                h, w = int(1080*h/w), 1080
            else:
                h, w = 1080, int(1080*w/h)
        image = cv2.resize(image, (w, h),
                            interpolation=cv2.INTER_AREA)
        h, w = (h//8)*8, (w//8)*8
        image = image[:h, :w, :]
        return image

    def load_model(self, weights_dir, gpu):
        try:
            tf.disable_eager_execution()
        except:
            None

        tf.reset_default_graph()

        
        self.input_photo = tf.placeholder(tf.float32, [1, None, None, 3], name='input_image')
        network_out = network.unet_generator(self.input_photo)
        self.final_out = guided_filter.guided_filter(self.input_photo, network_out, r=1, eps=5e-3)

        all_vars = tf.trainable_variables()
        gene_vars = [var for var in all_vars if 'generator' in var.name]
        saver = tf.train.Saver(var_list=gene_vars)
        
        if gpu:
            gpu_options = tf.GPUOptions(allow_growth=True)
            device_count = {'GPU':1}
        else:
            gpu_options = None
            device_count = {'GPU':0}
        
        config = tf.ConfigProto(gpu_options=gpu_options, device_count=device_count)
        
        self.sess = tf.Session(config=config)

        self.sess.run(tf.global_variables_initializer())
        saver.restore(self.sess, tf.train.latest_checkpoint(weights_dir))

    def infer(self, image):
        image = self.resize_crop(image)
        batch_image = image.astype(np.float32)/127.5 - 1
        batch_image = np.expand_dims(batch_image, axis=0)
        
        ## Session Run
        output = self.sess.run(self.final_out, feed_dict={self.input_photo: batch_image})
        
        ## Post Process
        output = (np.squeeze(output)+1)*127.5
        output = np.clip(output, 0, 255).astype(np.uint8)
        
        return output
    
    def process_video(self, fname, frame_rate):
        ## Capture video using opencv
        cap = cv2.VideoCapture(fname)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # get total number of frames

        target_size = (int(cap.get(3)),int(cap.get(4)))
        output_fname = os.path.abspath('{}/{}-{}.mp4'.format(fname.replace(os.path.basename(fname), ''),os.path.basename(fname).split('.')[0],str(uuid.uuid4())[:7]))

        out = skvideo.io.FFmpegWriter(output_fname, inputdict={'-r':frame_rate}, outputdict={'-r':frame_rate})

        pbar = tqdm(total=total_frames)
        while True:
            ret, frame = cap.read()
            
            if ret:
                  
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                   
                frame = self.infer(frame)
                   
                frame = cv2.resize(frame, target_size)
                  
                out.writeFrame(frame)
                pbar.update(1)  # update the progress bar
                    
            else:
                break
        pbar.close()
        cap.release()
        out.close()
        
        final_name = '{}{}_toon{}'.format(fname.replace(os.path.basename(fname), ''), Path(output_fname).stem, Path(output_fname).suffix)

        os.system(f"ffmpeg -i {output_fname} -i {fname} -pix_fmt yuv420p -map 0:v -map 1:a -c:v libx264 -c:a aac {final_name}")

        os.system("rm "+output_fname)

        return final_name

