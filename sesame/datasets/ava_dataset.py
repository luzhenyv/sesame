import os
import numpy as np
import torch
import sesame.utils.logger as logger

from collections import defaultdict
from . import cv2_transform
from . import transform
from . import utils

log = logger.getLogger(__name__)

FPS = 30
AVA_VALID_FRAMES = range(902, 1799)


def load_image_lists(cfg, is_train):
    """
    Loading image paths from corresponding files.

    Args:
        cfg (CfgNode): config
        is_train (bool): if it is training dataset or not

    Returns:
        image_paths(list[list]): a list of items. Each item (also a list)
                                corresponds to one video and contains the
                                paths of images for this video.
        video_idx_to_name (list): a list which stores video names
    """
    list_filenames = [
        os.path.join(cfg.AVA.FRAME_LIST_DIR, filename)
        for filename in (cfg.AVA.TRAIN_LISTS if is_train else cfg.AVA.TEST_LISTS)
    ]
    image_paths = defaultdict(list)
    video_name_to_idx = {}
    video_idx_to_name = []
    for list_filename in list_filenames:
        with open(list_filename, "r") as f:
            for line in f.read().splitlines():
                row = line.split()
                # The format of each row should follow:
                # original_video_id video_id frame_id path labels
                assert len(row) == 5
                video_name = row[0]

                if video_name not in video_name_to_idx:
                    idx = len(video_name_to_idx)
                    video_name_to_idx[video_name] = idx
                    video_idx_to_name.append(video_name)

                data_key = video_name_to_idx[video_name]

                image_paths[data_key].append(os.path.join(cfg.AVA.FRAME_DIR, row[3]))

    image_paths = [image_paths[i] for i in range(len(image_paths))]

    log.info("Finished loading image paths from: {}".format(", ".join(list_filenames)))
    return image_paths, video_idx_to_name


def load_boxes_and_labels(cfg, mode):
    """
    Loading boxes and labels from csv files.

    Args:
        cfg (CfgNode): config.
        mode (str): 'train', 'val' or 'test' mode.

    Returns:
        all_boxes (dict): a dict which maps from 'video_name' and
                        'frame_sec' to a list of 'box'. Each 'box'
                        is a ['box_coord', 'box_labels'] where 'box_coord'
                        is the coordinates of box and 'box_labels' are the
                        corresponding labels for the box.
    """
    gt_lists = cfg.AVA.TRAIN_GT_BOX_LISTS if mode == "train" else []
    pred_lists = cfg.AVA.TRAIN_PREDICT_BOX_LISTS if mode == "train" else cfg.AVA.TEST_PREDICT_BOX_LISTS
    ann_filenames = [os.path.join(cfg.AVA.ANNOTATION_DIR, filename) for filename in gt_lists + pred_lists]
    ann_is_gt_box = [True] * len(gt_lists) + [False] * len(pred_lists)

    detect_thresh = cfg.AVA.DETECTION_SCORE_THRESH
    # Only select frame_sec % 4 = 0 samples for validation if not set FULL_TEST_ON_VAL
    boxes_sample_rate = 4 if mode == "val" and not cfg.AVA.FULL_TEST_ON_VAL else 1
    all_boxes, count, unique_box_count = parse_bboxes_file(
        ann_filenames=ann_filenames,
        ann_is_gt_box=ann_is_gt_box,
        detect_thresh=detect_thresh,
        boxes_sample_rate=boxes_sample_rate,
    )
    log.info("Finished loading annotations from: %s".format(", ".join(ann_filenames)))
    log.info("Detection threshold: {}".format(detect_thresh))
    log.info("Number of unique boxes: {}".format(unique_box_count))
    log.info("Number of annotations: {}".format(count))

    return all_boxes


