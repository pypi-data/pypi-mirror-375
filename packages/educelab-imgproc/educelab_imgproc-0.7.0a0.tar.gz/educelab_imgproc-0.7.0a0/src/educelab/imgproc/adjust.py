import numpy as np
from skimage import color
from skimage.filters import gaussian
from skimage.restoration import denoise_bilateral

from educelab.imgproc.conversion import as_dtype


def brightness(image, val):
    """Adjust image brightness.

    :param image: Input image.
    :param val: Brightness adjustment factor in units of the image's
           dynamic range (+/-).
    :return: Brightness-adjusted image.
    """
    return image + val


def contrast(image, val: float):
    """Adjust image contrast.

    Note that this is a simple contrast adjustment that corresponds to the
    Legacy method in Photoshop.

    :param image: Input image.
    :param val: Contrast adjustment factor (+/-). Positive values increase
           contrast while negative values decrease contrast. Values below -1
           will invert the image.
    :return: Contrast-adjusted image.
    """
    val = val + 1.
    return val * image + 0.5 * (1. - val)


def brightness_contrast(image: np.ndarray, b: float, c):
    """Apply a brightness-contrast adjustment.

    :param image: Input image.
    :param b: Brightness adjustment factor in units of the image's dynamic
           range (+/-).
    :param c: Contrast adjustment factor (+/-). Positives values increase
           contrast while negative values decrease contrast.
    :return: Brightness/contrast-adjusted image.
    """
    return contrast(brightness(image, b), c)


def exposure(image, val):
    """Increase image exposure.

    :param image: Input image.
    :param val: Exposure adjustment factor (+/-).
    :return: Exposure-adjusted image.
    """
    return image * 2 ** val


def shadows(image, val):
    """Image shadow adjustment.

    Adapted from an implementation by
    `HViktorTsoi <https://gist.github.com/HViktorTsoi/8e8b0468a9fb07842669aa368382a7df>`_.

    :param image: Input image.
    :param val: Shadow adjustment factor (+/-).
    :return: Exposure-adjusted image.
    """
    shadow_val = 1. + val / 100. * 2
    shadow_mid = 3. / 10.
    shadow_region = np.clip(1. - image / shadow_mid, 0, 1)
    shadow_region[np.where(image >= shadow_mid)] = 0.
    return (1. - shadow_region) * image + shadow_region * (
                1 - np.power(1. - np.clip(image, 0., 1.), shadow_val))


