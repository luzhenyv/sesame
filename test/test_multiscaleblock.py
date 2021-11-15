import time
import torch
import numpy as np

import sesame.utils.logger as logger
from yacs.config import CfgNode
from torchsummaryX import summary
from sesame.models.attention import MultiScaleAttention, MultiScaleBlock
from sesame.models.model_builder import MViT

log = logger.get_logger(__name__)
logger.setup_logging()

def test_msa():
    msa = MultiScaleAttention(
        96, 8, False, 0.0, (1, 3, 3), (1, 3, 3),
        (1, 2, 2), (1, 2, 2),
    )
    msa.eval()
    x = torch.rand((1, 6273, 96))
    y, thw_shape = msa(x, (8, 28, 28))
    print(msa)
    print(y.shape)


def test_msb():
    msb = MultiScaleBlock(
        96, 96, 8,
        kernel_q=(1, 1, 1), kernel_kv=(1, 3, 3),
        stride_q=(1, 1, 1), stride_kv=(1, 2, 2)
    )
    msb.eval()
    x = torch.rand((1, 6273, 96))
    y, thw_shape = msb(x, (8, 28, 28))
    print(msb)
    print(y.shape)


def test_mvit():
    cfg = CfgNode.load_cfg(open(r'../configs/Kinetics/MVIT_B_32x3_CONV.yaml'))
    model = MViT(cfg)
    model.eval()
    x_dummy = torch.rand(1, 3, 32, 224, 224)
    y_hat = model(x_dummy)
    # print(model)
    print(y_hat.shape)
    # print(summary(model, torch.rand(1, 3, 32, 224, 224)))


start = time.perf_counter()
# test_msa()
# test_msb()
# test_mvit()
labels = np.eye(10)[np.random.randint(0, 10, (10,)).tolist()]
preds = np.random.rand(10, 10)
print(f'labels is {labels}')
# print(f'prediction is {preds}')
print(f'labels[:, ~(np.all(labels == 0, axis=0))] is {labels[:, ~(np.all(labels == 0, axis=0))]}')
# preds = labels[:, ~(np.all(labels == 0, axis=0))]

end = time.perf_counter()
print(f'consuming time is {end - start}')
print(globals()['test_msa'])
