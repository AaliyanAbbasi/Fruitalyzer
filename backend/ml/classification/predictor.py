#
# import json
#
# import numpy as np
# import torch
# from PIL import Image
# from torchvision import transforms
#
# from ml.models.model_builder import build_model, load_checkpoint
# from ml.utils.helpers import get_device, load_config
#
#
# class FruitQualityPredictor:
#
#     def __init__(self):
#         self.config = load_config("configs/config.yaml")
#
#         self.device = get_device(
#             self.config["inference"]["device"]
#         )
#
#         with open(
#             self.config["paths"]["class_mapping_path"],
#             "r",
#         ) as file:
#             self.class_names = json.load(file)
#
#         self.model = build_model(
#             num_classes=len(self.class_names),
#             pretrained=False,
#             dropout_rate=self.config["model"]["dropout_rate"],
#         )
#
#         self.model = load_checkpoint(
#             model=self.model,
#             checkpoint_path=self.config["paths"]["model_path"],
#             device=self.device,
#         )
#
#         self.model.to(self.device)
#         self.model.eval()
#
#         # This deterministic preprocessing is the same as validation/test.
#         self.transform = transforms.Compose(
#             [
#                 transforms.Resize(
#                     (
#                         self.config["preprocessing"]["image_size"],
#                         self.config["preprocessing"]["image_size"],
#                     )
#                 ),
#                 transforms.ToTensor(),
#                 transforms.Normalize(
#                     mean=self.config["preprocessing"]["mean"],
#                     std=self.config["preprocessing"]["std"],
#                 ),
#             ]
#         )
#
#         self.confidence_threshold = self.config["inference"]["confidence_threshold"]
#         self.top_k = self.config["inference"].get("top_k", 3)
#
#     def normalize_lighting(self, image):
#         """Optional gamma correction controlled completely by config.yaml."""
#         gamma_config = self.config["inference"].get("gamma_correction", {})
#
#         if not gamma_config.get("enabled", False):
#             return image
#
#         image_array = np.array(image)
#         brightness = image_array.mean()
#         brightness_threshold = gamma_config.get("brightness_threshold", 110)
#
#         if brightness < brightness_threshold:
#             gamma = gamma_config.get("gamma", 1.35)
#
#             image_array = np.power(
#                 image_array / 255.0,
#                 1.0 / gamma,
#             )
#
#             image_array = (image_array * 255).astype(np.uint8)
#             image = Image.fromarray(image_array)
#
#         return image
#
#     def predict(self, image):
#         image = image.convert("RGB")
#         image = self.normalize_lighting(image)
#
#         tensor = self.transform(image)
#         tensor = tensor.unsqueeze(0).to(self.device)
#
#         with torch.no_grad():
#             outputs = self.model(tensor)
#             probabilities = torch.softmax(outputs, dim=1)
#             confidence, predicted_index = torch.max(probabilities, dim=1)
#
#         confidence = confidence.item()
#         predicted_index = predicted_index.item()
#         class_name = self.class_names[predicted_index]
#         fruit, grade = class_name.split("_", 1)
#
#         if confidence < self.confidence_threshold:
#             return {
#                 "prediction": "unknown",
#                 "fruit": None,
#                 "grade": None,
#                 "confidence": round(confidence, 4),
#             }
#
#         top_values, top_indices = torch.topk(
#             probabilities,
#             k=min(self.top_k, len(self.class_names)),
#         )
#
#         top_predictions = []
#
#         for value, index in zip(top_values[0], top_indices[0]):
#             name = self.class_names[index.item()]
#             top_fruit, top_grade = name.split("_", 1)
#
#             top_predictions.append(
#                 {
#                     "class": name,
#                     "fruit": top_fruit,
#                     "grade": top_grade,
#                     "confidence": round(value.item(), 4),
#                 }
#             )
#
#         return {
#             "prediction": class_name,
#             "fruit": fruit,
#             "grade": grade,
#             "confidence": round(confidence, 4),
#             "top_predictions": top_predictions,
#         }
import json

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from ml.models.model_builder import build_model, load_checkpoint
from ml.utils.helpers import get_device, load_config


