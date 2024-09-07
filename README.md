## Turn your image or video into a cartoon

A tool for converting images and videos into cartoons. Tested on python 3.7.

## Results
<div>
<img src="/media/toonize.webp" width="640"/>
</div>

This code is based on WhiteBox cartoonization tool from https://github.com/SystemErrorWang/White-box-Cartoonization/. It uses pretrained models from https://github.com/experience-ml/cartoonize.

## Install

Create virtual environment

```
python -m venv .venv
pip install -r requirements.txt
```

## Run

Set environment variable before running.

```
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
```

Convert image to cartoon (code replaces image in place):

```
python toonize.py image.jpg
```

Convert all jpg images in curent folder to cartoon:

```
python toonize.py "*.jpg"
```

Convert video to cartoon:

```
python toonize.py video.mp4
```
