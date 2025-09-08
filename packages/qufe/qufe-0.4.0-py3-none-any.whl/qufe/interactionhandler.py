"""
Screen interaction and automation utilities for capturing, analyzing, and interacting with screen content.

This module provides comprehensive tools for:
- Screen capture and image processing
- Color detection and analysis
- Mouse automation and region-based clicking
- Image comparison and difference detection
- Progress tracking in Jupyter environments

Required dependencies:
    pip install qufe[vision]

This installs: opencv-python>=4.1.0, matplotlib>=3.1.0, pyautogui>=0.9.48, mss>=4.0.0

Optional Jupyter dependencies:
    pip install qufe[jupyter]

This installs: ipython>=6.0.0
"""

import time
import random
from typing import Tuple, List, Dict, Optional, Union


# Lazy imports for external dependencies
def _import_vision_dependencies():
    """Lazy import computer vision dependencies with helpful error message."""
    try:
        import numpy as np
        import cv2
        import pyautogui
        import mss
        from matplotlib import pyplot as plt
        return np, cv2, pyautogui, mss, plt
    except ImportError as e:
        raise ImportError(
            "Screen interaction functionality requires computer vision libraries. "
            "Install with: pip install qufe[vision]"
        ) from e


def _import_jupyter_dependencies():
    """Lazy import Jupyter dependencies with graceful fallback."""
    try:
        from IPython.display import clear_output, DisplayHandle
        return clear_output, DisplayHandle
    except ImportError:
        return None, None


def help():
    """
    Display help information for screen interaction utilities.

    Shows installation instructions, available functions, and usage examples.
    """
    print("qufe.interactionhandler - Screen Interaction & Automation")
    print("=" * 60)
    print()

    try:
        _import_vision_dependencies()
        print("✓ Vision Dependencies: INSTALLED")
    except ImportError:
        print("✗ Vision Dependencies: MISSING")
        print("  Install with: pip install qufe[vision]")
        print("  This installs: opencv-python, matplotlib, pyautogui, mss, numpy")
        print()

    clear_output, DisplayHandle = _import_jupyter_dependencies()
    if clear_output and DisplayHandle:
        print("✓ Jupyter Dependencies: INSTALLED")
    else:
        print("✗ Jupyter Dependencies: MISSING (optional)")
        print("  Install with: pip install qufe[jupyter]")
        print("  This enables: ProgressUpdater class")

    print()
    print("AVAILABLE FUNCTIONS:")
    print("  • get_resolution(): Get screen resolution")
    print("  • get_screenshot(): Capture screen regions or full screen")
    print("  • display_image(): Show images in Jupyter or OpenCV windows")
    print("  • get_color_boxes(): Find regions matching specific colors")
    print("  • click_random_in_region(): Automated clicking with randomization")
    print("  • find_image_differences(): Compare images and highlight changes")
    print("  • analyze_color_codes(): Extract and analyze colors from regions")
    print("  • ProgressUpdater: Real-time progress updates in Jupyter")
    print()

    print("USAGE EXAMPLES:")
    print("  from qufe.interactionhandler import get_screenshot, display_image")
    print("  ")
    print("  # Capture full screen")
    print("  screenshot = get_screenshot()")
    print("  display_image(screenshot, is_bgra=True)")
    print("  ")
    print("  # Capture specific region")
    print("  region_shot = get_screenshot(100, 100, 800, 600)")
    print("  ")
    print("  # Find colored regions")
    print("  boxes = get_color_boxes(screenshot, (255, 0, 0), tolerance=0.1)")
    print("  ")
    print("  # Progress tracking in Jupyter")
    print("  progress = ProgressUpdater('Processing...')")
    print("  progress.update('Step 1 complete')")


def get_resolution() -> Tuple[int, int]:
    """
    Get screen resolution.

    Returns:
        Tuple[int, int]: Screen width and height in pixels

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    with mss_module.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        width = monitor["width"]
        height = monitor["height"]
        print(f"Screen Resolution: {width}x{height}")
        return width, height


def build_region(x: int, y: int, w: int, h: int) -> Dict[str, int]:
    """
    Build a region dictionary for screen capture.

    Args:
        x: Left coordinate
        y: Top coordinate
        w: Width
        h: Height

    Returns:
        Dict[str, int]: Region dictionary with 'left', 'top', 'width', 'height' keys
    """
    return {'left': x, 'top': y, 'width': w, 'height': h}


def get_screenshot(x: int = 0, y: int = 0, w: int = 0, h: int = 0):
    """
    Capture a screenshot of specified region or full screen.

    Args:
        x: Left coordinate (default: 0)
        y: Top coordinate (default: 0)
        w: Width (default: 0, captures full width)
        h: Height (default: 0, captures full height)

    Returns:
        numpy.ndarray: Screenshot as numpy array in BGRA format

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    if not sum([x, y, w, h]):  # If no parameters provided, capture full desktop
        (w, h) = get_resolution()

    region = build_region(x, y, w, h)
    with mss_module.mss() as sct:
        screenshot = sct.grab(region)

    return np.array(screenshot)


