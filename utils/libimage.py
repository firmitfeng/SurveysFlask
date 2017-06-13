# -*- coding: utf-8 -*-
import os
from PIL import Image

def resizeImg(origin_file_path, new_file_path, width=640, height=0):
    im = Image.open(origin_file_path)
    (w, h) = im.size
    if w > width:
        w_n = width
    else:
        w_n = w

    if height != 0 and h > height:
        h_n = height
    elif height == 0:
        h_n = h*w_n/w
        if h_n > h:
            h_n = h
    else:
        h_n = height

    out = im.resize((w_n, h_n), Image.ANTIALIAS)  # resize image with high-quality
    out.save(new_file_path)


class Horizontal:
    LEFT = -1
    CENTER = 0
    RIGHT = 1

class Vertical:
    TOP = -1
    MIDDLE = 0
    BOTTOM = 1

def clipImg(origin_file_path, new_file_path, width=150, height=150, h=Horizontal.CENTER, v=Vertical.MIDDLE):
    im = Image.open(origin_file_path)

    (w, h) = im.size

    if w < width:
        x = 0
        width = w
    else:
        if h == Horizontal.LEFT:
            x = 0
        elif h == Horizontal.RIGHT:
            x = w-width
        else :
            x = (w-width)/2

    if h < height:
        y = 0
        height = h
    else:
        if v == Vertical.TOP:
            y = 0
        elif v == Vertical.BOTTOM:
            y = h-height
        else:
            y = (h-height)/2

    # 这里的参数可以这么认为：从某图的(x,y)坐标开始截，截到(width+x,height+y)坐标
    region = (x, y, x+width, y+height)
    #print region

    # 裁切图片
    cropImg = im.crop(region)

    # 保存裁切后的图片
    cropImg.save(new_file_path)


def clipReszImg(origin_file_path, new_file_path, width=150, height=150, h=Horizontal.CENTER, v=Vertical.MIDDLE):

    im = Image.open(origin_file_path)
    (w, h) = im.size

    width_scale = float(w)/width
    height_scale = float(h)/height

    if width_scale > height_scale:
        w_n = w / height_scale
        h_n = height
    else:
        w_n = width
        h_n = height / width_scale

    reImg = im.resize((int(w_n), int(h_n)), Image.ANTIALIAS)  # resize image with high-quality
    reImg.save(new_file_path)

    clipImg(new_file_path, new_file_path, width, height, h, v)

