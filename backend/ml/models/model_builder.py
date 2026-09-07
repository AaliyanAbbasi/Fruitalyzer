#
# import torch
# import torch.nn as nn
# from torchvision import models
#
#
# def build_model(num_classes, pretrained=True, dropout_rate=0.3):
#     """Builds one EfficientNet-B0 with a classifier matching the dataset."""
#     if pretrained:
#         weights = models.EfficientNet_B0_Weights.DEFAULT
#     else:
#         weights = None
#
#     model = models.efficientnet_b0(weights=weights)
#     in_features = model.classifier[1].in_features
#
#     model.classifier = nn.Sequential(
#         nn.Dropout(p=dropout_rate),
#         nn.Linear(in_features, num_classes),
#     )
#
#     return model
#
#
# def freeze_backbone(model, freeze_blocks=5, freeze_batch_norm=True):
#     """
#     Configures which EfficientNet feature blocks can learn.
#
#     The function first resets all feature parameters to trainable. This matters
#     because it is called twice: all blocks are frozen in stage 1, then only the
#     early blocks remain frozen in stage 2.
#     """
#     if hasattr(model, "features"):
#         for parameter in model.features.parameters():
#             parameter.requires_grad = True
#
#         total_blocks = len(model.features)
#         blocks_to_freeze = min(freeze_blocks, total_blocks)
#
#         for block_index in range(blocks_to_freeze):
#             for parameter in model.features[block_index].parameters():
#                 parameter.requires_grad = False
#
#     # The new nine-class classifier must always remain trainable.
#     for parameter in model.classifier.parameters():
#         parameter.requires_grad = True
#
#     if freeze_batch_norm:
#         for module in model.modules():
#             if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d)):
#                 module.eval()
#                 for parameter in module.parameters():
#                     parameter.requires_grad = False
#
#     return model
#
#
# def keep_frozen_batch_norm_in_eval(model):
#     """
#     model.train() changes every BatchNorm layer back to training mode.
#     Calling this immediately afterwards keeps frozen BatchNorm statistics fixed.
#     """
#     for module in model.modules():
#         if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d)):
#             if not any(parameter.requires_grad for parameter in module.parameters()):
#                 module.eval()
#
#
# def save_checkpoint(
#     model,
#     optimizer,
#     epoch,
#     metrics,
#     class_names,
#     save_path,
#     config=None,
#     stage=None,
# ):
#     checkpoint = {
#         "epoch": epoch,
#         "stage": stage,
#         "model_state_dict": model.state_dict(),
#         "optimizer_state_dict": optimizer.state_dict() if optimizer else None,
#         "metrics": metrics,
#         "class_names": class_names,
#         "num_classes": len(class_names),
#     }
#
#     # Store deployment-critical preprocessing beside the weights.
#     if config:
#         checkpoint["preprocessing"] = {
#             "image_size": config["preprocessing"]["image_size"],
#             "mean": config["preprocessing"]["mean"],
#             "std": config["preprocessing"]["std"],
#         }
#
#     torch.save(checkpoint, save_path)
#
#
# def load_checkpoint(model, checkpoint_path, device):
#     checkpoint = torch.load(checkpoint_path, map_location=device)
#
#     if "model_state_dict" in checkpoint:
#         model.load_state_dict(checkpoint["model_state_dict"])
#     else:
#         model.load_state_dict(checkpoint)
#
#     return model
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models


class FruitalyzerMultiTaskModel(nn.Module):
    """
    One EfficientNet-B0 backbone with two small output heads.

    quality head keeps the old 9 outputs: apple_A ... mango_C
    category head adds: red_apple, green_apple, banana, chaunsa, sindhri,
    anwar_ratol
    """

    def __init__(
        self,
        num_quality_classes,
        num_category_classes,
        pretrained=True,
        dropout_rate=0.3,
    ):
        super().__init__()

        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        base_model = models.efficientnet_b0(weights=weights)
        in_features = base_model.classifier[1].in_features

        # Keep these names compatible with the previous checkpoint so its
        # EfficientNet features and 9-class quality classifier can be reused.
        self.features = base_model.features
        self.avgpool = base_model.avgpool
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, num_quality_classes),
        )
        self.category_classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, num_category_classes),
        )

    def forward(self, images):
        features = self.features(images)
        pooled = self.avgpool(features)
        pooled = torch.flatten(pooled, 1)

        quality_logits = self.classifier(pooled)
        category_logits = self.category_classifier(pooled)

        return quality_logits, category_logits