def shadows_highlights(img, shadows_gain, highlights_gain,
                       blur_method='gaussian', whitepoint=0, compress=.5,
                       shadows_correct=1., highlights_correct=.5,
                       bilateral_radius: int = None, sigma: float = 1):
    """Image shadows and highlights correct. Ported from
    `darktable <https://docs.darktable.org/usermanual/3.8/en/module-reference/processing-modules/shadows-and-highlights/>`_.

    :param img: Input image
    :param shadows_gain: [-1, 1] Shadow adjustment.
    :param highlights_gain: [-1, 1] Highlight adjustment.
    :param blur_method: 'bilateral' or 'gaussian'.
    :param whitepoint: [-1, 1] White point adjustment.
    :param compress: [0, 1] Controls effect on midtones. High values limit the
           effect to only the darkest and brightest values.
    :param shadows_correct: [0, 1] Controls saturation effect on adjusted shadows.
    :param highlights_correct: [0, 1] Controls saturation effect on adjusted highlights.
    :param sigma: (0, inf) Std. dev. for Gaussian blur filter.
    :param bilateral_radius: [5, inf) Radius of Bilateral filter kernel.
    """
    # This function is a port of the shadows/highlights function from darktable:
    # https://github.com/darktable-org/darktable/blob/d2c11c4f54066afab21de1cbeb981275c53f0dfb/src/iop/shadhi.c#L343
    # This port is functionally identical to the darktable version, though we
    # rely on alternative methods for blurring the intensity map.

    if shadows_gain == 0. and highlights_gain == 0.:
        return img

    out_dtype = img.dtype
    in_2d = False
    if img.ndim == 2:
        in_2d = True
        img = img[..., None]
    cns = img.shape[-1]
    img = as_dtype(img, np.float32)

    # split channels
    img_in, a = None, None
    if cns == 1:
        img_in = img
    elif cns == 2:
        img_in, a = img[..., 0:1], img[..., 1:2]
    elif cns == 3:
        img_in = img
    elif cns == 4:
        img_in, a = img[..., :3], img[..., 3:4]
    else:
        raise ValueError(f'unsupported number of channels: {cns}')

    # Gray to RGB
    if img_in.shape[2] == 1:
        img_in = np.concatenate((img_in,) * 3, axis=-1)

    # blur in Gray/RGB (out)
    if blur_method == 'bilateral':
        win_size = None
        if bilateral_radius is not None:
            win_size = 2 * bilateral_radius
        img_out = denoise_bilateral(img_in, win_size=win_size, sigma_spatial=1,
                                    channel_axis=-1)
    elif blur_method == 'gaussian':
        img_out = gaussian(img_in, sigma=sigma)
    else:
        raise ValueError(f'unsupported blur method: {blur_method}')

    # convert to LAB
    img_in = color.rgb2lab(img_in)
    img_out = color.rgb2lab(img_out)

    # adjust params
    shadows_gain = 2. * shadows_gain
    highlights_gain = 2. * highlights_gain
    whitepoint = max(1. - whitepoint / 10., 0.01)
    compress = np.clip(compress, 0, 0.99)
    shadows_correct = shadows_correct - 0.5 * np.sign(shadows_gain) + 0.5
    highlights_correct = highlights_correct - 0.5 * np.sign(
        -highlights_gain) + 0.5
    low_approx = 0.000001

    # useful constants
    min_l, max_l = 0., 1.
    min_ab, max_ab = -1., 1.
    halfmax = 0.5
    doublemax = 2.

    # invert and desaturate the blurred image
    img_out[..., 0] = 100. - img_out[..., 0]
    img_out[..., 1:3] = 0.

    # normalize LAB values
    ta = img_in / np.array([100., 128., 128.], np.float32)
    tb = img_out / np.array([100., 128., 128.], np.float32)

    # scale w.r.t. whitepoint adjustment
    ta[..., 0] = np.where(ta[..., 0] > 0, ta[..., 0] / whitepoint, ta[..., 0])
    tb[..., 0] = np.where(tb[..., 0] > 0, tb[..., 0] / whitepoint, tb[..., 0])

    # overlay highlights
    highlights2 = highlights_gain * highlights_gain
    highlights_xform = np.clip(1. - tb[..., 0] / (1. - compress), 0., 1.)
    iters = 0
    while highlights2 > 0.:
        la = ta[..., 0]
        lb = (tb[..., 0] - halfmax) * np.sign(-highlights_gain) * np.sign(
            max_l - la) + halfmax

        abs_la = np.abs(la)
        abs_la[abs_la == 0] = np.finfo(np.float32).eps
        lref = np.where(abs_la > low_approx, 1. / abs_la, 1. / low_approx)
        lref = np.copysign(lref, la)
        abs_la = np.abs(1 - la)
        abs_la[abs_la == 0] = np.finfo(np.float32).eps
        href = np.where(abs_la > low_approx, 1. / abs_la, 1. / low_approx)
        href = np.copysign(href, 1. - la)

        chunk = 1. if highlights2 > 1. else highlights2
        optrans = chunk * highlights_xform
        highlights2 -= 1.

        # luma
        ta_cond = np.where(la > halfmax,
                           max_l - (max_l - doublemax * (la - halfmax)) * (
                                   max_l - lb), doublemax * la * lb)
        ta[..., 0] = la * (1. - optrans) + ta_cond * optrans
        ta[..., 0] = np.clip(ta[..., 0], min_l, max_l)

        # chroma
        chroma_factor = ta[..., 0] * lref * (1. - highlights_correct) + (
                1. - ta[..., 0]) * href * highlights_correct
        ta[..., 1:3] = ta[..., 1:3] * (1. - optrans[..., None]) + (
                ta[..., 1:3] + tb[..., 1:3]) * chroma_factor[..., None] * \
                       optrans[..., None]
        ta[..., 1:3] = np.clip(ta[..., 1:3], min_ab, max_ab)
        iters += 1

    # overlay shadows
    shadows2 = shadows_gain * shadows_gain
    shadows_xform = np.clip(
        tb[..., 0] / (1. - compress) - compress / (1. - compress), 0., 1.)
    iters = 0
    while shadows2 > 0.:
        la = ta[..., 0]
        lb = (tb[..., 0] - halfmax) * np.sign(shadows_gain) * np.sign(
            max_l - la) + halfmax

        abs_la = np.abs(la)
        abs_la[abs_la == 0] = np.finfo(np.float32).eps
        lref = np.where(abs_la > low_approx, 1. / abs_la, 1. / low_approx)
        lref = np.copysign(lref, la)
        abs_la = np.abs(1 - la)
        abs_la[abs_la == 0] = np.finfo(np.float32).eps
        href = np.where(abs_la > low_approx, 1 / abs_la, 1. / low_approx)
        href = np.copysign(href, 1. - la)

        chunk = 1. if shadows2 > 1. else shadows2
        optrans = chunk * shadows_xform
        shadows2 -= 1.

        # luma
        ta_cond = np.where(la > halfmax,
                           max_l - (max_l - doublemax * (la - halfmax)) * (
                                   max_l - lb), doublemax * la * lb)
        ta[..., 0] = la * (1. - optrans) + ta_cond * optrans
        ta[..., 0] = np.clip(ta[..., 0], min_l, max_l)

        # chroma
        chroma_factor = ta[..., 0] * lref * shadows_correct + (
                1. - ta[..., 0]) * href * (1. - shadows_correct)
        ta[..., 1:3] = ta[..., 1:3] * (1. - optrans[..., None]) + (
                ta[..., 1:3] + tb[..., 1:3]) * chroma_factor[..., None] * \
                       optrans[..., None]
        ta[..., 1:3] = np.clip(ta[..., 1:3], min_ab, max_ab)
        iters += 1

    output = ta * [100., 128., 128.]
    output = color.lab2rgb(output)

    # convert back to output
    if cns == 1:
        idx = 0 if in_2d else slice(0, 1)
        output = output[..., idx]
    elif cns == 2:
        output = np.concatenate([output[..., 0:1], a], axis=-1)
    elif cns == 3:
        # nothing to do
        pass
    elif cns == 4:
        output = np.concatenate([output, a], axis=-1)
    else:
        raise ValueError(f'unsupported number of channels: {cns}')

    # convert to output dtype
    output = as_dtype(output, dtype=out_dtype)
    return output
