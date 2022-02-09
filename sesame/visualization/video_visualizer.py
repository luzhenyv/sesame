import math
import colorsys
import itertools
import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
import matplotlib.figure as mplfigure
import torch
from enum import Enum, unique
from matplotlib.backends.backend_agg import FigureCanvasAgg

import sesame.utils.logger as logger
from sesame.utils.misc import get_class_names
from sesame.visualization.colormap import random_color


log = logger.get_logger(__name__)


_SMALL_OBJECT_AREA_THRESH = 1000
_LARGE_MASK_AREA_THRESH = 120000
_OFF_WHITE = (1.0, 1.0, 240.0 / 255)
_BLACK = (0, 0, 0)
_RED = (1.0, 0, 0)


@unique
class ColorMode(Enum):
    """
    Enum of different color modes to use for instance visualizations.
    """
    IMAGE = 0
    """
    Picks a random color for every instance and overlay segmentations
    with low opacity.
    """
    SEGMENTATION = 1
    """
    Let instances of the same category have similar colors (from
    meta.things_colors), and overlay them with high opacity. This
    provides more attention on the quality of segmentation.
    """
    IMAGE_BW = 2
    """
    Same as IMAGE, but convert all areas without masks to gray-scale.
    Only available for drawing per-instance mask predictions.
    """


class VisImage(object):
    def __init__(self, img, scale=1.0):
        """
        Args:
            img (ndarray): an RGB image of shape (H, W, 3) in range [0, 255].
            scale (float): scale the input image
        """
        self.img = img
        self.scale = scale
        self.width, self.height = img.shape[1], img.shape[0]
        self._setup_figure(img)

    def _setup_figure(self, img):
        """
        Args:
            Same as in :meth:`__init__()`.
        Returns:
            fig (matplotlib.pyplot.figure): top level container
                for all the image plot elements.
            ax (matplotlib.pyplot.Axes): contains figure elements
                and sets the coordinate system.
        """
        fig = mplfigure.Figure(frameon=False)
        self.dpi = fig.get_dpi()
        # add a small 1e-2 to avoid precision lost due to matplotlib's truncation
        # (https://github.com/matplotlib/matplotlib/issues/15363)
        fig.set_size_inches(
            (self.width * self.scale + 1e-2) / self.dpi,
            (self.height * self.scale + 1e-2) / self.dpi,
        )
        self.canvas = FigureCanvasAgg(fig)
        ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
        ax.axis("off")
        self.fig = fig
        self.ax = ax
        self.reset_image(img)

    def reset_image(self, img):
        """
        Args:
            img: same as in __init__
        """
        img = img.astype("uint8")
        self.ax.imshow(
            img,
            extent=(0, self.width, self.height, 0),
            interpolation="nearest"
        )

    def save(self, filepath):
        """
        Args:
            filepath (str): a string that contains the absolute path,
                including the file name, where the visualized image
                will be saved.
        """
        self.fig.savefig(filepath)

    def get_image(self):
        """
        Returns:
            ndarray:
                the visualized image of shape (H, W, 3) (RGB) in
                uint8 type. The shape is scaled w.r.t the input
                image using the given `scale` argument.
        """
        canvas = self.canvas
        s, (width, height) = canvas.print_to_buffer()
        # buf = io.BytesIO()  # works for cairo backend
        # canvas.print_rgba(buf)
        # width, height = self.width, self.height
        # s = buf.getvalue()

        buffer = np.frombuffer(s, dtype="uint8")

        img_rgba = buffer.reshape(height, width, 4)
        rgb, alpha = np.split(img_rgba, [3], axis=2)
        return rgb.astype("uint8")


