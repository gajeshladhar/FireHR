# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_predict.ipynb (unless otherwise specified).

__all__ = ['get_preds']

# Cell
import numpy as np
import pandas as pd
import torch
import rasterio
import matplotlib.pyplot as plt
from pathlib import Path
from IPython.core.debugger import set_trace
from fastprogress import progress_bar
from banet.predict import image2tiles, tiles2image
from rasterio.crs import CRS
from fire_split.core import split_fires, save_data, to_polygon
from .data import download_data, RegionST, get_event_data
from .models import *

#Hi Everyone Yes
#Yo Yo
# Cell
def get_preds(im, thr=0.5, tile_size=2048, tile_step=2000, max_image_size=2048,
              coarse_mask_expansion_size=101, gpu=True):
    image_size = im.shape[:2]
    if max(image_size) < max_image_size:
        im = torch.from_numpy(im)[None].permute(0,3,1,2).float()
    else:
        im = torch.from_numpy(
            image2tiles(im, step=tile_step, size=tile_size)).permute(0,3,1,2).float()
    model = load_pretrained_model(gpu=gpu)
    outs = []
    print('Generating model predicitons...')
    with torch.no_grad():
        for im0 in progress_bar(im):
            im0 = im0[None]
            im0 = expand_filter(im0, ks=coarse_mask_expansion_size)
            if gpu:
                out = model(im0.half().cuda()).squeeze().sigmoid()
            else:
                out = model(im0).squeeze().sigmoid()
            out = out.cpu().numpy()
            outs.append(out)

    outs = np.array(outs)
    if max(image_size) > max_image_size:
        out = tiles2image(outs, image_size, size=tile_size, step=tile_step)
    else: out = outs.squeeze().astype(np.float32)
    out[out<thr] = 0
    return out