def get_keyframe_data(boxes_and_labels):
    """
    Getting keyframe indices, boxes and labels in the dataset.

    Args:
        boxes_and_labels(list[dict]): a list which maps from video_idx to a dict.
                                    Each dict 'frame_sec' to a list of boxes and
                                    corresponding labels.

    Returns:
        keyframe_indices (list): a list of indices of the keyframes.
        keyframe_boxes_and_labels (list[list[list]]): a list of list which maps
                                from video_idx and sec_idx to a list of boxes and
                                corresponding labels.
    """

    def sec_to_frame(sec):
        """
        Convert time index (in second) to frame index.
        0: 900
        30: 901
        """
        return (sec - 900) * FPS

    keyframe_indices = []
    keyframe_box_and_labels = []
    count = 0
    for video_idx in range(len(boxes_and_labels)):
        sec_idx = 0
        keyframe_box_and_labels.append([])
        for sec in boxes_and_labels[video_idx].keys():
            if sec not in AVA_VALID_FRAMES:
                continue

            if len(boxes_and_labels[video_idx][sec]) > 0:
                keyframe_indices.append(
                    (video_idx, sec_idx, sec, sec_to_frame(sec))
                )
                keyframe_box_and_labels[video_idx].append(
                    boxes_and_labels[video_idx][sec]
                )
                sec_idx += 1
                count += 1
    log.info("{} keyframes used.".format(count))
    return keyframe_indices, keyframe_box_and_labels


def get_num_boxes_used(keyframe_indices, keyframe_boxes_and_labels):
    """
    Get total number of used boxes.

    Args:
        keyframe_indices (list): a list of indices of the keyframes.
        keyframe_boxes_and_labels (list[list[list]]): a list of list which maps
                                from video_idx and sec_idx to a list of boxes
                                and corresponding labels.

    Returns:
        count (int): total number of used boxes.
    """

    count = 0
    for video_idx, sec_idx, _, _ in keyframe_indices:
        count += len(keyframe_boxes_and_labels[video_idx][sec_idx])
    return count


def parse_bboxes_file(ann_filenames, ann_is_gt_box, detect_thresh, boxes_sample_rate=1):
    """
    Parse AVA bounding boxes files.

    Args:
        ann_filenames (list of str(s)): a list of AVA bounding boxes annotation files.
        ann_is_gt_box (list of bools): a list of boolean to indicate whether the
                                    corresponding ann_file is ground-truth. 'ann_is_gt_box[i]'
                                    correspond to `ann_filenames[i]`.
        detect_thresh (float): threshold for accepting predicted boxes, range [0, 1].
        boxes_sample_rate (int): sample rate for test bounding boxes. Get 1 every `boxes_sample_rate`.
    """
    all_boxes = {}
    count = 0
    unique_box_count = 0
    for filename, is_gt_box in zip(ann_filenames, ann_is_gt_box):
        with open(filename, "r") as f:
            for line in f:
                row = line.strip().split(",")
                # When we use predicted boxes to train/eval, we need to
                # ignore the boxes whose score are below the threshold.
                if not is_gt_box:
                    score = float(row[7])
                    if score < detect_thresh:
                        continue

                video_name, frame_sec = row[0], int(row[1])
                if frame_sec % boxes_sample_rate != 0:
                    continue

                # Box with format [x1, y1, x2, y2] with a range of [0, 1] as float.
                box_key = ",".join(row[2:6])
                box = list(map(float, row[2:6]))
                label = -1 if row[6] == "" else int(row[6])

                if video_name not in all_boxes:
                    all_boxes[video_name] = {}
                    for sec in AVA_VALID_FRAMES:
                        all_boxes[video_name][sec] = {}

                if box_key not in all_boxes[video_name][frame_sec]:
                    all_boxes[video_name][frame_sec][box_key] = [box, []]
                    unique_box_count += 1

                all_boxes[video_name][frame_sec][box_key][1].append(label)
                if label != -1:
                    count += 1

    for video_name in all_boxes.keys():
        for frame_sec in all_boxes[video_name].keys():
            # Save in format of a list of [box_i, box_i_labels].
            all_boxes[video_name][frame_sec] = list(
                all_boxes[video_name][frame_sec].values()
            )

    return all_boxes, count, unique_box_count