def build_model(
    num_classes,
    pretrained=True,
    dropout_rate=0.3,
    num_category_classes=None,
):
    """Builds the single multitask EfficientNet used by training and API."""
    if num_category_classes is None:
        raise ValueError("num_category_classes is required for the multitask model.")

    return FruitalyzerMultiTaskModel(
        num_quality_classes=num_classes,
        num_category_classes=num_category_classes,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
    )


def load_existing_quality_weights(model, checkpoint_path, device):
    """
    Reuses the current 9-class model's backbone and quality head.

    The new category head has no matching old weights and remains randomly
    initialized. All existing model files remain untouched during loading.
    """
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Existing quality model not found: {checkpoint_path}"
        )

    checkpoint = torch.load(checkpoint_path, map_location=device)
    old_state = checkpoint.get("model_state_dict", checkpoint)

    compatible_state = {
        key: value
        for key, value in old_state.items()
        if key.startswith("features.") or key.startswith("classifier.")
    }

    result = model.load_state_dict(compatible_state, strict=False)

    unexpected = list(result.unexpected_keys)
    unsafe_missing = [
        key
        for key in result.missing_keys
        if not key.startswith("category_classifier.")
    ]

    if unexpected or unsafe_missing:
        raise RuntimeError(
            "Existing model is not compatible with multitask initialization. "
            f"Unexpected={unexpected}, unsafe_missing={unsafe_missing}"
        )

    print("Loaded existing EfficientNet backbone and 9-class quality head.")
    print("New category head will be learned from the new variety folders.")
    return model


def configure_training_stage(model, stage_name, freeze_blocks=5, freeze_batch_norm=True):
    """Sets trainable parameters for the two safe training stages."""
    for parameter in model.parameters():
        parameter.requires_grad = False

    if stage_name == "stage1_category_head":
        # Preserve the proven quality model while learning only the new head.
        for parameter in model.category_classifier.parameters():
            parameter.requires_grad = True

    elif stage_name == "stage2_multitask_finetune":
        total_blocks = len(model.features)
        blocks_to_freeze = min(freeze_blocks, total_blocks)

        for block_index in range(blocks_to_freeze, total_blocks):
            for parameter in model.features[block_index].parameters():
                parameter.requires_grad = True

        for parameter in model.classifier.parameters():
            parameter.requires_grad = True

        for parameter in model.category_classifier.parameters():
            parameter.requires_grad = True

    else:
        raise ValueError(f"Unknown training stage: {stage_name}")

    if freeze_batch_norm:
        for module in model.modules():
            if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d)):
                module.eval()
                for parameter in module.parameters():
                    parameter.requires_grad = False

    return model


def keep_frozen_batch_norm_in_eval(model):
    """Keeps frozen BatchNorm running statistics fixed after model.train()."""
    for module in model.modules():
        if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d)):
            if not any(parameter.requires_grad for parameter in module.parameters()):
                module.eval()


def save_checkpoint(
    model,
    optimizer,
    epoch,
    metrics,
    class_names,
    category_names,
    save_path,
    config=None,
    stage=None,
):
    checkpoint = {
        "epoch": epoch,
        "stage": stage,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict() if optimizer else None,
        "metrics": metrics,
        "class_names": class_names,
        "category_names": category_names,
        "num_classes": len(class_names),
        "num_category_classes": len(category_names),
        "model_type": "efficientnet_b0_multitask",
    }

    if config:
        checkpoint["preprocessing"] = {
            "image_size": config["preprocessing"]["image_size"],
            "mean": config["preprocessing"]["mean"],
            "std": config["preprocessing"]["std"],
        }

    torch.save(checkpoint, save_path)


def load_checkpoint(model, checkpoint_path, device):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state)
    return model