def display_image(img, jupyter: bool = True, is_bgra: bool = False) -> None:
    """
    Display image in Jupyter notebook or OpenCV window.

    Args:
        img: Image array to display (numpy.ndarray)
        jupyter: Whether to display in Jupyter notebook (default: True)
        is_bgra: Whether image is in BGRA format (default: False)

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    if not hasattr(img, 'shape'):
        raise TypeError("Input must be a numpy array (image)")

    if jupyter:
        if is_bgra:  # Convert BGRA to RGBA
            img_rgba = img[..., [2, 1, 0, 3]]
        else:
            img_rgba = img

        plt.imshow(img_rgba)
        plt.axis('off')
        plt.show()
    else:
        cv2.imshow("Screen Capture", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def get_color_boxes(
        image,
        rgb_color: Tuple[int, int, int],
        tolerance: float = 0.1,
        min_size: int = 5) -> List[Tuple[int, int, int, int]]:
    """
    Find bounding boxes of regions matching a specific color within tolerance.

    Args:
        image: Input image array (numpy.ndarray)
        rgb_color: Target RGB color tuple
        tolerance: Color matching tolerance (0.0 to 1.0)
        min_size: Minimum size for valid boxes

    Returns:
        List[Tuple[int, int, int, int]]: List of bounding boxes as (x, y, width, height)

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    if not hasattr(image, 'shape'):
        raise TypeError("Input must be a numpy array (image)")

    target_color = np.array(rgb_color[::-1])  # RGB to BGR
    lower_bound = np.clip(target_color * (1 - tolerance), 0, 255).astype(np.uint8)
    upper_bound = np.clip(target_color * (1 + tolerance), 0, 255).astype(np.uint8)

    mask = cv2.inRange(image, lower_bound, upper_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > min_size and h > min_size:
            boxes.append((x, y, w, h))

    return boxes


def find_largest_box(boxes: List[Tuple[int, int, int, int]]) -> Optional[Tuple[int, int, int, int]]:
    """
    Find the box with the largest area from a list of boxes.

    Args:
        boxes: List of bounding boxes as (x, y, width, height)

    Returns:
        Optional[Tuple[int, int, int, int]]: Largest box or None if list is empty
    """
    if not boxes:
        return None
    return max(boxes, key=lambda b: b[2] * b[3])


def draw_boxes(
        image,
        boxes: List[Tuple[int, int, int, int]],
        color: Tuple[int, int, int] = (0, 0, 255),
        thickness: int = 2):
    """
    Draw bounding boxes on an image.

    Args:
        image: Input image array (numpy.ndarray)
        boxes: List of bounding boxes as (x, y, width, height)
        color: Box color in BGR format (default: red)
        thickness: Box border thickness

    Returns:
        numpy.ndarray: Image with drawn boxes

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    if not hasattr(image, 'shape'):
        raise TypeError("Input must be a numpy array (image)")

    img = image.copy()
    if img.shape[2] == 4:  # Convert BGRA to BGR
        img = img[..., :3].copy()

    for x, y, w, h in boxes:
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

    return img


def click_random_in_region(region: Dict[str, int], margin: float = 0.4) -> Tuple[int, int]:
    """
    Click randomly within a specified region with margin.

    Args:
        region: Region dictionary with 'left', 'top', 'width', 'height' keys
        margin: Margin ratio to avoid edges (0.0 to 0.5)

    Returns:
        Tuple[int, int]: Click coordinates (x, y)

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    x_min = region['left'] + int(region['width'] * margin)
    x_max = region['left'] + int(region['width'] * (1 - margin))
    y_min = region['top'] + int(region['height'] * margin)
    y_max = region['top'] + int(region['height'] * (1 - margin))

    click_x = random.randint(x_min, x_max)
    click_y = random.randint(y_min, y_max)

    pyautogui.moveTo(click_x, click_y)
    pyautogui.sleep(0.01)
    pyautogui.click()

    return click_x, click_y


def click_random_in_position(
        top_left_x: int,
        top_left_y: int,
        bottom_right_x: int,
        bottom_right_y: int) -> Tuple[int, int]:
    """
    Click randomly within a rectangular area defined by two corner points.

    Args:
        top_left_x: Left coordinate
        top_left_y: Top coordinate
        bottom_right_x: Right coordinate
        bottom_right_y: Bottom coordinate

    Returns:
        Tuple[int, int]: Click coordinates (x, y)
    """
    width = bottom_right_x - top_left_x
    height = bottom_right_y - top_left_y

    region = build_region(top_left_x, top_left_y, width, height)
    return click_random_in_region(region)


def find_image_differences(
        img_1,
        img_2,
        min_size: int = 5,
        print_result: bool = False,
        display_result: bool = False,
        thickness: int = 1,
        is_bgra: bool = False) -> List:
    """
    Find differences between two images and return contours of different regions.

    Args:
        img_1: First image array (numpy.ndarray)
        img_2: Second image array (numpy.ndarray)
        min_size: Minimum size for valid difference regions
        print_result: Whether to print difference regions
        display_result: Whether to display result with boxes
        thickness: Box border thickness for display
        is_bgra: Whether images are in BGRA format

    Returns:
        List: Contours of different regions

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    if not hasattr(img_1, 'shape') or not hasattr(img_2, 'shape'):
        raise TypeError("Inputs must be numpy arrays (images)")

    # Calculate image difference
    img_diff = cv2.absdiff(img_1, img_2)
    mask = np.any(img_diff > 30, axis=2).astype(np.uint8)

    # Dilation to better detect contours
    kernel = np.ones((3, 3), np.uint8)
    mask_dilated = cv2.dilate(mask, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if w > min_size and h > min_size:
            boxes.append((x, y, w, h))

    if print_result:
        for (i, (x, y, w, h)) in enumerate(boxes):
            print(f"[{i}] Difference region: x={x}, y={y}, w={w}, h={h}")

    if display_result:
        output = draw_boxes(image=img_1, boxes=boxes, thickness=thickness)
        display_image(output, jupyter=True, is_bgra=is_bgra)

    return contours


def analyze_color_codes(
        x: int = 0,
        y: int = 0,
        size: int = 0,
        print_result: bool = True,
        display_result: bool = False,
        display_original: bool = False,
        img_path: str = '',
        thickness: int = 1,
        img = None):
    """
    Analyze color codes in a specified square region of the screen or image.

    Args:
        x: Left coordinate of analysis region
        y: Top coordinate of analysis region
        size: Size of square region to analyze
        print_result: Whether to print individual pixel colors
        display_result: Whether to display the analyzed region
        display_original: Whether to display original image with region box
        img_path: Path to image file (alternative to screen capture)
        thickness: Box border thickness for display
        img: Image array to analyze (alternative to screen capture or file)

    Returns:
        numpy.ndarray: Array of unique colors found in the region

    Raises:
        ImportError: If required vision dependencies are not installed
    """
    np, cv2, pyautogui, mss_module, plt = _import_vision_dependencies()

    # Determine image source
    if img is not None:
        if not hasattr(img, 'shape'):
            raise TypeError("img parameter must be a numpy array (image)")
        img_rgba = img
    elif img_path:
        img_read = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img_read is None:
            raise FileNotFoundError(f"Could not load image from: {img_path}")
        img_rgba = img_read[..., [2, 1, 0, 3]]  # BGRA to RGBA
    else:
        img_np = get_screenshot()  # Capture full screen
        img_rgba = img_np[..., [2, 1, 0, 3]]  # BGRA to RGBA

    if display_result:
        display_image(img_rgba[y:y+size, x:x+size])

    if display_original:
        original_with_box = draw_boxes(
            image=img_rgba,
            boxes=[(x, y, size, size)],
            color=(255, 0, 0),  # Red in RGB format
            thickness=thickness
        )
        display_image(original_with_box)

    color_array = img_rgba[y:y+size, x:x+size, :3]  # Extract RGB channels

    if print_result:
        for i in range(size):
            print(f'\nLine No. {i+1}')
            for j in range(size):
                color = tuple(int(c) for c in color_array[i, j])
                print(f"(x: {x+j}, y: {y+i})  Color: {color}")

    # Find unique colors
    flat_colors = color_array.reshape(-1, 3)
    unique_colors = np.unique(flat_colors, axis=0)

    print('\nUnique colors found:')
    for color in unique_colors:
        print(tuple(int(c) for c in color))

    return unique_colors


class ProgressUpdater:
    """
    A progress updater for Jupyter notebooks that updates text in place.

    Uses display handles to update progress information without creating
    multiple output cells.

    Note: Requires Jupyter/IPython environment. Install with: pip install qufe[jupyter]
    """

    def __init__(self, initial_text: str = '', display_id: str = 'Progress'):
        """
        Initialize progress updater.

        Args:
            initial_text: Initial text to display
            display_id: Unique identifier for the display handle

        Raises:
            ImportError: If IPython is not available (not in Jupyter environment)
        """
        clear_output, DisplayHandle = _import_jupyter_dependencies()

        if not DisplayHandle:
            raise ImportError(
                "ProgressUpdater requires Jupyter/IPython environment. "
                "Install with: pip install qufe[jupyter]"
            )

        self.handle = DisplayHandle(display_id=display_id)
        self.handle.display(initial_text)

    def update(self, text: str) -> None:
        """
        Update the displayed text.

        Args:
            text: New text to display
        """
        self.handle.update(text)