class Visualizer(object):
    """
    Visualizer that draws data about detection/segmentation on images.
    It contains methods like `draw_{text,box,circle,line,binary_mask,polygon}`
    that draw primitive objects to images, as well as high-level wrappers like
    `draw_{instance_predictions,sem_seg,panoptic_seg_predictions,dataset_dict}`
    that draw composite data in some pre-defined style.
    Note that the exact visualization style for the high-level wrappers are subject to change.
    Style such as color, opacity, label contents, visibility of labels, or even the visibility
    of objects themselves (e.g. when the object is too small) may change according
    to different heuristics, as long as the results still look visually reasonable.
    To obtain a consistent style, you can implement custom drawing functions with the
    abovementioned primitive methods instead. If you need more customized visualization
    styles, you can process the data yourself following their format documented in
    tutorials (:doc:`/tutorials/models`, :doc:`/tutorials/datasets`). This class does not
    intend to satisfy everyone's preference on drawing styles.
    This visualizer focuses on high rendering quality rather than performance. It is not
    designed to be used for real-time applications.
    """

    # TODO implement a fast, rasterized version using OpenCV

    def __init__(self, img_rgb, metadata=None, scale=1.0, instance_mode=ColorMode.IMAGE):
        """
        Args:
            img_rgb: a numpy array of shape (H, W, C), where H and W correspond to
                the height and width of the image respectively. C is the number of
                color channels. The image is required to be in RGB format since that
                is a requirement of the Matplotlib library. The image is also expected
                to be in the range [0, 255].
            metadata (Metadata): dataset metadata (e.g. class names and colors)
            instance_mode (ColorMode): defines one of the pre-defined style for drawing
                instances on an image.
        """
        self.img = np.asarray(img_rgb).clip(0, 255).astype(np.uint8)
        # if metadata is None:
        #     metadata = MetadataCatalog.get("__nonexist__")
        self.metadata = metadata
        self.output = VisImage(self.img, scale=scale)
        self.cpu_device = torch.device("cpu")

        # too small texts are useless, therefore clamp to 9
        self._default_font_size = max(
            np.sqrt(self.output.height * self.output.width) // 90, 10 // scale
        )
        self._instance_mode = instance_mode
        # self.keypoint_threshold = _KEYPOINT_THRESHOLD

    def draw_instance_predictions(self, predictions):
        """
        Draw instance-level prediction results on an image.
        Args:
            predictions (Instances): the output of an instance detection/segmentation
                model. Following fields will be used to draw:
                "pred_boxes", "pred_classes", "scores", "pred_masks" (or "pred_masks_rle").
        Returns:
            output (VisImage): image object with visualizations.
        """
        boxes = predictions.pred_boxes if predictions.has("pred_boxes") else None
        scores = predictions.scores if predictions.has("scores") else None
        classes = predictions.pred_classes.tolist() if predictions.has("pred_classes") else None
        labels = _create_text_labels(classes, scores, self.metadata.get("thing_classes", None))
        # keypoints = predictions.pred_keypoints if predictions.has("pred_keypoints") else None

        if predictions.has("pred_masks"):
            masks = np.asarray(predictions.pred_masks)
            # masks = [GenericMask(x, self.output.height, self.output.width) for x in masks]
        else:
            masks = None

        if self._instance_mode == ColorMode.SEGMENTATION and self.metadata.get("thing_colors"):
            colors = [
                self._jitter([x / 255 for x in self.metadata.thing_colors[c]]) for c in classes
            ]
            alpha = 0.8
        else:
            colors = None
            alpha = 0.5

        if self._instance_mode == ColorMode.IMAGE_BW:
            self.output.reset_image(
                self._create_grayscale_image(
                    (predictions.pred_masks.any(dim=0) > 0).numpy()
                    if predictions.has("pred_masks")
                    else None
                )
            )
            alpha = 0.3

        self.overlay_instances(
            masks=masks,
            boxes=boxes,
            labels=labels,
            # keypoints=keypoints,
            assigned_colors=colors,
            alpha=alpha,
        )
        return self.output

    def draw_sem_seg(self, sem_seg, area_threshold=None, alpha=0.8):
        """
        Draw semantic segmentation predictions/labels.
        Args:
            sem_seg (Tensor or ndarray): the segmentation of shape (H, W).
                Each value is the integer label of the pixel.
            area_threshold (int): segments with less than `area_threshold` are not drawn.
            alpha (float): the larger it is, the more opaque the segmentations are.
        Returns:
            output (VisImage): image object with visualizations.
        """
        if isinstance(sem_seg, torch.Tensor):
            sem_seg = sem_seg.numpy()
        labels, areas = np.unique(sem_seg, return_counts=True)
        sorted_idxs = np.argsort(-areas).tolist()
        labels = labels[sorted_idxs]
        for label in filter(lambda l: l < len(self.metadata.stuff_classes), labels):
            try:
                mask_color = [x / 255 for x in self.metadata.stuff_colors[label]]
            except (AttributeError, IndexError):
                mask_color = None

            binary_mask = (sem_seg == label).astype(np.uint8)
            text = self.metadata.stuff_classes[label]
            self.draw_binary_mask(
                binary_mask,
                color=mask_color,
                edge_color=(1.0, 1.0, 240.0 / 255),
                text=text,
                alpha=alpha,
                area_threshold=area_threshold,
            )
        return self.output

    def draw_panoptic_seg(self, panoptic_seg, segments_info, area_threshold=None, alpha=0.7):
        """
        Draw panoptic prediction annotations or results.
        Args:
            panoptic_seg (Tensor): of shape (height, width) where the values are ids for each
                segment.
            segments_info (list[dict] or None): Describe each segment in `panoptic_seg`.
                If it is a ``list[dict]``, each dict contains keys "id", "category_id".
                If None, category id of each pixel is computed by
                ``pixel // metadata.label_divisor``.
            area_threshold (int): stuff segments with less than `area_threshold` are not drawn.
        Returns:
            output (VisImage): image object with visualizations.
        """
        pass

    draw_panoptic_seg_predictions = draw_panoptic_seg  # backward compatibility

    def draw_dataset_dict(self, dic):
        """
        Draw annotations/segmentaions in Detectron2 Dataset format.
        Args:
            dic (dict): annotation/segmentation data of one image, in Detectron2 Dataset format.
        Returns:
            output (VisImage): image object with visualizations.
        """
        pass

    def overlay_instances(
        self,
        *,
        boxes=None,
        labels=None,
        masks=None,
        keypoints=None,
        assigned_colors=None,
        alpha=0.5,
    ):
        """
        Args:
            boxes (Boxes, RotatedBoxes or ndarray): either a :class:`Boxes`,
                or an Nx4 numpy array of XYXY_ABS format for the N objects in a single image,
                or a :class:`RotatedBoxes`,
                or an Nx5 numpy array of (x_center, y_center, width, height, angle_degrees) format
                for the N objects in a single image,
            labels (list[str]): the text to be displayed for each instance.
            masks (masks-like object): Supported types are:
                * :class:`detectron2.structures.PolygonMasks`,
                  :class:`detectron2.structures.BitMasks`.
                * list[list[ndarray]]: contains the segmentation masks for all objects in one image.
                  The first level of the list corresponds to individual instances. The second
                  level to all the polygon that compose the instance, and the third level
                  to the polygon coordinates. The third level should have the format of
                  [x0, y0, x1, y1, ..., xn, yn] (n >= 3).
                * list[ndarray]: each ndarray is a binary mask of shape (H, W).
                * list[dict]: each dict is a COCO-style RLE.
            keypoints (Keypoint or array like): an array-like object of shape (N, K, 3),
                where the N is the number of instances and K is the number of keypoints.
                The last dimension corresponds to (x, y, visibility or score).
            assigned_colors (list[matplotlib.colors]): a list of colors, where each color
                corresponds to each mask or box in the image. Refer to 'matplotlib.colors'
                for full list of formats that the colors are accepted in.
        Returns:
            output (VisImage): image object with visualizations.
        """
        num_instances = 0
        if boxes is not None:
            boxes = self._convert_boxes(boxes)
            num_instances = len(boxes)
        if masks is not None:
            masks = self._convert_masks(masks)
            if num_instances:
                assert len(masks) == num_instances
            else:
                num_instances = len(masks)
        if keypoints is not None:
            if num_instances:
                assert len(keypoints) == num_instances
            else:
                num_instances = len(keypoints)
            keypoints = self._convert_keypoints(keypoints)
        if labels is not None:
            assert len(labels) == num_instances
        if assigned_colors is None:
            assigned_colors = [random_color(rgb=True, maximum=1) for _ in range(num_instances)]
        if num_instances == 0:
            return self.output
        if boxes is not None and boxes.shape[1] == 5:
            return self.overlay_rotated_instances(
                boxes=boxes, labels=labels, assigned_colors=assigned_colors
            )

        # Display in largest to smallest order to reduce occlusion.
        areas = None
        if boxes is not None:
            areas = np.prod(boxes[:, 2:] - boxes[:, :2], axis=1)
        elif masks is not None:
            areas = np.asarray([x.area() for x in masks])

        if areas is not None:
            sorted_idxs = np.argsort(-areas).tolist()
            # Re-order overlapped instances in descending order.
            boxes = boxes[sorted_idxs] if boxes is not None else None
            labels = [labels[k] for k in sorted_idxs] if labels is not None else None
            masks = [masks[idx] for idx in sorted_idxs] if masks is not None else None
            assigned_colors = [assigned_colors[idx] for idx in sorted_idxs]
            keypoints = keypoints[sorted_idxs] if keypoints is not None else None

        for i in range(num_instances):
            color = assigned_colors[i]
            if boxes is not None:
                self.draw_box(boxes[i], edge_color=color)

            if masks is not None:
                for segment in masks[i].polygons:
                    self.draw_polygon(segment.reshape(-1, 2), color, alpha=alpha)

            if labels is not None:
                # first get a box
                if boxes is not None:
                    x0, y0, x1, y1 = boxes[i]
                    text_pos = (x0, y0)  # if drawing boxes, put text on the box corner.
                    horiz_align = "left"
                elif masks is not None:
                    # skip small mask without polygon
                    if len(masks[i].polygons) == 0:
                        continue

                    x0, y0, x1, y1 = masks[i].bbox()

                    # draw text in the center (defined by median) when box is not drawn
                    # median is less sensitive to outliers.
                    text_pos = np.median(masks[i].mask.nonzero(), axis=1)[::-1]
                    horiz_align = "center"
                else:
                    continue  # drawing the box confidence for keypoints isn't very useful.
                # for small objects, draw text at the side to avoid occlusion
                instance_area = (y1 - y0) * (x1 - x0)
                if (
                    instance_area < _SMALL_OBJECT_AREA_THRESH * self.output.scale
                    or y1 - y0 < 40 * self.output.scale
                ):
                    if y1 >= self.output.height - 5:
                        text_pos = (x1, y0)
                    else:
                        text_pos = (x0, y1)

                height_ratio = (y1 - y0) / np.sqrt(self.output.height * self.output.width)
                lighter_color = self._change_color_brightness(color, brightness_factor=0.7)
                font_size = (
                    np.clip((height_ratio - 0.02) / 0.08 + 1, 1.2, 2)
                    * 0.5
                    * self._default_font_size
                )
                self.draw_text(
                    labels[i],
                    text_pos,
                    color=lighter_color,
                    horizontal_alignment=horiz_align,
                    font_size=font_size,
                )

        # draw keypoints
        if keypoints is not None:
            for keypoints_per_instance in keypoints:
                self.draw_and_connect_keypoints(keypoints_per_instance)

        return self.output

    def overlay_rotated_instances(self, boxes=None, labels=None, assigned_colors=None):
        """
        Args:
            boxes (ndarray): an Nx5 numpy array of
                (x_center, y_center, width, height, angle_degrees) format
                for the N objects in a single image.
            labels (list[str]): the text to be displayed for each instance.
            assigned_colors (list[matplotlib.colors]): a list of colors, where each color
                corresponds to each mask or box in the image. Refer to 'matplotlib.colors'
                for full list of formats that the colors are accepted in.
        Returns:
            output (VisImage): image object with visualizations.
        """
        num_instances = len(boxes)

        if assigned_colors is None:
            assigned_colors = [random_color(rgb=True, maximum=1) for _ in range(num_instances)]
        if num_instances == 0:
            return self.output

        # Display in largest to smallest order to reduce occlusion.
        if boxes is not None:
            areas = boxes[:, 2] * boxes[:, 3]

        sorted_idxs = np.argsort(-areas).tolist()
        # Re-order overlapped instances in descending order.
        boxes = boxes[sorted_idxs]
        labels = [labels[k] for k in sorted_idxs] if labels is not None else None
        colors = [assigned_colors[idx] for idx in sorted_idxs]

        for i in range(num_instances):
            self.draw_rotated_box_with_label(
                boxes[i], edge_color=colors[i], label=labels[i] if labels is not None else None
            )

        return self.output

    def draw_and_connect_keypoints(self, keypoints):
        """
        Draws keypoints of an instance and follows the rules for keypoint connections
        to draw lines between appropriate keypoints. This follows color heuristics for
        line color.
        Args:
            keypoints (Tensor): a tensor of shape (K, 3), where K is the number of keypoints
                and the last dimension corresponds to (x, y, probability).
        Returns:
            output (VisImage): image object with visualizations.
        """
        visible = {}
        keypoint_names = self.metadata.get("keypoint_names")
        for idx, keypoint in enumerate(keypoints):

            # draw keypoint
            x, y, prob = keypoint
            if prob > self.keypoint_threshold:
                self.draw_circle((x, y), color=_RED)
                if keypoint_names:
                    keypoint_name = keypoint_names[idx]
                    visible[keypoint_name] = (x, y)

        if self.metadata.get("keypoint_connection_rules"):
            for kp0, kp1, color in self.metadata.keypoint_connection_rules:
                if kp0 in visible and kp1 in visible:
                    x0, y0 = visible[kp0]
                    x1, y1 = visible[kp1]
                    color = tuple(x / 255.0 for x in color)
                    self.draw_line([x0, x1], [y0, y1], color=color)

        # draw lines from nose to mid-shoulder and mid-shoulder to mid-hip
        # Note that this strategy is specific to person keypoints.
        # For other keypoints, it should just do nothing
        try:
            ls_x, ls_y = visible["left_shoulder"]
            rs_x, rs_y = visible["right_shoulder"]
            mid_shoulder_x, mid_shoulder_y = (ls_x + rs_x) / 2, (ls_y + rs_y) / 2
        except KeyError:
            pass
        else:
            # draw line from nose to mid-shoulder
            nose_x, nose_y = visible.get("nose", (None, None))
            if nose_x is not None:
                self.draw_line([nose_x, mid_shoulder_x], [nose_y, mid_shoulder_y], color=_RED)

            try:
                # draw line from mid-shoulder to mid-hip
                lh_x, lh_y = visible["left_hip"]
                rh_x, rh_y = visible["right_hip"]
            except KeyError:
                pass
            else:
                mid_hip_x, mid_hip_y = (lh_x + rh_x) / 2, (lh_y + rh_y) / 2
                self.draw_line([mid_hip_x, mid_shoulder_x], [mid_hip_y, mid_shoulder_y], color=_RED)
        return self.output

    """
    Primitive drawing functions:
    """

    def draw_text(
        self,
        text,
        position,
        *,
        font_size=None,
        color="g",
        horizontal_alignment="center",
        rotation=0,
    ):
        """
        Args:
            text (str): class label
            position (tuple): a tuple of the x and y coordinates to place text on image.
            font_size (int, optional): font of the text. If not provided, a font size
                proportional to the image width is calculated and used.
            color: color of the text. Refer to `matplotlib.colors` for full list
                of formats that are accepted.
            horizontal_alignment (str): see `matplotlib.text.Text`
            rotation: rotation angle in degrees CCW
        Returns:
            output (VisImage): image object with text drawn.
        """
        if not font_size:
            font_size = self._default_font_size

        # since the text background is dark, we don't want the text to be dark
        color = np.maximum(list(mplc.to_rgb(color)), 0.2)
        color[np.argmax(color)] = max(0.8, np.max(color))

        x, y = position
        self.output.ax.text(
            x,
            y,
            text,
            size=font_size * self.output.scale,
            family="sans-serif",
            bbox={"facecolor": "black", "alpha": 0.8, "pad": 0.7, "edgecolor": "none"},
            verticalalignment="top",
            horizontalalignment=horizontal_alignment,
            color=color,
            zorder=10,
            rotation=rotation,
        )
        return self.output

    def draw_box(self, box_coord, alpha=0.5, edge_color="g", line_style="-"):
        """
        Args:
            box_coord (tuple): a tuple containing x0, y0, x1, y1 coordinates, where x0 and y0
                are the coordinates of the image's top left corner. x1 and y1 are the
                coordinates of the image's bottom right corner.
            alpha (float): blending efficient. Smaller values lead to more transparent masks.
            edge_color: color of the outline of the box. Refer to `matplotlib.colors`
                for full list of formats that are accepted.
            line_style (string): the string to use to create the outline of the boxes.
        Returns:
            output (VisImage): image object with box drawn.
        """
        x0, y0, x1, y1 = box_coord
        width = x1 - x0
        height = y1 - y0

        linewidth = max(self._default_font_size / 4, 1)

        self.output.ax.add_patch(
            mpl.patches.Rectangle(
                (x0, y0),
                width,
                height,
                fill=False,
                edgecolor=edge_color,
                linewidth=linewidth * self.output.scale,
                alpha=alpha,
                linestyle=line_style,
            )
        )
        return self.output

    def draw_rotated_box_with_label(
        self, rotated_box, alpha=0.5, edge_color="g", line_style="-", label=None
    ):
        """
        Draw a rotated box with label on its top-left corner.
        Args:
            rotated_box (tuple): a tuple containing (cnt_x, cnt_y, w, h, angle),
                where cnt_x and cnt_y are the center coordinates of the box.
                w and h are the width and height of the box. angle represents how
                many degrees the box is rotated CCW with regard to the 0-degree box.
            alpha (float): blending efficient. Smaller values lead to more transparent masks.
            edge_color: color of the outline of the box. Refer to `matplotlib.colors`
                for full list of formats that are accepted.
            line_style (string): the string to use to create the outline of the boxes.
            label (string): label for rotated box. It will not be rendered when set to None.
        Returns:
            output (VisImage): image object with box drawn.
        """
        cnt_x, cnt_y, w, h, angle = rotated_box
        area = w * h
        # use thinner lines when the box is small
        linewidth = self._default_font_size / (
            6 if area < _SMALL_OBJECT_AREA_THRESH * self.output.scale else 3
        )

        theta = angle * math.pi / 180.0
        c = math.cos(theta)
        s = math.sin(theta)
        rect = [(-w / 2, h / 2), (-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2)]
        # x: left->right ; y: top->down
        rotated_rect = [(s * yy + c * xx + cnt_x, c * yy - s * xx + cnt_y) for (xx, yy) in rect]
        for k in range(4):
            j = (k + 1) % 4
            self.draw_line(
                [rotated_rect[k][0], rotated_rect[j][0]],
                [rotated_rect[k][1], rotated_rect[j][1]],
                color=edge_color,
                linestyle="--" if k == 1 else line_style,
                linewidth=linewidth,
            )

        if label is not None:
            text_pos = rotated_rect[1]  # topleft corner

            height_ratio = h / np.sqrt(self.output.height * self.output.width)
            label_color = self._change_color_brightness(edge_color, brightness_factor=0.7)
            font_size = (
                np.clip((height_ratio - 0.02) / 0.08 + 1, 1.2, 2) * 0.5 * self._default_font_size
            )
            self.draw_text(label, text_pos, color=label_color, font_size=font_size, rotation=angle)

        return self.output

    def draw_circle(self, circle_coord, color, radius=3):
        """
        Args:
            circle_coord (list(int) or tuple(int)): contains the x and y coordinates
                of the center of the circle.
            color: color of the polygon. Refer to `matplotlib.colors` for a full list of
                formats that are accepted.
            radius (int): radius of the circle.
        Returns:
            output (VisImage): image object with box drawn.
        """
        x, y = circle_coord
        self.output.ax.add_patch(
            mpl.patches.Circle(circle_coord, radius=radius, fill=True, color=color)
        )
        return self.output

    def draw_line(self, x_data, y_data, color, linestyle="-", linewidth=None):
        """
        Args:
            x_data (list[int]): a list containing x values of all the points being drawn.
                Length of list should match the length of y_data.
            y_data (list[int]): a list containing y values of all the points being drawn.
                Length of list should match the length of x_data.
            color: color of the line. Refer to `matplotlib.colors` for a full list of
                formats that are accepted.
            linestyle: style of the line. Refer to `matplotlib.lines.Line2D`
                for a full list of formats that are accepted.
            linewidth (float or None): width of the line. When it's None,
                a default value will be computed and used.
        Returns:
            output (VisImage): image object with line drawn.
        """
        if linewidth is None:
            linewidth = self._default_font_size / 3
        linewidth = max(linewidth, 1)
        self.output.ax.add_line(
            mpl.lines.Line2D(
                x_data,
                y_data,
                linewidth=linewidth * self.output.scale,
                color=color,
                linestyle=linestyle,
            )
        )
        return self.output

    def draw_binary_mask(
        self, binary_mask, color=None, *, edge_color=None, text=None, alpha=0.5, area_threshold=10
    ):
        """
        Args:
            binary_mask (ndarray): numpy array of shape (H, W), where H is the image height and
                W is the image width. Each value in the array is either a 0 or 1 value of uint8
                type.
            color: color of the mask. Refer to `matplotlib.colors` for a full list of
                formats that are accepted. If None, will pick a random color.
            edge_color: color of the polygon edges. Refer to `matplotlib.colors` for a
                full list of formats that are accepted.
            text (str): if None, will be drawn on the object
            alpha (float): blending efficient. Smaller values lead to more transparent masks.
            area_threshold (float): a connected component smaller than this area will not be shown.
        Returns:
            output (VisImage): image object with mask drawn.
        """
        pass

    def draw_soft_mask(self, soft_mask, color=None, *, text=None, alpha=0.5):
        """
        Args:
            soft_mask (ndarray): float array of shape (H, W), each value in [0, 1].
            color: color of the mask. Refer to `matplotlib.colors` for a full list of
                formats that are accepted. If None, will pick a random color.
            text (str): if None, will be drawn on the object
            alpha (float): blending efficient. Smaller values lead to more transparent masks.
        Returns:
            output (VisImage): image object with mask drawn.
        """
        if color is None:
            color = random_color(rgb=True, maximum=1)
        color = mplc.to_rgb(color)

        shape2d = (soft_mask.shape[0], soft_mask.shape[1])
        rgba = np.zeros(shape2d + (4,), dtype="float32")
        rgba[:, :, :3] = color
        rgba[:, :, 3] = soft_mask * alpha
        self.output.ax.imshow(rgba, extent=(0, self.output.width, self.output.height, 0))

        if text is not None:
            lighter_color = self._change_color_brightness(color, brightness_factor=0.7)
            binary_mask = (soft_mask > 0.5).astype("uint8")
            self._draw_text_in_mask(binary_mask, text, lighter_color)
        return self.output

    def draw_polygon(self, segment, color, edge_color=None, alpha=0.5):
        """
        Args:
            segment: numpy array of shape Nx2, containing all the points in the polygon.
            color: color of the polygon. Refer to `matplotlib.colors` for a full list of
                formats that are accepted.
            edge_color: color of the polygon edges. Refer to `matplotlib.colors` for a
                full list of formats that are accepted. If not provided, a darker shade
                of the polygon color will be used instead.
            alpha (float): blending efficient. Smaller values lead to more transparent masks.
        Returns:
            output (VisImage): image object with polygon drawn.
        """
        if edge_color is None:
            # make edge color darker than the polygon color
            if alpha > 0.8:
                edge_color = self._change_color_brightness(color, brightness_factor=-0.7)
            else:
                edge_color = color
        edge_color = mplc.to_rgb(edge_color) + (1,)

        polygon = mpl.patches.Polygon(
            segment,
            fill=True,
            facecolor=mplc.to_rgb(color) + (alpha,),
            edgecolor=edge_color,
            linewidth=max(self._default_font_size // 15 * self.output.scale, 1),
        )
        self.output.ax.add_patch(polygon)
        return self.output

    """
    Internal methods:
    """

    def _jitter(self, color):
        """
        Randomly modifies given color to produce a slightly different color than the color given.
        Args:
            color (tuple[double]): a tuple of 3 elements, containing the RGB values of the color
                picked. The values in the list are in the [0.0, 1.0] range.
        Returns:
            jittered_color (tuple[double]): a tuple of 3 elements, containing the RGB values of the
                color after being jittered. The values in the list are in the [0.0, 1.0] range.
        """
        color = mplc.to_rgb(color)
        vec = np.random.rand(3)
        # better to do it in another color space
        vec = vec / np.linalg.norm(vec) * 0.5
        res = np.clip(vec + color, 0, 1)
        return tuple(res)

    def _create_grayscale_image(self, mask=None):
        """
        Create a grayscale version of the original image.
        The colors in masked area, if given, will be kept.
        """
        img_bw = self.img.astype("f4").mean(axis=2)
        img_bw = np.stack([img_bw] * 3, axis=2)
        if mask is not None:
            img_bw[mask] = self.img[mask]
        return img_bw

    def _change_color_brightness(self, color, brightness_factor):
        """
        Depending on the brightness_factor, gives a lighter or darker color i.e. a color with
        less or more saturation than the original color.
        Args:
            color: color of the polygon. Refer to `matplotlib.colors` for a full list of
                formats that are accepted.
            brightness_factor (float): a value in [-1.0, 1.0] range. A lightness factor of
                0 will correspond to no change, a factor in [-1.0, 0) range will result in
                a darker color and a factor in (0, 1.0] range will result in a lighter color.
        Returns:
            modified_color (tuple[double]): a tuple containing the RGB values of the
                modified color. Each value in the tuple is in the [0.0, 1.0] range.
        """
        assert brightness_factor >= -1.0 and brightness_factor <= 1.0
        color = mplc.to_rgb(color)
        polygon_color = colorsys.rgb_to_hls(*mplc.to_rgb(color))
        modified_lightness = polygon_color[1] + (brightness_factor * polygon_color[1])
        modified_lightness = 0.0 if modified_lightness < 0.0 else modified_lightness
        modified_lightness = 1.0 if modified_lightness > 1.0 else modified_lightness
        modified_color = colorsys.hls_to_rgb(polygon_color[0], modified_lightness, polygon_color[2])
        return modified_color

    def _convert_boxes(self, boxes):
        """
        Convert different format of boxes to an NxB array, where B = 4 or 5 is the box dimension.
        """
        pass

    def _convert_masks(self, masks_or_polygons):
        """
        Convert different format of masks or polygons to a tuple of masks and polygons.
        Returns:
            list[GenericMask]:
        """
        pass

    def _draw_text_in_mask(self, binary_mask, text, color):
        """
        Find proper places to draw text given a binary mask.
        """
        # TODO sometimes drawn on wrong objects. the heuristics here can improve.
        _num_cc, cc_labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask, 8)
        if stats[1:, -1].size == 0:
            return
        largest_component_id = np.argmax(stats[1:, -1]) + 1

        # draw text on the largest component, as well as other very large components.
        for cid in range(1, _num_cc):
            if cid == largest_component_id or stats[cid, -1] > _LARGE_MASK_AREA_THRESH:
                # median is more stable than centroid
                # center = centroids[largest_component_id]
                center = np.median((cc_labels == cid).nonzero(), axis=1)[::-1]
                self.draw_text(text, center, color=color)

    def _convert_keypoints(self, keypoints):
        pass

    def get_output(self):
        """
        Returns:
            output (VisImage): the image output containing the visualizations added
            to the image.
        """
        return self.output