class FruitQualityPredictor:

    def __init__(self):
        self.config = load_config("configs/config.yaml")
        self.device = get_device(self.config["inference"]["device"])

        with open(self.config["paths"]["class_mapping_path"], "r") as file:
            self.class_names = json.load(file)

        with open(self.config["paths"]["category_mapping_path"], "r") as file:
            self.category_names = json.load(file)

        self.model = build_model(
            num_classes=len(self.class_names),
            num_category_classes=len(self.category_names),
            pretrained=False,
            dropout_rate=self.config["model"]["dropout_rate"],
        )

        self.model = load_checkpoint(
            model=self.model,
            checkpoint_path=self.config["paths"]["model_path"],
            device=self.device,
        )

        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.Resize(
                    (
                        self.config["preprocessing"]["image_size"],
                        self.config["preprocessing"]["image_size"],
                    )
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=self.config["preprocessing"]["mean"],
                    std=self.config["preprocessing"]["std"],
                ),
            ]
        )

        self.confidence_threshold = self.config["inference"]["confidence_threshold"]
        self.category_confidence_threshold = self.config["inference"].get(
            "category_confidence_threshold", 0.35
        )
        self.top_k = self.config["inference"].get("top_k", 3)
        self.allowed_categories = self.config["inference"]["allowed_categories"]

    def normalize_lighting(self, image):
        """Optional gamma correction controlled completely by config.yaml."""
        gamma_config = self.config["inference"].get("gamma_correction", {})

        if not gamma_config.get("enabled", False):
            return image

        image_array = np.array(image)
        brightness = image_array.mean()
        brightness_threshold = gamma_config.get("brightness_threshold", 110)

        if brightness < brightness_threshold:
            gamma = gamma_config.get("gamma", 1.35)
            image_array = np.power(image_array / 255.0, 1.0 / gamma)
            image_array = (image_array * 255).astype(np.uint8)
            image = Image.fromarray(image_array)

        return image

    def _select_allowed_category(self, fruit, category_probabilities):
        """Prevents impossible outputs such as apple + chaunsa."""
        allowed_names = self.allowed_categories.get(fruit, self.category_names)
        allowed_indices = [
            self.category_names.index(name)
            for name in allowed_names
            if name in self.category_names
        ]

        if not allowed_indices:
            raise ValueError(f"No allowed categories configured for fruit: {fruit}")

        best_index = max(
            allowed_indices,
            key=lambda index: category_probabilities[index].item(),
        )
        best_confidence = category_probabilities[best_index].item()

        ranked_indices = sorted(
            allowed_indices,
            key=lambda index: category_probabilities[index].item(),
            reverse=True,
        )[: self.top_k]

        top_categories = [
            {
                "category": self.category_names[index],
                "confidence": round(category_probabilities[index].item(), 4),
            }
            for index in ranked_indices
        ]

        return self.category_names[best_index], best_confidence, top_categories

    def predict(self, image):
        image = image.convert("RGB")
        image = self.normalize_lighting(image)

        tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            quality_outputs, category_outputs = self.model(tensor)
            quality_probabilities = torch.softmax(quality_outputs, dim=1)[0]
            category_probabilities = torch.softmax(category_outputs, dim=1)[0]

        confidence, predicted_index = torch.max(quality_probabilities, dim=0)
        confidence = confidence.item()
        predicted_index = predicted_index.item()

        class_name = self.class_names[predicted_index]
        fruit, grade = class_name.split("_", 1)

        if confidence < self.confidence_threshold:
            return {
                "prediction": "unknown",
                "fruit": None,
                "grade": None,
                "category": None,
                "confidence": round(confidence, 4),
                "category_confidence": 0.0,
            }

        category, category_confidence, top_categories = self._select_allowed_category(
            fruit=fruit,
            category_probabilities=category_probabilities,
        )

        returned_category = category
        if category_confidence < self.category_confidence_threshold:
            returned_category = "unknown"

        top_values, top_indices = torch.topk(
            quality_probabilities,
            k=min(self.top_k, len(self.class_names)),
        )

        top_predictions = []
        for value, index in zip(top_values, top_indices):
            name = self.class_names[index.item()]
            top_fruit, top_grade = name.split("_", 1)
            top_predictions.append(
                {
                    "class": name,
                    "fruit": top_fruit,
                    "grade": top_grade,
                    "confidence": round(value.item(), 4),
                }
            )

        return {
            # Existing fields remain unchanged for controllers and Flutter.
            "prediction": class_name,
            "fruit": fruit,
            "grade": grade,
            "confidence": round(confidence, 4),
            "top_predictions": top_predictions,

            # New category fields are added without breaking the old response.
            "category": returned_category,
            "category_confidence": round(category_confidence, 4),
            "combined_prediction": f"{fruit}_{returned_category}_{grade}",
            "top_categories": top_categories,
        }
