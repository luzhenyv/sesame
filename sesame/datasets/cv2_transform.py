import math
import numpy as np
import cv2


def clip_boxes_to_image(boxes, height, width):
    """
    Clip the boxes with the height and width of the image size.
    Args:
        boxes (ndarray): bounding boxes to perform crop. The
                        dimension is 'num boxes' x 4.
        height (int): the height of the image.
        width (int): the width of the image.
    Returns:
        boxes (ndarray): cropped bounding boxes.
    """
    boxes[:, [0, 2]] = np.minimum(
        width - 1.0, np.maximum(0.0, boxes[:, [0, 2]])
    )
    boxes[:, [1, 3]] = np.minimum(
        height - 1.0, np.maximum(0.0, boxes[:, [1, 3]])
    )
    return boxes


def horizontal_flip_list(prob, images, order="CHW", boxes=None):
    """
    Horizontally flip the list of image and optional boxes.
    Args:
        prob (float): probability to flip.
        images (list): a list of images to perform short side scale.
                        Dimension is `height` x `width` x `channel`
                        or `channel` x `height` x `width`.
        order (str): order of the `height`, `channel` and `width`.
        boxes (list): optional. Corresponding boxes to images.
                        Dimension is `num boxes` x 4.
    Returns:
        (ndarray): the scaled image with dimension of `height` x `width` x `channel`.
        (list): optional. Corresponding boxes to images. Dimension is `num boxes` x 4.
    """

    assert order in ["CHW", "HWC"], "order {} is not supported".format(order)

    _, width, _ = images[0].shape
    if np.random.uniform() < prob:
        if boxes is not None:
            boxes = [flip_boxes(proposal, width) for proposal in boxes]
        if order == "CHW":
            out_images = []
            for image in images:
                image = np.asarray(image).swapaxes(2, 0)
                image = image[::-1]
                out_images.append(image.swapaxes(0, 2))
            return out_images, boxes
        elif order == "HWC":
            return [cv2.flip(image, 1) for image in images], boxes
    return images, boxes


def random_short_side_scale_jitter_list(images, min_size, max_size, boxes=None):
    """
    Perform a spatial short scale jittering on the given images and
    corresponding boxes.
    Args:
        images (list): list of images to perform scale jitter. Dimension is
                        'height' x 'width' x 'channel'.
        min_size (int): the minimal size to scale the frames.
        max_size (int): the maximal size to scale the frames.
        boxes (list): optional. Corresponding boxes to images. Dimension is
                        'num boxes' x 4
    Returns:
        (list): the list of scaled images with dimension of
                `new height` x `new width` x `channel`.
        (ndarray or None): the scaled boxes with dimension of
                `num boxes` x 4.
    """
    size = int(round(1.0 / np.random.uniform(1.0 / max_size, 1.0 / min_size)))
    height = images[0].shape[0]
    width = images[0].shape[1]
    if (width <= height and width == size) or (height <= width and height == size):
        return images, boxes
    new_width = size
    new_height = size
    if width < height:
        new_height = int(math.floor((float(height) / width) * size))
        if boxes is not None:
            boxes = [proposal * float(new_height) / height for proposal in boxes]
    else:
        new_width = int(math.floor((float(width) / height) * size))
        if boxes is not None:
            boxes = [proposal * float(new_width) / width for proposal in boxes]
    return (
        [
            cv2.resize(
                image, (new_width, new_height), interpolation=cv2.INTER_LINEAR
            ).astype(np.float32)
            for image in images
        ],
        boxes,
    )