class ImgVisualizer(Visualizer):
    def __init__(self, img_rgb, meta, **kwargs):
        """
        See https://github.com/facebookresearch/detectron2/blob/master/detectron2/utils/visualizer.py
        for more details.
        Args:
            img_rgb: a tensor or numpy array of shape (H, W, C), where H and W correspond to
                the height and width of the image respectively. C is the number of
                color channels. The image is required to be in RGB format since that
                is a requirement of the Matplotlib library. The image is also expected
                to be in the range [0, 255].
            meta (MetadataCatalog): image metadata.
                See https://github.com/facebookresearch/detectron2/blob/81d5a87763bfc71a492b5be89b74179bd7492f6b/detectron2/data/catalog.py#L90
        """
        super(ImgVisualizer, self).__init__(img_rgb, meta, **kwargs)

    def draw_text(
        self,
        text,
        position,
        *,
        font_size=None,
        color="w",
        horizontal_alignment="center",
        vertical_alignment="bottom",
        box_facecolor="black",
        alpha=0.5,
    ):
        """
        Draw text at the specified position.
        Args:
            text (str): the text to draw on image.
            position (list of 2 ints): the x,y coordinate to place the text.
            font_size (Optional[int]): font of the text. If not provided, a font size
                proportional to the image width is calculated and used.
            color (str): color of the text. Refer to `matplotlib.colors` for full list
                of formats that are accepted.
            horizontal_alignment (str): see `matplotlib.text.Text`.
            vertical_alignment (str): see `matplotlib.text.Text`.
            box_facecolor (str): color of the box wrapped around the text. Refer to
                `matplotlib.colors` for full list of formats that are accepted.
            alpha (float): transparency level of the box.
        """
        if not font_size:
            font_size = self._default_font_size
        x, y = position
        self.output.ax.text(
            x,
            y,
            text,
            size=font_size * self.output.scale,
            family="monospace",
            bbox={
                "facecolor": box_facecolor,
                "alpha": alpha,
                "pad": 0.7,
                "edgecolor": "none",
            },
            verticalalignment=vertical_alignment,
            horizontalalignment=horizontal_alignment,
            color=color,
            zorder=10,
        )

    def draw_multiple_text(
        self,
        text_ls,
        box_coordinate,
        *,
        top_corner=True,
        font_size=None,
        color="w",
        box_facecolors="black",
        alpha=0.5,
    ):
        """
        Draw a list of text labels for some bounding box on the image.
        Args:
            text_ls (list of strings): a list of text labels.
            box_coordinate (tensor): shape (4,). The (x_left, y_top, x_right, y_bottom)
                coordinates of the box.
            top_corner (bool): If True, draw the text labels at (x_left, y_top) of the box.
                Else, draw labels at (x_left, y_bottom).
            font_size (Optional[int]): font of the text. If not provided, a font size
                proportional to the image width is calculated and used.
            color (str): color of the text. Refer to `matplotlib.colors` for full list
                of formats that are accepted.
            box_facecolors (str): colors of the box wrapped around the text. Refer to
                `matplotlib.colors` for full list of formats that are accepted.
            alpha (float): transparency level of the box.
        """
        if not isinstance(box_facecolors, list):
            box_facecolors = [box_facecolors] * len(text_ls)
        assert len(box_facecolors) == len(
            text_ls
        ), "Number of colors provided is not equal to the number of text labels."
        if not font_size:
            font_size = self._default_font_size
        text_box_width = font_size + font_size // 2
        # If the texts does not fit in the assigned location,
        # we split the text and draw it in another place.
        if top_corner:
            num_text_split = self._align_y_top(
                box_coordinate, len(text_ls), text_box_width
            )
            y_corner = 1
        else:
            num_text_split = len(text_ls) - self._align_y_bottom(
                box_coordinate, len(text_ls), text_box_width
            )
            y_corner = 3

        text_color_sorted = sorted(
            zip(text_ls, box_facecolors), key=lambda x: x[0], reverse=True
        )
        if len(text_color_sorted) != 0:
            text_ls, box_facecolors = zip(*text_color_sorted)
        else:
            text_ls, box_facecolors = [], []
        text_ls, box_facecolors = list(text_ls), list(box_facecolors)
        self.draw_multiple_text_upward(
            text_ls[:num_text_split][::-1],
            box_coordinate,
            y_corner=y_corner,
            font_size=font_size,
            color=color,
            box_facecolors=box_facecolors[:num_text_split][::-1],
            alpha=alpha,
        )
        self.draw_multiple_text_downward(
            text_ls[num_text_split:],
            box_coordinate,
            y_corner=y_corner,
            font_size=font_size,
            color=color,
            box_facecolors=box_facecolors[num_text_split:],
            alpha=alpha,
        )

    def draw_multiple_text_upward(
        self,
        text_ls,
        box_coordinate,
        *,
        y_corner=1,
        font_size=None,
        color="w",
        box_facecolors="black",
        alpha=0.5,
    ):
        """
        Draw a list of text labels for some bounding box on the image in upward direction.
        The next text label will be on top of the previous one.
        Args:
            text_ls (list of strings): a list of text labels.
            box_coordinate (tensor): shape (4,). The (x_left, y_top, x_right, y_bottom)
                coordinates of the box.
            y_corner (int): Value of either 1 or 3. Indicate the index of the y-coordinate of
                the box to draw labels around.
            font_size (Optional[int]): font of the text. If not provided, a font size
                proportional to the image width is calculated and used.
            color (str): color of the text. Refer to `matplotlib.colors` for full list
                of formats that are accepted.
            box_facecolors (str or list of strs): colors of the box wrapped around the text. Refer to
                `matplotlib.colors` for full list of formats that are accepted.
            alpha (float): transparency level of the box.
        """
        if not isinstance(box_facecolors, list):
            box_facecolors = [box_facecolors] * len(text_ls)
        assert len(box_facecolors) == len(
            text_ls
        ), "Number of colors provided is not equal to the number of text labels."

        assert y_corner in [1, 3], "Y_corner must be either 1 or 3"
        if not font_size:
            font_size = self._default_font_size

        x, horizontal_alignment = self._align_x_coordinate(box_coordinate)
        y = box_coordinate[y_corner].item()
        for i, text in enumerate(text_ls):
            self.draw_text(
                text,
                (x, y),
                font_size=font_size,
                color=color,
                horizontal_alignment=horizontal_alignment,
                vertical_alignment="bottom",
                box_facecolor=box_facecolors[i],
                alpha=alpha,
            )
            y -= font_size + font_size // 2

    def draw_multiple_text_downward(
        self,
        text_ls,
        box_coordinate,
        *,
        y_corner=1,
        font_size=None,
        color="w",
        box_facecolors="black",
        alpha=0.5,
    ):
        """
        Draw a list of text labels for some bounding box on the image in downward direction.
        The next text label will be below the previous one.
        Args:
            text_ls (list of strings): a list of text labels.
            box_coordinate (tensor): shape (4,). The (x_left, y_top, x_right, y_bottom)
                coordinates of the box.
            y_corner (int): Value of either 1 or 3. Indicate the index of the y-coordinate of
                the box to draw labels around.
            font_size (Optional[int]): font of the text. If not provided, a font size
                proportional to the image width is calculated and used.
            color (str): color of the text. Refer to `matplotlib.colors` for full list
                of formats that are accepted.
            box_facecolors (str): colors of the box wrapped around the text. Refer to
                `matplotlib.colors` for full list of formats that are accepted.
            alpha (float): transparency level of the box.
        """
        if not isinstance(box_facecolors, list):
            box_facecolors = [box_facecolors] * len(text_ls)
        assert len(box_facecolors) == len(
            text_ls
        ), "Number of colors provided is not equal to the number of text labels."

        assert y_corner in [1, 3], "Y_corner must be either 1 or 3"
        if not font_size:
            font_size = self._default_font_size

        x, horizontal_alignment = self._align_x_coordinate(box_coordinate)
        y = box_coordinate[y_corner].item()
        for i, text in enumerate(text_ls):
            self.draw_text(
                text,
                (x, y),
                font_size=font_size,
                color=color,
                horizontal_alignment=horizontal_alignment,
                vertical_alignment="top",
                box_facecolor=box_facecolors[i],
                alpha=alpha,
            )
            y += font_size + font_size // 2

    def _align_x_coordinate(self, box_coordinate):
        """
        Choose an x-coordinate from the box to make sure the text label
        does not go out of frames. By default, the left x-coordinate is
        chosen and text is aligned left. If the box is too close to the
        right side of the image, then the right x-coordinate is chosen
        instead and the text is aligned right.
        Args:
            box_coordinate (array-like): shape (4,). The (x_left, y_top, x_right, y_bottom)
            coordinates of the box.
        Returns:
            x_coordinate (float): the chosen x-coordinate.
            alignment (str): whether to align left or right.
        """
        # If the x-coordinate is greater than 5/6 of the image width,
        # then we align test to the right of the box. This is
        # chosen by heuristics.
        if box_coordinate[0] > (self.output.width * 5) // 6:
            return box_coordinate[2], "right"

        return box_coordinate[0], "left"

    def _align_y_top(self, box_coordinate, num_text, textbox_width):
        """
        Calculate the number of text labels to plot on top of the box
        without going out of frames.
        Args:
            box_coordinate (array-like): shape (4,). The (x_left, y_top, x_right, y_bottom)
            coordinates of the box.
            num_text (int): the number of text labels to plot.
            textbox_width (float): the width of the box wrapped around text label.
        """
        dist_to_top = box_coordinate[1]
        num_text_top = dist_to_top // textbox_width

        if isinstance(num_text_top, torch.Tensor):
            num_text_top = int(num_text_top.item())

        return min(num_text, num_text_top)

    def _align_y_bottom(self, box_coordinate, num_text, textbox_width):
        """
        Calculate the number of text labels to plot at the bottom of the box
        without going out of frames.
        Args:
            box_coordinate (array-like): shape (4,). The (x_left, y_top, x_right, y_bottom)
            coordinates of the box.
            num_text (int): the number of text labels to plot.
            textbox_width (float): the width of the box wrapped around text label.
        """
        dist_to_bottom = self.output.height - box_coordinate[3]
        num_text_bottom = dist_to_bottom // textbox_width

        if isinstance(num_text_bottom, torch.Tensor):
            num_text_bottom = int(num_text_bottom.item())

        return min(num_text, num_text_bottom)


