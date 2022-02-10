import torch
import torch.nn as nn

from sesame.models.roi_align import ROIAlign


class TransformerBasicHead(nn.Module):
    """
    Basic Classify Head. No pool.
    """

    def __init__(
            self,
            dim_in,
            num_classes,
            dropout_rate=0.0,
            act_func="softmax",
    ):
        """
        Perform linear projection and activation as head for tranformers.
        Args:
            dim_in (int): the channel dimension of the input to the head.
            num_classes (int): the channel dimensions of the output to the head.
            dropout_rate (float): dropout rate. If equal to 0.0, perform no
                dropout.
            act_func (string): activation function to use. 'softmax': applies
                softmax on the output. 'sigmoid': applies sigmoid on the output.
        """
        super(TransformerBasicHead, self).__init__()
        if dropout_rate > 0.0:
            self.dropout = nn.Dropout(dropout_rate)
        self.projection = nn.Linear(dim_in, num_classes, bias=True)

        # Softmax for evaluation and testing.
        if act_func == "softmax":
            self.act = nn.Softmax(dim=1)
        elif act_func == "sigmoid":
            self.act = nn.Sigmoid()
        else:
            raise NotImplementedError(
                "{} is not supported as an activation"
                "function.".format(act_func)
            )

    def forward(self, x):
        if hasattr(self, "dropout"):
            x = self.dropout(x)
        x = self.projection(x)

        if not self.training:
            x = self.act(x)
        return x


class TransformerRoIHead(nn.Module):
    """
    Transformer RoI head
    """

    def __init__(
        self,
        dim_in,
        num_classes,
        pool_size,
        resolution,
        scale_factor,
        dropout_rate=0.0,
        act_func="softmax",
        aligned=True,
    ):
        """
        The `__init__` method of any subclass should also contain these
           arguments.

        Args:
           dim_in (int): the channel dimensions of inputs to the head.
           num_classes (int): the channel dimensions of outputs to the head.
           pool_size (list): the kernel sizes of spatial temporal pooling.
                temporal pool kernel size, spatial pool kernel size,
                spatial pool kernel size in order.
           resolution (list): the spatial output size from the ROIAlign.
           scale_factor (float): the ratio to the input boxes by this number.
           dropout_rate (float): dropout rate. If equal to 0.0, no dropout.
           act_func (string): activation function to use. 'softmax', 'sigmoid' etc.
           aligned (bool): if False, use the legacy implementation. If True,
               align the results more perfectly.
        Note:
           Given a continuous coordinate c, its two neighboring pixel indices
           (in our pixel model) are computed by floor (c - 0.5) and ceil
           (c - 0.5). For example, c=1.3 has pixel neighbors with discrete
           indices [0] and [1] (which are sampled from the underlying signal at
           continuous coordinates 0.5 and 1.5). But the original roi_align
           (aligned=False) does not subtract the 0.5 when computing neighboring
           pixel indices and therefore it uses pixels with a slightly incorrect
           alignment (relative to our pixel model) when performing bilinear
           interpolation.
           With `aligned=True`, we first appropriately scale the ROI and then
           shift it by -0.5 prior to calling roi_align. This produces the
           correct neighbors; It makes negligible differences to the model's
           performance if ROIAlign is used together with conv layers.
        """
        super(TransformerRoIHead, self).__init__()
        self.temporal_pool = nn.AvgPool3d(pool_size, stride=1)
        self.roi_align = ROIAlign(
            resolution,
            spatial_scale=1.0/scale_factor,
            sampling_ratio=0.0,
            aligned=aligned,
        )
        self.spatial_pool = nn.MaxPool2d(resolution, stride=1)
        if dropout_rate > 0.0:
            self.dropout = nn.Dropout(dropout_rate)

        # Perform FC in a fully convolutional manner. The FC layer will be
        # initialized with a different std comparing to convolutional layers.
        self.projection = nn.Linear(dim_in, num_classes, bias=True)

        if act_func == "softmax":
            self.act = nn.Softmax(dim=1)
        elif act_func == "sigmoid":
            self.act = nn.Sigmoid()
        else:
            raise NotImplementedError(
                "{} is not supported as an activation"
                "function.".format(act_func)
            )

    def forward(self, inputs, bboxes):
        out = self.temporal_pool(inputs)
        out = torch.squeeze(out, 2)
        out = self.roi_align(out, bboxes)
        out = self.spatial_pool(out)

        # Perform dropout.
        if hasattr(self, "dropout"):
            out = self.dropout(out)

        out = out.view(out.shape[0], -1)
        out = self.projection(out)
        out = self.act(out)
        return out