def random_crop_list(images, size, pad_size=0, order="CHW", boxes=None):
    """
    Perform random crop on a list of images.
    Args:
        images (list): list of images to perform random crop.
        size (int): size to crop.
        pad_size (int): padding size.
        order (string): order of the 'height', 'width' and 'channel'.
        boxes (list): optional. Corresponding boxes to images.
                    Dimension is 'num boxes' x 4.
    Returns:
        cropped (ndarray): the cropped list of images with dimension of
                        'height' x 'width' x 'channel'.
        boxes (list): optional. Corresponding boxes to images. Dimension
                        is 'num boxes' x 4.
    """

    assert order in ["CHW", "HWC"], "order {} is not supported".format(order)

    # explicitly dealing processing per image order to avoid flipping images.
    if pad_size > 0:
        images = [
            pad_image(pad_size=pad_size, image=image, order=order)
            for image in images
        ]

    # image format should be CHW.
    if order == "CHW":
        if images[0].shape[1] == size and images[0].shape[2] == size:
            return images, boxes
        height = images[0].shape[1]
        width = images[0].shape[2]
        y_offset = 0
        if height > size:
            y_offset = int(np.random.randint(0, height - size))
        x_offset = 0
        if width > size:
            x_offset = int(np.random.randint(0, width - size))
        cropped = [
            image[:, y_offset: y_offset + size, x_offset: x_offset + size]
            for image in images
        ]
        assert cropped[0].shape[1] == size, "Image not cropped properly"
        assert cropped[0].shape[2] == size, "Image not cropped properly"
    elif order == "HWC":
        if images[0].shape[1] == size and images[0].shape[2] == size:
            return images, boxes
        height = images[0].shape[0]
        width = images[0].shape[1]
        y_offset = 0
        if height > size:
            y_offset = int(np.random.randint(0, height - size))
        x_offset = 0
        if width > size:
            x_offset = int(np.random.randint(0, width - size))
        cropped = [
            image[y_offset: y_offset + size, x_offset: x_offset + size, :]
            for image in images
        ]
        assert cropped[0].shape[1] == size, "Image not cropped properly"
        assert cropped[0].shape[2] == size, "Image not cropped properly"
    else:
        raise NotImplementedError("Unknown order {}".format(order))

    if boxes is not None:
        boxes = [crop_boxes(proposal, x_offset, y_offset) for proposal in boxes]

    return cropped, boxes


def spatial_shift_crop_list(size, images, spatial_shift_pos, order="CHW", boxes=None):
    """
    Perform left, center or right crop of the given list of images.
    Args:
        size (int): size to crop.
        images (list): a list of images to perform short side scale.
                        Dimension is `height` x `width` x `channel`
                        or `channel` x `height` x `width`.
        spatial_shift_pos (int): option includes 0 (left), 1 (middle)
                        and 2 (right) crop
        order (String): order of the 'height', 'channel' and 'width'.
        boxes (list): optional. Corresponding boxes to images. Dimension
                        is 'num boxes' x 4
    Returns:
        cropped (ndarray): the cropped list of images with dimension of
                        'height' x 'width' x 'channel'
        boxes (list): optional. Corresponding boxes to images. Dimension is
                        'num boxes' x 4
    """
    assert spatial_shift_pos in [0, 1, 2]
    assert order in ["CHW", "HWC"], "order {} is not supported".format(order)

    height = images[0].shape[0]
    width = images[0].shape[1]
    y_offset = int(math.ceil((height - size) / 2))
    x_offset = int(math.ceil((width - size) / 2))

    if height > width:
        if spatial_shift_pos == 0:
            y_offset = 0
        elif spatial_shift_pos == 2:
            y_offset = height - size
    else:
        if spatial_shift_pos == 0:
            x_offset = 0
        elif spatial_shift_pos == 2:
            x_offset = width - size

    if order == "CHW":
        cropped = [
            image[:, y_offset: y_offset + size, x_offset: x_offset + size]
            for image in images
        ]
    elif order == "HWC":
        cropped = [
            image[y_offset: y_offset + size, x_offset: x_offset + size, :]
            for image in images
        ]
    else:
        raise NotImplementedError("Unknown order {}".format(order))

    if boxes is not None:
        for i in range(len(boxes)):
            boxes[i][:, [0, 2]] -= x_offset
            boxes[i][:, [1, 3]] -= y_offset

    return cropped, boxes


