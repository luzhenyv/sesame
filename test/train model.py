#!/usr/bin/env python
# coding: utf-8

# # Train Model


import os
import sys
# sys.path.append('/Users/zhenyvlu/work/sesame')
sys.path.append(r"C:\Users\luzhe\deep_learning\sesame")

import numpy as np
import torch

import sesame.utils.distributed as du
import sesame.utils.checkpoint as cu
import sesame.utils.misc as misc
import sesame.models.optimizer as optim
import sesame.visualization.tensorboard_vis as tb
import sesame.utils.logger as logger

from sesame.utils.parser import load_config, parse_args
from sesame.datasets.kinetics import Kinetics
from sesame.models.model_builder import MViT
from sesame.utils.meters import TrainMeter, ValMeter, EpochTimer
from sesame.config.defaults import get_cfg
from tools.train_net import train_epoch, eval_epoch

log = logger.get_logger('train model')
logger.setup_logging('.')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


cfg = get_cfg()
cfg.merge_from_file("../configs/Kinetics/MINI_MVIT_B_16x4_CONV.yaml")

# cfg = CN.load_cfg(open("../configs/Kinetics/MVIT_B_16x4_CONV.yaml", "r", encoding="UTF-8"))

model = MViT(cfg)
checkpoint = torch.load(r"C:\Users\luzhe\deep_learning\multiscale vision transformers\K400_MVIT_B_16x4_CONV.pyth", map_location=torch.device('cpu'))
# 去除头部权重
model_dict = checkpoint['model_state']
# model_dict.keys()
model_dict.pop('head.projection.weight')
model_dict.pop('head.projection.bias')

model.load_state_dict(model_dict, strict=False)

for param in model.parameters():
    param.requires_grad = False
    
# 修改梯度下降
model.blocks[14].attn.pool_k.weight.requires_grad = True
model.blocks[14].attn.norm_k.weight.requires_grad = True
model.blocks[14].attn.norm_k.bias.requires_grad = True

model.blocks[14].attn.pool_v.weight.requires_grad = True
model.blocks[14].attn.norm_v.weight.requires_grad = True
model.blocks[14].attn.norm_v.bias.requires_grad = True

model.blocks[15].attn.pool_k.weight.requires_grad = True
model.blocks[15].attn.norm_k.weight.requires_grad = True
model.blocks[15].attn.norm_k.bias.requires_grad = True

model.blocks[15].attn.pool_v.weight.requires_grad = True
model.blocks[15].attn.norm_v.weight.requires_grad = True
model.blocks[15].attn.norm_v.bias.requires_grad = True

model.head.projection.weight.requires_grad = True
model.head.projection.bias.requires_grad = True

# missing_keys=['blocks.14.attn.pool_k.weight',
#               'blocks.14.attn.norm_k.weight',
#               'blocks.14.attn.norm_k.bias',
#
#               'blocks.14.attn.pool_v.weight',
#               'blocks.14.attn.norm_v.weight',
#               'blocks.14.attn.norm_v.bias',
#
#               'blocks.15.attn.pool_k.weight',
#               'blocks.15.attn.norm_k.weight',
#               'blocks.15.attn.norm_k.bias',
#
#               'blocks.15.attn.pool_v.weight',
#               'blocks.15.attn.norm_v.weight',
#               'blocks.15.attn.norm_v.bias']

model.to(device)
optimizer = optim.construct_optimizer(model, cfg)

kinetics_dataset_train = Kinetics(cfg, 'train')
kinetics_dataset_val = Kinetics(cfg, 'val')

kinetics_dataset_train_loader = torch.utils.data.DataLoader(
            kinetics_dataset_train,
            batch_size=int(cfg.TRAIN.BATCH_SIZE / max(1, cfg.NUM_GPUS)),
            num_workers=cfg.DATA_LOADER.NUM_WORKERS,
            pin_memory=cfg.DATA_LOADER.PIN_MEMORY,
            shuffle=True,
            drop_last=True,
            worker_init_fn=None,
        )

kinetics_dataset_val_loader = torch.utils.data.DataLoader(
            kinetics_dataset_val,
            batch_size=int(cfg.TRAIN.BATCH_SIZE / max(1, cfg.NUM_GPUS)),
            num_workers=cfg.DATA_LOADER.NUM_WORKERS,
            pin_memory=cfg.DATA_LOADER.PIN_MEMORY,
            drop_last=True,
            worker_init_fn=None,
        )

train_meter = TrainMeter(len(kinetics_dataset_train_loader), cfg)
val_meter = ValMeter(len(kinetics_dataset_val_loader), cfg)


scaler = torch.cuda.amp.GradScaler(enabled=cfg.TRAIN.MIXED_PRECISION)

# set up writer for logging to Tensorboard format.
if cfg.TENSORBOARD.ENABLE and du.is_master_proc(cfg.NUM_GPUS * cfg.NUM_SHARDS):
    writer = tb.TensorboardWriter(cfg)
else:
    writer = None

start_epoch = 0
# Perform the training loop.
# log.info("Start epoch: {}".format(start_epoch + 1))

epoch_timer = EpochTimer()
for cur_epoch in range(start_epoch, cfg.SOLVER.MAX_EPOCH):
    # Shuffle the dataset.
#     loader.shuffle_dataset(train_loader, cur_epoch)

    # Train for one epoch.
    epoch_timer.epoch_tic()
    train_epoch(
        kinetics_dataset_train_loader,
        model,
        optimizer,
        scaler,
        train_meter,
        cur_epoch,
        cfg,
        writer,
    )
    epoch_timer.epoch_toc()

    is_checkp_epoch = cu.is_checkpoint_epoch(
        cfg,
        cur_epoch,
        None
    )
    is_eval_epoch = misc.is_eval_epoch(
        cfg, cur_epoch, None
    )

    # Compute precise BN stats.
    if (
        (is_checkp_epoch or is_eval_epoch)
        and cfg.BN.USE_PRECISE_STATS
        and len(get_bn_modules(model)) > 0
    ):
        calculate_and_update_precise_bn(
            precise_bn_loader,
            model,
            min(cfg.BN.NUM_BATCHES_PRECISE, len(precise_bn_loader)),
            cfg.NUM_GPUS > 0,
        )
#     _ = misc.aggregate_sub_bn_stats(model)

    # Save a checkpoint.
    if is_checkp_epoch:
        cu.save_checkpoint(
            cfg.OUTPUT_DIR,
            model,
            optimizer,
            cur_epoch,
            cfg,
            scaler if cfg.TRAIN.MIXED_PRECISION else None,
        )
    # Evaluate the model on validation set.
    if is_eval_epoch:
        eval_epoch(kinetics_dataset_val_loader, model, val_meter, cur_epoch, cfg, writer)

if writer is not None:
    writer.close()



