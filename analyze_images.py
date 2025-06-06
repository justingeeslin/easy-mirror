#!/usr/bin/env python3
"""Run clothing analysis on test images.

This script loads one or more images and processes them using the
:class:`ClothingAnalyzer` to verify clothing detection works.

Usage:
    python analyze_images.py image1.jpg image2.png
    python analyze_images.py path/to/image_directory/

Results are printed as JSON. Optionally, use ``-o`` to write results to a file.
"""

import argparse
import json
import os
import glob
import cv2

from clothing_analysis import ClothingAnalyzer


def gather_images(paths):
    """Collect image files from the provided paths."""
    images = []
    for path in paths:
        if os.path.isdir(path):
            for pattern in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
                images.extend(sorted(glob.glob(os.path.join(path, pattern))))
        else:
            images.append(path)
    return images


def analyze_images(image_paths):
    """Analyze each image and return a mapping of path -> analysis."""
    analyzer = ClothingAnalyzer()
    results = {}
    for img_path in image_paths:
        frame = cv2.imread(img_path)
        if frame is None:
            results[img_path] = {"error": "Failed to load image"}
            continue
        analysis = analyzer.analyze_clothing(frame)
        if analysis is None:
            results[img_path] = {"error": "Analysis failed"}
        else:
            results[img_path] = analysis
    return results


def main():
    parser = argparse.ArgumentParser(description="Run clothing analysis on images")
    parser.add_argument("paths", nargs="+", help="Image files or directories")
    parser.add_argument("-o", "--output", help="Optional JSON output file")
    args = parser.parse_args()

    images = gather_images(args.paths)
    if not images:
        parser.error("No image files found")

    results = analyze_images(images)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