def pad_image(image, pad_size, order="CHW"):
    """
    Pad the given image with the size of pad_size.
    Args:
        image (array): image to pad.
        pad_size (int): size to pad.
        order (String): order of the 'height', 'channel' and 'width'.
    Returns:
        img (array): padded image.
    """
    assert order in ["CHW", "HWC"], "order {} is not supported".format(order)
    if order == "CHW":
        img = np.pad(
            image, ((0, 0), (pad_size, pad_size), (pad_size, pad_size)),
            mode=str("constant"),
        )
    elif order == "HWC":
        img = np.pad(
            image, ((pad_size, pad_size), (pad_size, pad_size), (0, 0)),
            mode=str("constant"),
        )
    else:
        raise NotImplementedError("Unknown order {}".format(order))
    return img


def scale(size, image):
    """
    Scale the short side of the image to size.
    Args:
        size (int): size to scale the image.
        image (array): image to perform short side scale. Dimension is
                     `height` x `width` x `channel`.
    Returns:
          (ndarray): the scaled image with dimension of
                     `height` x `width` x `channel`.
    """
    height = image.shape[0]
    width = image.shape[1]
    if (width <= height and width == size) or (height <= width and height == size):
        return image
    new_width = size
    new_height = size
    if width < height:
        new_height = int(math.floor((float(height) / width) * size))
    else:
        new_width = int(math.floor((float(width) / height) * size))
    image = cv2.resize(
        image, (new_width, new_height), interpolation=cv2.INTER_LINEAR
    )
    return image.astype(np.float32)


def crop_boxes(boxes, x_offset, y_offset):
    """
    Crop the boxes given the offsets.
    Args:
        boxes (array): boxes to crop.
        x_offset (int): offset on x.
        y_offset (int): offset on y.
    """
    boxes[:, [0, 2]] = boxes[:, [0, 2]] - x_offset
    boxes[:, [1, 3]] = boxes[:, [1, 3]] - y_offset
    return boxes


def flip_boxes(boxes, im_width):
    """
    Horizontally flip the boxes.
    Args:
        boxes (array): box to flip.
        im_width (int): width of the image.
    Returns:
        boxes_flipped (array): flipped box.
    """

    boxes_flipped = boxes.copy()
    boxes_flipped[:, 0::4] = im_width - boxes[:, 2::4] - 1
    boxes_flipped[:, 2::4] = im_width - boxes[:, 0::4] - 1
    return boxes_flipped


def scale_boxes(size, boxes, height, width):
    """
    Scale the short side of the box to size.
    Args:
        size (int): size to scale the image.
        boxes (ndarray): bounding boxes to peform scale. The dimension is
        `               num boxes` x 4.
        height (int): the height of the image.
        width (int): the width of the image.
    Returns:
        boxes (ndarray): scaled bounding boxes.
    """

    if (width <= height and width == size) or (height <= width and height == size):
        return boxes

    new_width = size
    new_height = size
    if width < height:
        new_height = int(math.floor((float(height) / width) * size))
        boxes *= float(new_height) / height
    else:
        new_width = int(math.floor((float(width) / height) * size))
        boxes *= float(new_width) / width
    return boxes


def CHW2HWC(image):
    """
    Transpose the dimension from `channel` x `height` x `width` to
    `height` x `width` x `channel`.
    Args:
        image (ndarray): image to transpose.
    Returns:
        (array): transposed image.
    """
    return np.transpose(image, (1, 2, 0))


def HWC2CHW(image):
    """
    Transpose the dimension from `height` x `width` x `channel` to
        `channel` x `height` x `width`.
    Args:
        image (ndarray): image to transpose.
    Returns
        (array): transposed image.
    """
    return np.transpose(image, (2, 0, 1))


def color_jitter_list(images, brightness=0., contrast=0., saturation=0.):
    """
    Perform color jitter on the list of images.
    Args:
        images (list): list of images to perform color jitter.
        brightness (float): jitter ratio for brightness.
        contrast (float):jitter ratio for contrast.
        saturation (float): jitter ratio for saturation.
    Returns:
        images (list): the jittered list of images.
    """
    jitter = []
    if brightness != 0:
        jitter.append("brightness")
    if contrast != 0:
        jitter.append("contrast")
    if saturation != 0:
        jitter.append("saturation")

    if len(jitter) > 0:
        order = np.random.permutation(np.arange(len(jitter)))
        for idx in range(0, len(jitter)):
            if jitter[order[idx]] == "brightness":
                images = brightness_list(brightness, images)
            elif jitter[order[idx]] == "contrast":
                images = contrast_list(contrast, images)
            elif jitter[order[idx]] == "saturation":
                images = saturation_list(saturation, images)

    return images


