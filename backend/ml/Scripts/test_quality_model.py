# import argparse
# from pathlib import Path
# from PIL import Image
# from ml.classification.predictor import FruitQualityPredictor
#
# def load_image(image_path):
#     image_path = Path(image_path)
#
#     if not image_path.exists():
#         raise FileNotFoundError(f"Image not found: {image_path}")
#
#     if not image_path.is_file():
#         raise ValueError(f"Path is not a file: {image_path}")
#
#     try:
#         with Image.open(image_path) as image:
#             return image.convert("RGB").copy()
#     except Exception as error:
#         raise ValueError(
#             f"Could not open image: {image_path}"
#         ) from error
#
# def print_result(result):
#     print("\nPrediction Result")
#     print("-----------------")
#     print(f"Prediction : {result['prediction']}")
#     print(f"Fruit      : {result['fruit']}")
#     print(f"Grade      : {result['grade']}")
#     print(f"Confidence : {result['confidence']}")
#     if "top_predictions" in result:
#         print("\nTop Predictions")
#         print("---------------")
#         for item in result["top_predictions"]:
#             print(
#                 f"{item['class']} | "
#                 f"fruit={item['fruit']} | "
#                 f"grade={item['grade']} | "
#                 f"confidence={item['confidence']}"
#             )
#
# def main():
#     parser=argparse.ArgumentParser(
#         description="test fruitalyzer on one image"
#     )
#     parser.add_argument(
#         "--image",
#         required=True,
#         help="Path to test image"
#     )
#
#     args = parser.parse_args()
#
#     print("Loading model...")
#     predictor = FruitQualityPredictor()
#
#     print("Loading image...")
#     image = load_image(args.image)
#
#     print("Running prediction...")
#     result = predictor.predict(image)
#
#     print_result(result)
#
#
# if __name__ == "__main__":
#     main()
#
import argparse
from pathlib import Path

from PIL import Image

from ml.classification.predictor import FruitQualityPredictor


def load_image(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if not image_path.is_file():
        raise ValueError(f"Path is not a file: {image_path}")

    with Image.open(image_path) as image:
        return image.convert("RGB").copy()


def print_result(result):
    print("\nPrediction Result")
    print("-----------------")
    print(f"Prediction          : {result['prediction']}")
    print(f"Fruit               : {result['fruit']}")
    print(f"Category            : {result.get('category')}")
    print(f"Grade               : {result['grade']}")
    print(f"Quality Confidence  : {result['confidence']}")
    print(f"Category Confidence : {result.get('category_confidence')}")
    print(f"Combined            : {result.get('combined_prediction')}")

    if "top_predictions" in result:
        print("\nTop Quality Predictions")
        print("-----------------------")
        for item in result["top_predictions"]:
            print(
                f"{item['class']} | fruit={item['fruit']} | "
                f"grade={item['grade']} | confidence={item['confidence']}"
            )

    if "top_categories" in result:
        print("\nTop Allowed Categories")
        print("----------------------")
        for item in result["top_categories"]:
            print(
                f"{item['category']} | confidence={item['confidence']}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Test Fruitalyzer quality and category prediction."
    )
    parser.add_argument("--image", required=True, help="Path to test image")
    args = parser.parse_args()

    print("Loading model...")
    predictor = FruitQualityPredictor()

    print("Loading image...")
    image = load_image(args.image)

    print("Running prediction...")
    result = predictor.predict(image)
    print_result(result)


if __name__ == "__main__":
    main()