class VideoVisualizer(object):

    def __init__(
        self,
        num_classes,
        class_names_path,
        top_k=1,
        colormap="rainbow",
        thres=0.7,
        lower_thres=0.3,
        common_class_names=None,
        mode="top-k",
    ):
        """
        Args:
            num_classes (int): total number of classes.
            class_names_path (str): path to json file that maps class
                names to ids. Must be in the format '{classname: id}'.
            top_k (int): number of top predicted classes to plot.
            colormap (str): the colormap to choose color for class labels form.
                see https://matplotlib.org/tutorials/colors/colormaps.html
            thres (float): threshold for picking predicted classes to visualize.
            lower_thres (Optional[float]): If `common_class_names` is given,
                this `lower_thres` will be applied to uncommon classes and
                `thres` will be applied to classes in `common_class_names`.
            common_class_names (Optional[list of str(s)]): list of common class names
                to apply `thres`. Class names not included in `common_class_names` will
                have `lower_thres` as a threshold. If None, all classes will have
                `thres` as a threshold.
            mode (str): Supported modes are {"top-k", "thres"}. This is used for
                choosing predictions for visualization.
        """
        assert mode in ["top-k", "thres"], "Mode {} is not supported.".format(mode)
        self.mode = mode
        self.num_classes = num_classes
        self.class_names, _, _ = get_class_names(class_names_path)
        self.top_k = top_k
        self.thres = thres
        self.lower_thres = lower_thres

        if mode == "thres":
            self._get_thres_array(common_class_names=common_class_names)

        self.color_map = plt.get_cmap(colormap)

    def _get_color(self, class_id):
        """
        Get color for a class id.
        Args:
            class_id (int): class id.
        """
        return self.color_map(class_id / self.num_classes)[:3]

    def draw_one_frame(
        self,
        frame,
        preds,
        bboxes=None,
        alpha=0.5,
        text_alpha=0.7,
        ground_truth=False,
    ):
        """
        Draw labels and bounding boxes for one image. By default, predicted
        labels are drawn in the top left corner of the image or corresponding
        bounding boxes. For ground truth labels (setting True for ground_truth
        flag), labels will be drawn in the bottom left corner.
        Args:
            frame (array-like): a tensor or numpy array of shape (H, W, C),
                where H and W correspond to the height and width of the
                image respectively. C is the number of color channels. The
                image required to be in RGB format since that is a
                requirement of the Matplotlib library. The image is also
                expected to be in the range [0, 255].
            preds (tensor or list): If ground_truth is False, provide a float
                tensor of shape (num_boxes, num_classes) that contains all of
                the confidence scores of the model.
                For recognition task, input shape can be (num_classes,). To
                plot true label (ground_truth is True), preds is a list contains
                int32 of the shape (num_boxes, true_class_ids) or (true_class_ids,).
            bboxes (Optional[tensor]): shape (num_boxes, 4) that contains the
                coordinates of the bounding boxes.
            alpha (Optional[float]): transparency level of the bounding boxes.
            text_alpha (Optional[float]): transparency level of the box wrapped
                around text labels.
            ground_truth (bool): whether the prodived bounding boxes are ground-truth.
        """
        if isinstance(preds, torch.Tensor):
            if preds.ndim == 1:
                preds = preds.unsqueeze(0)
            n_instances = preds.shape[0]
        elif isinstance(preds, list):
            n_instances = len(preds)
        else:
            log.error("Unsupported type of prediction input.")
            return

        if ground_truth:
            top_scores, top_classes = [None] * n_instances, preds
        elif self.mode == "top-k":
            top_scores, top_classes = torch.topk(preds, k=self.top_k)
            top_scores, top_classes = top_scores.tolist(), top_classes.tolist()
        elif self.mode == "thres":
            top_scores, top_classes = [], []
            for pred in preds:
                mask = pred >= self.thres
                top_scores.append(pred[mask].tolist())
                top_class = torch.squeeze(torch.nonzero(mask), dim=-1).tolist()
                top_classes.append(top_class)

        # Create labels top k predicted classes with their scores.
        text_labels = []
        for i in range(n_instances):
            text_labels.append(
                _create_text_labels(
                    top_classes[i],
                    top_scores[i],
                    self.class_names,
                    ground_truth=ground_truth,
                )
            )
        frame_visualizer = ImgVisualizer(frame, meta=None)
        font_size = min(
            max(np.sqrt(frame.shape[0] * frame.shape[1]) // 35, 5), 9
        )
        top_corner = not ground_truth
        if bboxes is not None:
            assert len(preds) == len(
                bboxes
            ), "Encounter {} predictions and {} bounding boxes".format(
                len(preds), len(bboxes)
            )
            for i, box in enumerate(bboxes):
                text = text_labels[i]
                pred_class = top_classes[i]
                colors = [self._get_color(pred) for pred in pred_class]

                box_color = "r" if ground_truth else "g"
                line_style = "--" if ground_truth else "-."
                frame_visualizer.draw_box(
                    box,
                    alpha=alpha,
                    edge_color=box_color,
                    line_style=line_style,
                )
                frame_visualizer.draw_multiple_text(
                    text,
                    box,
                    top_corner=top_corner,
                    font_size=font_size,
                    box_facecolors=colors,
                    alpha=text_alpha,
                )
        else:
            text = text_labels[0]
            pred_class = top_classes[0]
            colors = [self._get_color(pred) for pred in pred_class]
            frame_visualizer.draw_multiple_text(
                text,
                torch.Tensor([0, 5, frame.shape[1], frame.shape[0] - 5]),
                top_corner=top_corner,
                font_size=font_size,
                box_facecolors=colors,
                alpha=text_alpha,
            )

        return frame_visualizer.output.get_image()

    def draw_clip_range(
        self,
        frames,
        preds,
        bboxes=None,
        text_alpha=0.5,
        ground_truth=False,
        keyframe_idx=None,
        draw_range=None,
        repeat_frame=1,
    ):
        """
        Draw predicted labels or ground truth classes to clip. Draw
        bouding boxes to clip if bboxes is provided. Boxes will
        gradually fade in and out the clip, centered around the clip's
        central frame, within the provided `draw_range`.
        Args:
            frames (array-like): video data in the shape (T, H, W, C).
            preds (tensor): a tensor of shape (num_boxes, num_classes)
                that contains all of the confidence scores of the model.
                For recognition task or for ground_truth labels, input
                shape can be (num_classes,).
            bboxes (Optional[tensor]): shape (num_boxes, 4) that
                contains the coordinates of the bounding boxes.
            text_alpha (float): transparency label of the box wrapped
                around text labels.
            ground_truth (bool): whether the prodived bounding boxes
                are ground-truth.
            keyframe_idx (int): the index of keyframe in the clip.
            draw_range (Optional[list[ints]): only draw frames in
                range [start_idx, end_idx] inclusively in the clip.
                If None, draw on the entire clip.
            repeat_frame (int): repeat each frame in draw_range for
                `repeat_frame` time for slow-motion effect.
        """
        if draw_range is None:
            draw_range = [0, len(frames) - 1]
        if draw_range is not None:
            draw_range[0] = max(0, draw_range[0])
            left_frames = frames[: draw_range[0]]
            right_frames = frames[draw_range[1] + 1:]
        draw_frames = frames[draw_range[0] : draw_range[1] + 1]
        if keyframe_idx is None:
            keyframe_idx = len(frames) // 2
        img_ls = (
            list(left_frames)
            + self.draw_clip(
                draw_frames,
                preds,
                bboxes=bboxes,
                text_alpha=text_alpha,
                ground_truth=ground_truth,
                keyframe_idx=keyframe_idx - draw_range[0],
                repeat_frame=repeat_frame,
            )
            + list(right_frames)
        )

        return img_ls

    def draw_clip(
        self,
        frames,
        preds,
        bboxes=None,
        text_alpha=0.5,
        ground_truth=False,
        keyframe_idx=None,
        repeat_frame=1,
    ):
        """
        Draw predicted labels or ground truth classes to clip. Draw
        bouding boxes to clip if bboxes is provided. Boxes will gradually
        fade in and out the clip, centered around the clip's central frame.
        Args:
            frames (array-like): video data in the shape (T, H, W, C).
            preds (tensor): a tensor of shape (num_boxes, num_classes)
                that contains all of the confidence scores of the model.
                For recognition task or for ground_truth labels, input
                shape can be (num_classes,).
            bboxes (Optional[tensor]): shape (num_boxes, 4) that contains
                the coordinates of the bounding boxes.
            text_alpha (float): transparency label of the box wrapped
                around text labels.
            ground_truth (bool): whether the prodived bounding boxes
                are ground-truth.
            keyframe_idx (int): the index of keyframe in the clip.
            repeat_frame (int): repeat each frame in draw_range
                for `repeat_frame` time for slow-motion effect.
        """
        assert repeat_frame >= 1, "`repeat_frame` must be a positive integer."
        repeated_seq = range(0, len(frames))
        repeated_seq = list(
            itertools.chain.from_iterable(
                itertools.repeat(x, repeat_frame) for x in repeated_seq
            )
        )
        frames, adjusted = self._adjust_frames_type(frames)
        if keyframe_idx is None:
            half_left = len(repeated_seq) // 2
            half_right = (len(repeated_seq) + 1) // 2
        else:
            mid = int((keyframe_idx / len(frames)) * len(repeated_seq))
            half_left = mid
            half_right = len(repeated_seq) - mid

        alpha_ls = np.concatenate(
            [
                np.linspace(0, 1, num=half_left),
                np.linspace(1, 0, num=half_right),
            ]
        )
        text_alpha = text_alpha
        frames = frames[repeated_seq]
        img_ls = []
        for alpha, frame in zip(alpha_ls, frames):
            draw_img = self.draw_one_frame(
                frame,
                preds,
                bboxes,
                alpha=alpha,
                text_alpha=text_alpha,
                ground_truth=ground_truth,
            )
            if adjusted:
                draw_img = draw_img.astype("float32") / 255

            img_ls.append(draw_img)

        return img_ls

    def _adjust_frames_type(self, frames):
        """
        Modify video data to have dtype of uint8 and values range in [0, 255].
        Args:
            frames (array-like): 4D array of shape (T, H, W, C).
        Returns:
            frames (list of frames): list of frames in range [0, 1].
            adjusted (bool): whether the original frames need adjusted.
        """
        assert (
            frames is not None and len(frames) != 0
        ), "Frames does not contain any values"
        frames = np.array(frames)
        assert np.array(frames).ndim == 4, "Frames must have 4 dimensions"
        adjusted = False
        if frames.dtype in [np.float32, np.float64]:
            frames *= 255
            frames = frames.astype(np.uint8)
            adjusted = True

        return frames, adjusted

    def _get_thres_array(self, common_class_names=None):
        """
        Compute a thresholds array for all classes based on `self.thes` and `self.lower_thres`.
        Args:
            common_class_names (Optional[list of strs]): a list of common class names.
        """
        common_class_ids = []
        if common_class_names is not None:
            common_classes = set(common_class_names)

            for i, name in enumerate(self.class_names):
                if name in common_classes:
                    common_class_ids.append(i)
        else:
            common_class_ids = list(range(self.num_classes))

        thres_array = np.full(
            shape=(self.num_classes,), fill_value=self.lower_thres
        )
        thres_array[common_class_ids] = self.thres
        self.thres = torch.from_numpy(thres_array)


def _create_text_labels(classes, scores, class_names, is_crowd=None):
    """
    Args:
        classes (list[int] or None):
        scores (list[float] or None):
        class_names (list[str] or None):
        is_crowd (list[bool] or None):
    Returns:
        list[str] or None
    """
    labels = None
    if classes is not None:
        if class_names is not None and len(class_names) > 0:
            labels = [class_names[i] for i in classes]
        else:
            labels = [str(i) for i in classes]
    if scores is not None:
        if labels is None:
            labels = ["{:.0f}%".format(s * 100) for s in scores]
        else:
            labels = ["{} {:.0f}%".format(l, s * 100) for l, s in zip(labels, scores)]
    if labels is not None and is_crowd is not None:
        labels = [l + ("|crowd" if crowd else "") for l, crowd in zip(labels, is_crowd)]
    return labels


def _create_text_labels(classes, scores, class_names, ground_truth=False):
    """
    Create text labels.
    Args:
        classes (list[int]): a list of class ids for each example.
        scores (list[float] or None): list of scores for each example.
        class_names (list[str]): a list of class names, ordered by their ids.
        ground_truth (bool): whether the labels are ground truth.
    Returns:
        labels (list[str]): formatted text labels.
    """
    try:
        labels = [class_names[i] for i in classes]
    except IndexError:
        logger.error("Class indices get out of range: {}".format(classes))
        return None

    if ground_truth:
        labels = ["[{}] {}".format("GT", label) for label in labels]
    elif scores is not None:
        assert len(classes) == len(scores)
        labels = [
            "[{:.2f}] {}".format(s, label) for s, label in zip(scores, labels)
        ]
    return labels




