def lighting_list(images, alphastd, eigval, eigvec, alpha=None):
    """
    Perform AlexNet-style PCA jitter on the given list of images.
    Args:
        images (list): list of images to perform lighting jitter.
        alphastd (float): jitter ratio for PCA jitter.
        eigval (ndarray): eigenvalues for PCA jitter.
        eigvec (ndarray): eigenvectors for PCA jitter.
    Returns:
        out_images (list): the list of jittered images.
    """
    if alphastd == 0:
        return images
    # generate alpha1, alpha2, alpha3
    alpha = np.random.normal(0, alphastd, size=(1, 3))
    eig_vec = np.array(eigvec)
    eig_val = np.reshape(eigval, (1, 3))
    rgb = np.sum(
        eig_vec * np.repeat(alpha, 3, axis=0) * np.repeat(eig_val, 3, axis=0),
        axis=1,
    )
    out_images = []
    for image in images:
        for idx in range(image.shape[0]):
            image[idx] = image[idx] + rgb[2 - idx]
        out_images.append(image)
    return out_images


def brightness_list(var, images):
    """
    Perform color brightness on the given list of images.
    Args:
        var (float): variance.
        images (list): list of images to perform color brightness.
    Returns:
        (array): list of images that performed color brightness
    """
    alpha = 1.0 + np.random.uniform(-var, var)

    out_images = []
    for image in images:
        image_bright = np.zeros(image.shape).astype(image.dtype)
        out_images.append(blend(image, image_bright, alpha))
    return out_images


def contrast_list(var, images):
    """
    Perform color contrast on the given list of images.
    Args:
        var (float): variance.
        images (list): list of images to perform color contrast.
    Returns:
        (array): list of images that performed color contrast
    """
    alpha = 1.0 + np.random.uniform(-var, var)

    out_images = []
    for image in images:
        image_gray = grayscale(image)
        image_gray.fill(np.mean(image_gray[0]))
        out_images.append(blend(image, image_gray, alpha))
    return out_images


def saturation_list(var, images):
    """
    Perform color saturation on the list of given images.
    Args:
        var (float): variance.
        images (list): list of images to perform color saturation.
    Returns:
        (list): list of images that performed color saturation.
    """
    alpha = 1.0 + np.random.uniform(-var, var)

    out_images = []
    for image in images:
        img_gray = grayscale(image)
        out_images.append(blend(image, img_gray, alpha))
    return out_images


def color_normalization(image, mean, stddev):
    """
    Perform color normalization on the image with the given mean and stddev.
    Args:
        image (ndarray): image to perform color normalization.
        mean (ndarray): mean value to subtract. dtype is 'float'
        stddev (ndarray): stddev to devide.
    """
    # Input image should in format of CHW
    assert len(mean) == image.shape[0], "channel mean not computed properly"
    assert len(stddev) == image.shape[0], "channel stddev not computed properly"
    return (image - mean) / stddev


def grayscale(image):
    """
    Convert the image to gray scale
    Args:
        image (tensor): image to convert to gray scale. Dimension is
                    `channel` x `height` x `width`.
    Returns:
        image_gray (tensor): image in gray scale.
    """
    # R -> 0.299, G -> 0.587, B -> 0.114.
    image_gray = np.copy(image)
    gray_channel = 0.299 * image[2] + 0.587 * image[1] + 0.114 * image[0]
    image_gray[0] = gray_channel
    image_gray[1] = gray_channel
    image_gray[2] = gray_channel
    return image_gray


def blend(image1, image2, alpha):
    return image1 * alpha + image2 * (1 - alpha)

