class Ava(torch.utils.data.Dataset):
    """
    AVA Dataset
    """

    def __init__(self, cfg, split):
        self.cfg = cfg
        self._split = split
        self._sample_rate = cfg.DATA.SAMPLING_RATE
        self._video_length = cfg.DATA.NUM_FRAMES
        self._seq_len = self._video_length * self._sample_rate
        self._num_classes = cfg.MODEL.NUM_CLASSES
        # Augmentation params
        self._data_mean = cfg.DATA.MEAN
        self._data_std = cfg.DATA.STD
        self._use_bgr = cfg.AVA.BGR
        self.random_horizontal_flip = cfg.DATA.RANDOM_FLIP
        if self._split == "train":
            self._crop_size = cfg.DATA.TRAIN_CROP_SIZE
            self._jitter_min_scale = cfg.DATA.TRAIN_JITTER_SCALES[0]
            self._jitter_max_scale = cfg.DATA.TRAIN_JITTER_SCALES[1]
            self._use_color_augmentation = cfg.AVA.TRAIN_USE_COLOR_AUGMENTATION
            self._pca_jitter_only = cfg.AVA.TRAIN_PCA_JITTER_ONLY
            self._pca_eigval = cfg.DATA.TRAIN_PCA_EIGVAL
            self._pca_eigvec = cfg.DATA.TRAIN_PCA_EIGVEC
        else:
            self._crop_size = cfg.DATA.TEST_CROP_SIZE
            self._test_force_flip = cfg.AVA.TEST_FORCE_FLIP

        self._load_data(cfg)

    def _load_data(self, cfg):
        """
        Load frame paths and annotations from files
        Args:
            cfg(CfgNode): config
        """
        # Loading frame paths
        (
            self._image_paths,
            self._video_idx_to_name
        ) = load_image_lists(cfg, is_train=(self._split == "train"))

        # Loading annotations for boxes and labels
        boxes_and_labels = load_boxes_and_labels(cfg, mode=self._split)

        assert len(boxes_and_labels) == len(self._image_paths)

        boxes_and_labels = [
            boxes_and_labels[self._video_idx_to_name[i]]
            for i in range(len(self._image_paths))
        ]

        # Get indices of keyframes and corresponding boxes anf labels.
        (
            self._keyframe_indices,
            self._keyframe_boxes_and_labels,
        ) = get_keyframe_data(boxes_and_labels)

        # Calculate the number of used boxes.
        self._num_boxes_used = get_num_boxes_used(
            self._keyframe_indices, self._keyframe_boxes_and_labels
        )

        self.print_summary()

    def print_summary(self):
        log.info("=== AVA dataset summary ===")
        log.info("Split: {}".format(self._split))
        log.info("Number of video: {}".format(len(self._image_paths)))
        total_frames = sum(
            len(video_img_paths) for video_img_paths in self._image_paths
        )
        log.info("Number of frames: {}".format(total_frames))
        log.info("Number of key frames: {}".format(len(self)))
        log.info("Number of boxes: {}.".format(self._num_boxes_used))

    def __len__(self):
        """
        Returns:
            (int): the number of videos in the dataset
        """
        return self.num_videos

    @property
    def num_videos(self):
        """
        Returns:
            (int): the number of videos in the dataset.
        """
        return len(self._keyframe_indices)

    def _images_and_boxes_preprocessing_cv2(self, images, boxes):
        """
        This function performs preprocessing for the input images and
        corresponding boxes for one clip with opencv as backend.

        Args:
            images (tensor): the images.
            boxes (ndarray): the boxes for the current clip.

        Returns:
            images (tensor): list of preprocessed images.
            boxes (ndarray): preprocessed boxes.
        """

        height, width, _ = images[0].shape

        boxes[:, [0, 2]] *= width
        boxes[:, [1, 3]] *= height
        boxes = cv2_transform.clip_boxes_to_image(boxes, height, width)

        # `transform.py` is list of np.array. However, for AVA, we only have
        # one np.array.
        boxes = [boxes]

        # The image now is in HWC, BGR format.
        if self._split == "train":
            images, boxes = cv2_transform.random_short_side_scale_jitter_list(
                images,
                min_size=self._jitter_min_scale,
                max_size=self._jitter_max_scale,
                boxes=boxes,
            )
            images, boxes = cv2_transform.random_crop_list(
                images, self._crop_size, order="HWC", boxes=boxes
            )

            if self.random_horizontal_flip:
                # random flip
                images, boxes = cv2_transform.horizontal_flip_list(
                    0.5, images, order="HWC", boxes=boxes
                )
        elif self._split == "val":
            # Short side to test_scale. Non-local and STRG uses 256.
            images = [
                cv2_transform.scale(self._crop_size, image) for image in images
            ]
            boxes = [
                cv2_transform.scale_boxes(self._crop_size, boxes[0], height, width)
            ]
            images, boxes = cv2_transform.spatial_shift_crop_list(
                self._crop_size, images, 1, order="HWC", boxes=boxes
            )
            if self._test_force_flip:
                images, boxes = cv2_transform.horizontal_flip_list(
                    1, images, order="HWC", boxes=boxes
                )
        elif self._split == "test":
            # Short side to test_scale. Non-local and STRG uses 256.
            images = [
                cv2_transform.scale(self._crop_size, image) for image in images
            ]
            boxes = [
                cv2_transform.scale_boxes(self._crop_size, boxes[0], height, width)
            ]
            if self._test_force_flip:
                images, boxes = cv2_transform.horizontal_flip_list(
                    1, images, order="HWC", boxes=boxes
                )
        else:
            raise NotImplementedError(
                "Unsupported split mode {}".format(self._split)
            )

        # Convert image to CHW keeping BGR order.
        images = [cv2_transform.HWC2CHW(image) for image in images]

        # Image [0, 255] -> [0, 1]
        images = [image / 255.0 for image in images]

        # Reshape image to (3, self._crop_size, self._crop_size)
        images = [
            np.ascontiguousarray(
                np.reshape(
                    image,
                    (3, images[0].shape[1], images[0].shape[2]),
                    # (3, self._crop_size, self._crop_size),
                )
            )
            for image in images
        ]

        # Do color augmentation
        if self._split == "train" and self._use_color_augmentation:
            if not self._pca_jitter_only:
                images = cv2_transform.color_jitter_list(
                    images,
                    brightness=0.4,
                    contrast=0.4,
                    saturation=0.4,
                )

            images = cv2_transform.lighting_list(
                images,
                alphastd=0.1,
                eigval=np.array(self._pca_eigval).astype(np.float32),
                eigvec=np.array(self._pca_eigvec).astype(np.float32),
            )

        # Normalize images by mean and std.
        images = [
            cv2_transform.color_normalization(
                image,
                np.array(self._data_mean, dtype=np.float32),
                np.array(self._data_std, dtype=np.float32),
            )
            for image in images
        ]

        # Concat list of images to single ndarray.
        # add frame axis
        images = np.concatenate(
            [np.expand_dims(image, axis=1) for image in images], axis=1
        )

        if not self._use_bgr:
            # Convert image format from BGR to RGB.
            images = images[::-1, ...]

        images = np.ascontiguousarray(images)
        images = torch.from_numpy(images)
        boxes = cv2_transform.clip_boxes_to_image(
            boxes[0], images[0].shape[1], images[0].shape[2]
        )
        return images, boxes

    def _images_and_boxes_preprocessing(self, images, boxes):
        """
        This function performs preprocessing for the input images and
        corresponding boxes for one clip.
        Args:
            images (tensor): the images.
            boxes (ndarray): the boxes for the current clip.
        Returns:
            images (tensor): list of preprocessed images.
            boxes (ndarray): preprocessed boxes.
        """
        # Image [0, 255] -> [0, 1].
        images = images.float()
        images = images / 255.0

        height, width = images.shape[2], images.shape[3]
        # The format of boxes is [x1, y1, x2, y2]. The input boxes are in the
        # range of [0, 1].
        boxes[:, [0, 2]] *= width
        boxes[:, [1, 3]] *= height
        boxes = transform.clip_boxes_to_image(boxes, height, width)

        if self._split == "train":
            # Train split
            images, boxes = transform.random_short_side_scale_jitter(
                images,
                min_size=self._jitter_min_scale,
                max_size=self._jitter_max_scale,
                boxes=boxes,
            )
            images, boxes = transform.random_crop(
                images, self._crop_size, boxes=boxes
            )

            # Random flip.
            images, boxes = transform.horizontal_flip(0.5, images, boxes=boxes)
        elif self._split == "val":
            # Val split
            # Resize short side to crop_size. Non-local and STRG uses 256.
            images, boxes = transform.random_short_side_scale_jitter(
                images,
                min_size=self._crop_size,
                max_size=self._crop_size,
                boxes=boxes,
            )

            # Apply center crop for val split
            images, boxes = transform.uniform_crop(
                images, size=self._crop_size, spatial_idx=1, boxes=boxes
            )

            if self._test_force_flip:
                images, boxes = transform.horizontal_flip(1, images, boxes=boxes)
        elif self._split == "test":
            # Test split
            # Resize short side to crop_size. Non-local and STRG uses 256.
            images, boxes = transform.random_short_side_scale_jitter(
                images,
                min_size=self._crop_size,
                max_size=self._crop_size,
                boxes=boxes,
            )

            if self._test_force_flip:
                images, boxes = transform.horizontal_flip(1, images, boxes=boxes)
        else:
            raise NotImplementedError(
                "{} split not supported yet!".format(self._split)
            )

        # Do color augmentation (after divided by 255.0).
        if self._split == "train" and self._use_color_augmentation:
            if not self._pca_jitter_only:
                images = transform.color_jitter(
                    images,
                    img_brightness=0.4,
                    img_contrast=0.4,
                    img_saturation=0.4,
                )

            images = transform.lighting_jitter(
                images,
                alphastd=0.1,
                eigval=np.array(self._pca_eigval).astype(np.float32),
                eigvec=np.array(self._pca_eigvec).astype(np.float32),
            )

        # Normalize images by mean and std.
        images = transform.color_normalization(
            images,
            np.array(self._data_mean, dtype=np.float32),
            np.array(self._data_std, dtype=np.float32),
        )

        if not self._use_bgr:
            # Convert image format from BGR to RGB.
            # Note that Kinetics pre-training uses RGB!
            images = images[:, [2, 1, 0], ...]

        boxes = transform.clip_boxes_to_image(
            boxes, self._crop_size, self._crop_size
        )

        return images, boxes

    def __getitem__(self, idx):
        """
        Generate corresponding clips, boxes labels and metadata for given idx.

        Args:
            idx (int): the video index provided by the pytorch sampler.
        Returns:
            frames (tensor):  the frames of sampled from the video. The dimension
                            is `channel` x `num frames` x `height` x `width`.
            label (ndarray): the label for correspond boxes for the current video
            idx (int): the video index provided by the pytorch sampler.
            extra_data (dict): a dict containing extra data fields, like "boxes",
                                "ori_boxes" and "metadata".
        """
        video_idx, sec_idx, sec, center_idx = self._keyframe_indices[idx]
        # Get the frame idxs for current clip.
        seq = utils.get_sequence(
            center_idx,
            self._seq_len // 2,
            self._sample_rate,
            num_frames=len(self._image_paths[video_idx]),
        )

        clip_label_list = self._keyframe_boxes_and_labels[video_idx][sec_idx]
        assert len(clip_label_list) > 0

        # Get boxes and labels for current clip.
        boxes = []
        labels = []
        for box_labels in clip_label_list:
            boxes.append(box_labels[0])
            labels.append(box_labels[1])
        boxes = np.array(boxes)

        # Score is not used.
        boxes = boxes[:, :4].copy()
        ori_boxes = boxes.copy()

        # Load images of current clip.
        image_paths = [self._image_paths[video_idx][frame] for frame in seq]
        images = utils.retry_load_images(
            image_paths, backend=self.cfg.AVA.IMG_PROC_BACKEND
        )

        if self.cfg.AVA.IMG_PROC_BACKEND == "pytorch":
            # T H W C -> T C H W.
            images = images.permute(0, 3, 1, 2)
            # Preprocess images and boxes.
            images, boxes = self._images_and_boxes_preprocessing(images, boxes)
            # T C H W -> C T H W.
            images = images.permute(1, 0, 2, 3)
        else:
            # Preprocess images and boxes
            images, boxes = self._images_and_boxes_preprocessing_cv2(images, boxes)

        # Construct label arrays.
        label_arrs = np.zeros((len(labels), self._num_classes), dtype=np.int32)
        for i, box_labels in enumerate(labels):
            # AVA label index starts from 1.
            for label in boxes:
                if label == -1:
                    continue
                assert 1 <= label <= 80
                label_arrs[i][label - 1] = 1

        images = utils.pack_pathway_output(self.cfg, images)
        metadata = [[video_idx, sec]] * len(boxes)

        extra_data = {
            "boxes": boxes,
            "ori_boxes": ori_boxes,
            "metadata": metadata,
        }

        return images, label_arrs, idx, extra_data
















