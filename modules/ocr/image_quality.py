from pathlib import Path

import cv2


MINIMUM_WIDTH = 600
MINIMUM_HEIGHT = 400

BLUR_THRESHOLD = 100.0

DARK_BRIGHTNESS_THRESHOLD = 65.0
BRIGHT_BRIGHTNESS_THRESHOLD = 252.0

MINIMUM_PASSPORT_ASPECT_RATIO = 1.30
MAXIMUM_PASSPORT_ASPECT_RATIO = 2.20

GLARE_MRZ_CONTRAST_THRESHOLD = 20.0


def assess_image_quality(image_path):
    image_path = Path(image_path)

    image = cv2.imread(str(image_path))

    if image is None:
        return {
            "quality_check_available": False,
            "width": None,
            "height": None,
            "aspect_ratio": None,
            "blur_score": None,
            "brightness_score": None,
            "mrz_contrast_score": None,
            "is_low_resolution": False,
            "is_blurry": False,
            "is_too_dark": False,
            "is_too_bright": False,
            "is_wrong_orientation": False,
            "is_cropped": False,
            "is_glare_detected": False,
            "error": (
                f"Could not read image file: {image_path}"
            ),
        }

    height, width = image.shape[:2]

    grayscale_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    aspect_ratio = width / height

    blur_score = float(
        cv2.Laplacian(
            grayscale_image,
            cv2.CV_64F
        ).var()
    )

    brightness_score = float(grayscale_image.mean())

    mrz_start_y = int(height * 0.65)

    mrz_region = grayscale_image[
        mrz_start_y:height,
        0:width
    ]

    mrz_contrast_score = float(mrz_region.std())

    is_low_resolution = bool(
        width < MINIMUM_WIDTH
        or height < MINIMUM_HEIGHT
    )

    is_too_dark = bool(
        brightness_score < DARK_BRIGHTNESS_THRESHOLD
    )

    is_too_bright = bool(
        brightness_score > BRIGHT_BRIGHTNESS_THRESHOLD
    )

    is_wrong_orientation = bool(height > width)

    is_cropped = bool(
        not is_wrong_orientation
        and (
            aspect_ratio < MINIMUM_PASSPORT_ASPECT_RATIO
            or aspect_ratio > MAXIMUM_PASSPORT_ASPECT_RATIO
        )
    )

    is_blurry = bool(
        not is_too_dark
        and not is_too_bright
        and blur_score < BLUR_THRESHOLD
    )

    can_assess_glare = bool(
        not is_low_resolution
        and not is_blurry
        and not is_too_dark
        and not is_too_bright
        and not is_wrong_orientation
        and not is_cropped
    )

    is_glare_detected = bool(
        can_assess_glare
        and mrz_contrast_score < GLARE_MRZ_CONTRAST_THRESHOLD
    )

    return {
        "quality_check_available": True,
        "width": width,
        "height": height,
        "aspect_ratio": round(aspect_ratio, 2),
        "blur_score": round(blur_score, 2),
        "brightness_score": round(brightness_score, 2),
        "mrz_contrast_score": round(mrz_contrast_score, 2),
        "is_low_resolution": is_low_resolution,
        "is_blurry": is_blurry,
        "is_too_dark": is_too_dark,
        "is_too_bright": is_too_bright,
        "is_wrong_orientation": is_wrong_orientation,
        "is_cropped": is_cropped,
        "is_glare_detected": is_glare_detected,
        "error": None,
    }