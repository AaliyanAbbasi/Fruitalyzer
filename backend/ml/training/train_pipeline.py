#
# import argparse
# import copy
# import csv
# import json
# import os
# from pathlib import Path
#
# import matplotlib.pyplot as plt
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from sklearn.metrics import classification_report, confusion_matrix
#
# from ml.models.model_builder import (
#     build_model,
#     freeze_backbone,
#     keep_frozen_batch_norm_in_eval,
#     load_checkpoint,
#     save_checkpoint,
# )
# from ml.training.data_loader import get_dataloaders
# from ml.utils.helpers import (
#     ensure_dir,
#     get_device,
#     load_config,
#     save_class_mapping,
#     set_seed,
# )
#
#
# def compute_class_weights(train_loader, num_classes, device):
#     """Computes class weights directly from labels without decoding images."""
#     class_counts = torch.zeros(num_classes)
#
#     for _, label, _ in train_loader.dataset.samples:
#         class_counts[label] += 1
#
#     if torch.any(class_counts == 0):
#         raise ValueError(f"A training class has zero images: {class_counts.tolist()}")
#
#     total_samples = class_counts.sum()
#     weights = total_samples / (num_classes * class_counts)
#
#     print(f"Training class counts: {class_counts.int().tolist()}")
#     print(f"Loss class weights: {[round(value, 4) for value in weights.tolist()]}")
#
#     return weights.to(device)
#
#
# def train_one_epoch(model, train_loader, criterion, optimizer, device):
#     model.train()
#
#     # Frozen BatchNorm layers must not update their running mean/variance.
#     keep_frozen_batch_norm_in_eval(model)
#
#     running_loss = 0.0
#     correct_predictions = 0
#     total_samples = 0
#
#     for images, labels in train_loader:
#         images = images.to(device)
#         labels = labels.to(device)
#
#         optimizer.zero_grad()
#
#         outputs = model(images)
#         loss = criterion(outputs, labels)
#         loss.backward()
#         optimizer.step()
#
#         _, predictions = torch.max(outputs, 1)
#
#         running_loss += loss.item() * images.size(0)
#         correct_predictions += torch.sum(predictions == labels).item()
#         total_samples += labels.size(0)
#
#     epoch_loss = running_loss / total_samples
#     epoch_accuracy = correct_predictions / total_samples
#
#     return epoch_loss, epoch_accuracy
#
#
# def validate_one_epoch(model, data_loader, criterion, device):
#     model.eval()
#
#     running_loss = 0.0
#     correct_predictions = 0
#     total_samples = 0
#
#     with torch.no_grad():
#         for images, labels in data_loader:
#             images = images.to(device)
#             labels = labels.to(device)
#
#             outputs = model(images)
#             loss = criterion(outputs, labels)
#
#             _, predictions = torch.max(outputs, 1)
#
#             running_loss += loss.item() * images.size(0)
#             correct_predictions += torch.sum(predictions == labels).item()
#             total_samples += labels.size(0)
#
#     epoch_loss = running_loss / total_samples
#     epoch_accuracy = correct_predictions / total_samples
#
#     return epoch_loss, epoch_accuracy
#
#
# def save_metrics_csv(metrics_history, metrics_path):
#     ensure_dir(Path(metrics_path).parent)
#
#     with open(metrics_path, "w", newline="") as file:
#         writer = csv.DictWriter(
#             file,
#             fieldnames=[
#                 "stage",
#                 "epoch",
#                 "train_loss",
#                 "train_accuracy",
#                 "val_loss",
#                 "val_accuracy",
#                 "learning_rate",
#             ],
#         )
#
#         writer.writeheader()
#         writer.writerows(metrics_history)
#
#
# def run_training_stage(
#     stage_name,
#     model,
#     train_loader,
#     val_loader,
#     criterion,
#     device,
#     learning_rate,
#     weight_decay,
#     epochs,
#     patience,
#     scheduler_config,
#     class_names,
#     checkpoint_path,
#     config,
#     metrics_history,
#     best_tracker,
# ):
#     """Runs one simple training stage with early stopping and best saving."""
#     trainable_parameters = [
#         parameter for parameter in model.parameters() if parameter.requires_grad
#     ]
#
#     optimizer = optim.Adam(
#         trainable_parameters,
#         lr=learning_rate,
#         weight_decay=weight_decay,
#     )
#
#     scheduler = optim.lr_scheduler.ReduceLROnPlateau(
#         optimizer,
#         mode="max",
#         factor=scheduler_config["factor"],
#         patience=scheduler_config["patience"],
#     )
#
#     epochs_without_improvement = 0
#
#     # ============================================================
#     # FRUITALYZER TRAINING: STAGE-SPECIFIC EARLY STOPPING
#     # Purpose:
#     # Track improvement inside the current stage separately from the
#     # best model found across all stages. This allows Stage 2 to keep
#     # training while it is improving, even before it beats Stage 1.
#     # ============================================================
#     stage_best_accuracy = -1.0
#
#     print(f"\n{stage_name} started")
#     print("-" * len(f"{stage_name} started"))
#
#     for epoch in range(1, epochs + 1):
#         train_loss, train_accuracy = train_one_epoch(
#             model=model,
#             train_loader=train_loader,
#             criterion=criterion,
#             optimizer=optimizer,
#             device=device,
#         )
#
#         val_loss, val_accuracy = validate_one_epoch(
#             model=model,
#             data_loader=val_loader,
#             criterion=criterion,
#             device=device,
#         )
#
#         scheduler.step(val_accuracy)
#         current_lr = optimizer.param_groups[0]["lr"]
#
#         epoch_metrics = {
#             "stage": stage_name,
#             "epoch": epoch,
#             "train_loss": round(train_loss, 4),
#             "train_accuracy": round(train_accuracy, 4),
#             "val_loss": round(val_loss, 4),
#             "val_accuracy": round(val_accuracy, 4),
#             "learning_rate": current_lr,
#         }
#
#         metrics_history.append(epoch_metrics)
#
#         print(
#             f"{stage_name} | Epoch {epoch}/{epochs} | "
#             f"Train Loss: {train_loss:.4f} | "
#             f"Train Acc: {train_accuracy:.4f} | "
#             f"Val Loss: {val_loss:.4f} | "
#             f"Val Acc: {val_accuracy:.4f} | "
#             f"LR: {current_lr:.8f}"
#         )
#
#         # ============================================================
#         # FRUITALYZER TRAINING: CURRENT-STAGE IMPROVEMENT
#         # Purpose:
#         # Early stopping should depend on whether this stage is improving,
#         # not only on whether it has already beaten the previous stage.
#         # ============================================================
#         if val_accuracy > stage_best_accuracy:
#             stage_best_accuracy = val_accuracy
#             epochs_without_improvement = 0
#         else:
#             epochs_without_improvement += 1
#
#         # ============================================================
#         # FRUITALYZER TRAINING: GLOBAL BEST CHECKPOINT
#         # Purpose:
#         # Save only the best validation model found across both stages.
#         # Stage-specific improvement controls patience; global improvement
#         # controls which checkpoint becomes the final production candidate.
#         # ============================================================
#         if val_accuracy > best_tracker["accuracy"]:
#             best_tracker["accuracy"] = val_accuracy
#             best_tracker["weights"] = copy.deepcopy(model.state_dict())
#             best_tracker["stage"] = stage_name
#             best_tracker["epoch"] = epoch
#
#             save_checkpoint(
#                 model=model,
#                 optimizer=optimizer,
#                 epoch=epoch,
#                 metrics=epoch_metrics,
#                 class_names=class_names,
#                 save_path=checkpoint_path,
#                 config=config,
#                 stage=stage_name,
#             )
#
#             print(f"Best temporary checkpoint saved. Val Accuracy: {val_accuracy:.4f}")
#
#         save_metrics_csv(metrics_history, config["paths"]["metrics_path"])
#
#         if epochs_without_improvement >= patience:
#             print(f"Early stopping triggered in {stage_name}.")
#             break
#
#     return model
#
#
# def evaluate_test_set(
#     model,
#     test_loader,
#     criterion,
#     device,
#     class_names,
#     config,
# ):
#     """Evaluates the final best model on the untouched test set."""
#     model.eval()
#
#     total_loss = 0.0
#     total_samples = 0
#     all_labels = []
#     all_predictions = []
#
#     with torch.no_grad():
#         for images, labels in test_loader:
#             images = images.to(device)
#             labels = labels.to(device)
#
#             outputs = model(images)
#             loss = criterion(outputs, labels)
#             predictions = torch.argmax(outputs, dim=1)
#
#             total_loss += loss.item() * images.size(0)
#             total_samples += labels.size(0)
#             all_labels.extend(labels.cpu().tolist())
#             all_predictions.extend(predictions.cpu().tolist())
#
#     test_loss = total_loss / total_samples
#     test_accuracy = sum(
#         prediction == label
#         for prediction, label in zip(all_predictions, all_labels)
#     ) / total_samples
#
#     report_dictionary = classification_report(
#         all_labels,
#         all_predictions,
#         labels=list(range(len(class_names))),
#         target_names=class_names,
#         output_dict=True,
#         zero_division=0,
#     )
#
#     report_text = classification_report(
#         all_labels,
#         all_predictions,
#         labels=list(range(len(class_names))),
#         target_names=class_names,
#         zero_division=0,
#     )
#
#     test_metrics = {
#         "test_loss": round(test_loss, 4),
#         "test_accuracy": round(test_accuracy, 4),
#         "macro_precision": round(report_dictionary["macro avg"]["precision"], 4),
#         "macro_recall": round(report_dictionary["macro avg"]["recall"], 4),
#         "macro_f1": round(report_dictionary["macro avg"]["f1-score"], 4),
#         "weighted_f1": round(report_dictionary["weighted avg"]["f1-score"], 4),
#     }
#
#     ensure_dir(Path(config["paths"]["test_metrics_path"]).parent)
#
#     with open(config["paths"]["test_metrics_path"], "w") as file:
#         json.dump(test_metrics, file, indent=4)
#
#     with open(config["paths"]["classification_report_path"], "w") as file:
#         file.write(report_text)
#
#     matrix = confusion_matrix(
#         all_labels,
#         all_predictions,
#         labels=list(range(len(class_names))),
#     )
#
#     figure, axis = plt.subplots(figsize=(10, 8))
#     image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
#     figure.colorbar(image, ax=axis)
#
#     axis.set(
#         xticks=range(len(class_names)),
#         yticks=range(len(class_names)),
#         xticklabels=class_names,
#         yticklabels=class_names,
#         ylabel="True class",
#         xlabel="Predicted class",
#         title="Fruitalyzer Test Confusion Matrix",
#     )
#
#     plt.setp(axis.get_xticklabels(), rotation=45, ha="right")
#
#     threshold = matrix.max() / 2.0 if matrix.size else 0
#     for row in range(matrix.shape[0]):
#         for column in range(matrix.shape[1]):
#             axis.text(
#                 column,
#                 row,
#                 str(matrix[row, column]),
#                 ha="center",
#                 va="center",
#                 color="white" if matrix[row, column] > threshold else "black",
#             )
#
#     figure.tight_layout()
#     figure.savefig(config["paths"]["confusion_matrix_path"], dpi=160)
#     plt.close(figure)
#
#     print("\nFinal untouched test results")
#     print("----------------------------")
#     for key, value in test_metrics.items():
#         print(f"{key}: {value}")
#
#     return test_metrics
#
#
# def main():
#     parser = argparse.ArgumentParser(
#         description="Train the Fruitalyzer nine-class EfficientNet-B0 model."
#     )
#     parser.add_argument(
#         "--check-only",
#         action="store_true",
#         help="Validate folders, labels, splits, one image batch and 9-output model, then stop.",
#     )
#     arguments = parser.parse_args()
#
#     config = load_config("configs/config.yaml")
#
#     set_seed(config["dataset"]["seed"])
#     device = get_device(config["training"]["device"])
#
#     save_dir = config["paths"]["save_dir"]
#     final_model_path = Path(config["paths"]["model_path"])
#     class_mapping_path = config["paths"]["class_mapping_path"]
#
#     # Train into a temporary checkpoint. The currently working model remains
#     # untouched until the complete nine-class run and test evaluation succeed.
#     temporary_model_path = final_model_path.with_name(
#         f"{final_model_path.stem}.training{final_model_path.suffix}"
#     )
#
#     ensure_dir(save_dir)
#
#     print(f"Using device: {device}")
#     print("\nLoading and validating dataset...")
#     train_loader, val_loader, test_loader, class_names = get_dataloaders(config)
#
#     num_classes = len(class_names)
#
#     print("\nClasses discovered from config and folders:")
#     for index, class_name in enumerate(class_names):
#         print(f"{index}: {class_name}")
#
#     if num_classes != 9:
#         raise ValueError(
#             f"Expected 9 classes for apple, banana and mango, but found {num_classes}."
#         )
#
#     if arguments.check_only:
#         # This fast check uses an untrained model only to verify tensor shapes.
#         # It does not download pretrained weights and does not change saved files.
#         images, labels = next(iter(train_loader))
#         check_model = build_model(
#             num_classes=num_classes,
#             pretrained=False,
#             dropout_rate=config["model"]["dropout_rate"],
#         )
#
#         with torch.no_grad():
#             outputs = check_model(images)
#
#         print("\nCheck-only results")
#         print("------------------")
#         print(f"Image batch shape: {tuple(images.shape)}")
#         print(f"Label batch shape: {tuple(labels.shape)}")
#         print(f"Model output shape: {tuple(outputs.shape)}")
#
#         if outputs.shape[1] != 9:
#             raise ValueError(f"Model must output 9 classes, got {outputs.shape[1]}.")
#
#         print("CHECK PASSED: dataset and nine-class model setup are ready.")
#         return
#
#     print("\nBuilding ImageNet-pretrained EfficientNet-B0...")
#     model = build_model(
#         num_classes=num_classes,
#         pretrained=config["model"]["pretrained"],
#         dropout_rate=config["model"]["dropout_rate"],
#     )
#     model = model.to(device)
#
#     class_weights = compute_class_weights(
#         train_loader=train_loader,
#         num_classes=num_classes,
#         device=device,
#     )
#
#     criterion = nn.CrossEntropyLoss(
#         weight=class_weights,
#         label_smoothing=config["training"]["label_smoothing"],
#     )
#
#     metrics_history = []
#     best_tracker = {
#         "accuracy": 0.0,
#         "weights": copy.deepcopy(model.state_dict()),
#         "stage": None,
#         "epoch": 0,
#     }
#
#     # Stage 1: freeze the complete EfficientNet feature extractor and learn
#     # only the new classifier that maps features to the nine fruit-grade labels.
#     model = freeze_backbone(
#         model=model,
#         freeze_blocks=len(model.features),
#         freeze_batch_norm=config["model"]["freeze_batch_norm"],
#     )
#
#     model = run_training_stage(
#         stage_name="stage1_head",
#         model=model,
#         train_loader=train_loader,
#         val_loader=val_loader,
#         criterion=criterion,
#         device=device,
#         learning_rate=config["training"]["stage1"]["learning_rate"],
#         weight_decay=config["training"]["weight_decay"],
#         epochs=config["training"]["stage1"]["epochs"],
#         patience=config["training"]["stage1"]["patience"],
#         scheduler_config=config["training"]["scheduler"],
#         class_names=class_names,
#         checkpoint_path=temporary_model_path,
#         config=config,
#         metrics_history=metrics_history,
#         best_tracker=best_tracker,
#     )
#
#     # Stage 2 starts from the best stage-1 weights and fine-tunes only the
#     # later EfficientNet blocks using a much smaller learning rate.
#     model.load_state_dict(best_tracker["weights"])
#     model = freeze_backbone(
#         model=model,
#         freeze_blocks=config["model"]["freeze_blocks"],
#         freeze_batch_norm=config["model"]["freeze_batch_norm"],
#     )
#
#     model = run_training_stage(
#         stage_name="stage2_finetune",
#         model=model,
#         train_loader=train_loader,
#         val_loader=val_loader,
#         criterion=criterion,
#         device=device,
#         learning_rate=config["training"]["stage2"]["learning_rate"],
#         weight_decay=config["training"]["weight_decay"],
#         epochs=config["training"]["stage2"]["epochs"],
#         patience=config["training"]["stage2"]["patience"],
#         scheduler_config=config["training"]["scheduler"],
#         class_names=class_names,
#         checkpoint_path=temporary_model_path,
#         config=config,
#         metrics_history=metrics_history,
#         best_tracker=best_tracker,
#     )
#
#     if not temporary_model_path.exists():
#         raise RuntimeError("Training ended without creating a valid checkpoint.")
#
#     # Reload exactly the checkpoint that achieved the best validation score.
#     best_model = build_model(
#         num_classes=num_classes,
#         pretrained=False,
#         dropout_rate=config["model"]["dropout_rate"],
#     ).to(device)
#
#     best_model = load_checkpoint(
#         model=best_model,
#         checkpoint_path=temporary_model_path,
#         device=device,
#     )
#
#     evaluate_test_set(
#         model=best_model,
#         test_loader=test_loader,
#         criterion=criterion,
#         device=device,
#         class_names=class_names,
#         config=config,
#     )
#
#     # Only after the complete successful run do we replace the old model and
#     # mapping together. At the end there is still one production model.
#     os.replace(temporary_model_path, final_model_path)
#     save_class_mapping(class_names, class_mapping_path)
#
#     print("\nTraining completed successfully.")
#     print(f"Best validation accuracy: {best_tracker['accuracy']:.4f}")
#     print(f"Best stage: {best_tracker['stage']}, epoch: {best_tracker['epoch']}")
#     print(f"Production model saved at: {final_model_path}")
#     print(f"Class mapping saved at: {class_mapping_path}")
#     print(f"Training metrics saved at: {config['paths']['metrics_path']}")
#     print(f"Test metrics saved at: {config['paths']['test_metrics_path']}")
#     print(f"Classification report saved at: {config['paths']['classification_report_path']}")
#     print(f"Confusion matrix saved at: {config['paths']['confusion_matrix_path']}")
#
#
# if __name__ == "__main__":
#     main()
import argparse
import copy
import csv
import json
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import classification_report, confusion_matrix

from ml.models.model_builder import (
    build_model,
    configure_training_stage,
    keep_frozen_batch_norm_in_eval,
    load_checkpoint,
    load_existing_quality_weights,
    save_checkpoint,
)
from ml.training.data_loader import get_dataloaders
from ml.utils.helpers import (
    ensure_dir,
    get_device,
    load_config,
    save_class_mapping,
    set_seed,
)


def compute_class_weights(train_loader, num_quality_classes, num_category_classes, device):
    """Computes separate loss weights for quality and category targets."""
    quality_counts = torch.zeros(num_quality_classes)
    category_counts = torch.zeros(num_category_classes)

    for _, quality_label, category_label, _, _ in train_loader.dataset.samples:
        if quality_label >= 0:
            quality_counts[quality_label] += 1
        category_counts[category_label] += 1

    if torch.any(quality_counts == 0):
        raise ValueError(
            f"A quality class has zero training images: {quality_counts.tolist()}"
        )

    if torch.any(category_counts == 0):
        raise ValueError(
            f"A category class has zero training images: {category_counts.tolist()}"
        )

    quality_weights = quality_counts.sum() / (
        num_quality_classes * quality_counts
    )
    category_weights = category_counts.sum() / (
        num_category_classes * category_counts
    )

    print(f"Quality training counts: {quality_counts.int().tolist()}")
    print(
        "Quality loss weights: "
        f"{[round(value, 4) for value in quality_weights.tolist()]}"
    )
    print(f"Category training counts: {category_counts.int().tolist()}")
    print(
        "Category loss weights: "
        f"{[round(value, 4) for value in category_weights.tolist()]}"
    )

    return quality_weights.to(device), category_weights.to(device)


def compute_batch_loss(
    quality_outputs,
    category_outputs,
    quality_labels,
    category_labels,
    quality_criterion,
    category_criterion,
    quality_loss_weight,
    category_loss_weight,
):
    """Masks missing grades while always learning the category label."""
    quality_mask = quality_labels >= 0

    if quality_mask.any() and quality_loss_weight > 0:
        quality_loss = quality_criterion(
            quality_outputs[quality_mask],
            quality_labels[quality_mask],
        )
    else:
        quality_loss = torch.zeros((), device=quality_outputs.device)

    category_loss = category_criterion(category_outputs, category_labels)

    total_loss = (
        quality_loss_weight * quality_loss
        + category_loss_weight * category_loss
    )

    return total_loss, quality_loss, category_loss


def update_accuracy_counts(
    counters,
    quality_outputs,
    category_outputs,
    quality_labels,
    category_labels,
):
    quality_predictions = torch.argmax(quality_outputs, dim=1)
    category_predictions = torch.argmax(category_outputs, dim=1)
    quality_mask = quality_labels >= 0

    if quality_mask.any():
        counters["quality_correct"] += (
            quality_predictions[quality_mask] == quality_labels[quality_mask]
        ).sum().item()
        counters["quality_total"] += quality_mask.sum().item()

        counters["combined_correct"] += (
            (quality_predictions[quality_mask] == quality_labels[quality_mask])
            & (category_predictions[quality_mask] == category_labels[quality_mask])
        ).sum().item()
        counters["combined_total"] += quality_mask.sum().item()

    counters["category_correct"] += (
        category_predictions == category_labels
    ).sum().item()
    counters["category_total"] += category_labels.size(0)


def finalize_epoch_metrics(total_loss, total_samples, counters):
    return {
        "loss": total_loss / max(total_samples, 1),
        "quality_accuracy": counters["quality_correct"]
        / max(counters["quality_total"], 1),
        "category_accuracy": counters["category_correct"]
        / max(counters["category_total"], 1),
        "combined_accuracy": counters["combined_correct"]
        / max(counters["combined_total"], 1),
    }


def run_one_epoch(
    model,
    data_loader,
    quality_criterion,
    category_criterion,
    device,
    quality_loss_weight,
    category_loss_weight,
    optimizer=None,
):
    """Runs one train or validation epoch for both model heads."""
    is_training = optimizer is not None

    if is_training:
        model.train()
        keep_frozen_batch_norm_in_eval(model)
    else:
        model.eval()

    total_loss = 0.0
    total_samples = 0
    counters = defaultdict(int)

    context = torch.enable_grad() if is_training else torch.no_grad()

    with context:
        for images, quality_labels, category_labels in data_loader:
            images = images.to(device)
            quality_labels = quality_labels.to(device)
            category_labels = category_labels.to(device)

            if is_training:
                optimizer.zero_grad()

            quality_outputs, category_outputs = model(images)

            loss, _, _ = compute_batch_loss(
                quality_outputs=quality_outputs,
                category_outputs=category_outputs,
                quality_labels=quality_labels,
                category_labels=category_labels,
                quality_criterion=quality_criterion,
                category_criterion=category_criterion,
                quality_loss_weight=quality_loss_weight,
                category_loss_weight=category_loss_weight,
            )

            if is_training:
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            total_samples += images.size(0)

            update_accuracy_counts(
                counters=counters,
                quality_outputs=quality_outputs,
                category_outputs=category_outputs,
                quality_labels=quality_labels,
                category_labels=category_labels,
            )

    return finalize_epoch_metrics(total_loss, total_samples, counters)


def save_metrics_csv(metrics_history, metrics_path):
    ensure_dir(Path(metrics_path).parent)

    fieldnames = [
        "stage",
        "epoch",
        "train_loss",
        "train_quality_accuracy",
        "train_category_accuracy",
        "train_combined_accuracy",
        "val_loss",
        "val_quality_accuracy",
        "val_category_accuracy",
        "val_combined_accuracy",
        "selection_score",
        "learning_rate",
    ]

    with open(metrics_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics_history)


def calculate_selection_score(val_metrics, selection_weights):
    """Balances preservation of grading with improvement in category accuracy."""
    return (
        selection_weights["quality"] * val_metrics["quality_accuracy"]
        + selection_weights["category"] * val_metrics["category_accuracy"]
    )


def run_training_stage(
    stage_name,
    model,
    train_loader,
    val_loader,
    quality_criterion,
    category_criterion,
    device,
    learning_rate,
    weight_decay,
    epochs,
    patience,
    scheduler_config,
    loss_weights,
    selection_weights,
    class_names,
    category_names,
    checkpoint_path,
    config,
    metrics_history,
    best_tracker,
):
    """Runs one stage with stage-specific patience and global best saving."""
    trainable_parameters = [
        parameter for parameter in model.parameters() if parameter.requires_grad
    ]

    if not trainable_parameters:
        raise ValueError(f"No trainable parameters found for {stage_name}.")

    optimizer = optim.Adam(
        trainable_parameters,
        lr=learning_rate,
        weight_decay=weight_decay,
    )

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=scheduler_config["factor"],
        patience=scheduler_config["patience"],
    )

    epochs_without_improvement = 0
    stage_best_score = -1.0

    print(f"\n{stage_name} started")
    print("-" * len(f"{stage_name} started"))

    for epoch in range(1, epochs + 1):
        train_metrics = run_one_epoch(
            model=model,
            data_loader=train_loader,
            quality_criterion=quality_criterion,
            category_criterion=category_criterion,
            device=device,
            quality_loss_weight=loss_weights["quality"],
            category_loss_weight=loss_weights["category"],
            optimizer=optimizer,
        )

        val_metrics = run_one_epoch(
            model=model,
            data_loader=val_loader,
            quality_criterion=quality_criterion,
            category_criterion=category_criterion,
            device=device,
            quality_loss_weight=loss_weights["quality"],
            category_loss_weight=loss_weights["category"],
            optimizer=None,
        )

        selection_score = calculate_selection_score(
            val_metrics=val_metrics,
            selection_weights=selection_weights,
        )

        scheduler.step(selection_score)
        current_lr = optimizer.param_groups[0]["lr"]

        epoch_metrics = {
            "stage": stage_name,
            "epoch": epoch,
            "train_loss": round(train_metrics["loss"], 4),
            "train_quality_accuracy": round(
                train_metrics["quality_accuracy"], 4
            ),
            "train_category_accuracy": round(
                train_metrics["category_accuracy"], 4
            ),
            "train_combined_accuracy": round(
                train_metrics["combined_accuracy"], 4
            ),
            "val_loss": round(val_metrics["loss"], 4),
            "val_quality_accuracy": round(val_metrics["quality_accuracy"], 4),
            "val_category_accuracy": round(val_metrics["category_accuracy"], 4),
            "val_combined_accuracy": round(val_metrics["combined_accuracy"], 4),
            "selection_score": round(selection_score, 4),
            "learning_rate": current_lr,
        }
        metrics_history.append(epoch_metrics)

        print(
            f"{stage_name} | Epoch {epoch}/{epochs} | "
            f"Train Loss: {train_metrics['loss']:.4f} | "
            f"Train Quality: {train_metrics['quality_accuracy']:.4f} | "
            f"Train Category: {train_metrics['category_accuracy']:.4f} | "
            f"Val Loss: {val_metrics['loss']:.4f} | "
            f"Val Quality: {val_metrics['quality_accuracy']:.4f} | "
            f"Val Category: {val_metrics['category_accuracy']:.4f} | "
            f"Val Combined: {val_metrics['combined_accuracy']:.4f} | "
            f"Score: {selection_score:.4f} | LR: {current_lr:.8f}"
        )

        if selection_score > stage_best_score:
            stage_best_score = selection_score
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if selection_score > best_tracker["score"]:
            best_tracker["score"] = selection_score
            best_tracker["weights"] = copy.deepcopy(model.state_dict())
            best_tracker["stage"] = stage_name
            best_tracker["epoch"] = epoch
            best_tracker["quality_accuracy"] = val_metrics["quality_accuracy"]
            best_tracker["category_accuracy"] = val_metrics["category_accuracy"]

            save_checkpoint(
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                metrics=epoch_metrics,
                class_names=class_names,
                category_names=category_names,
                save_path=checkpoint_path,
                config=config,
                stage=stage_name,
            )

            print(
                "Best temporary multitask checkpoint saved. "
                f"Score: {selection_score:.4f}"
            )

        save_metrics_csv(metrics_history, config["paths"]["metrics_path"])

        if epochs_without_improvement >= patience:
            print(f"Early stopping triggered in {stage_name}.")
            break

    return model


def save_confusion_matrix(matrix, labels, path, title):
    figure, axis = plt.subplots(figsize=(10, 8))
    image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
    figure.colorbar(image, ax=axis)

    axis.set(
        xticks=range(len(labels)),
        yticks=range(len(labels)),
        xticklabels=labels,
        yticklabels=labels,
        ylabel="True class",
        xlabel="Predicted class",
        title=title,
    )

    plt.setp(axis.get_xticklabels(), rotation=45, ha="right")

    threshold = matrix.max() / 2.0 if matrix.size else 0
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            axis.text(
                column,
                row,
                str(matrix[row, column]),
                ha="center",
                va="center",
                color="white" if matrix[row, column] > threshold else "black",
            )

    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def evaluate_test_set(
    model,
    test_loader,
    quality_criterion,
    category_criterion,
    device,
    quality_names,
    category_names,
    config,
):
    """Evaluates grading on labeled data and category recognition on all data."""
    model.eval()

    quality_true = []
    quality_pred = []
    category_true = []
    category_pred = []
    combined_correct = 0
    combined_total = 0
    total_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for images, quality_labels, category_labels in test_loader:
            images = images.to(device)
            quality_labels = quality_labels.to(device)
            category_labels = category_labels.to(device)

            quality_outputs, category_outputs = model(images)
            loss, _, _ = compute_batch_loss(
                quality_outputs=quality_outputs,
                category_outputs=category_outputs,
                quality_labels=quality_labels,
                category_labels=category_labels,
                quality_criterion=quality_criterion,
                category_criterion=category_criterion,
                quality_loss_weight=1.0,
                category_loss_weight=1.0,
            )

            quality_predictions = torch.argmax(quality_outputs, dim=1)
            category_predictions = torch.argmax(category_outputs, dim=1)
            quality_mask = quality_labels >= 0

            if quality_mask.any():
                quality_true.extend(quality_labels[quality_mask].cpu().tolist())
                quality_pred.extend(quality_predictions[quality_mask].cpu().tolist())
                combined_correct += (
                    (quality_predictions[quality_mask] == quality_labels[quality_mask])
                    & (category_predictions[quality_mask] == category_labels[quality_mask])
                ).sum().item()
                combined_total += quality_mask.sum().item()

            category_true.extend(category_labels.cpu().tolist())
            category_pred.extend(category_predictions.cpu().tolist())

            total_loss += loss.item() * images.size(0)
            total_samples += images.size(0)

    quality_report_dict = classification_report(
        quality_true,
        quality_pred,
        labels=list(range(len(quality_names))),
        target_names=quality_names,
        output_dict=True,
        zero_division=0,
    )
    quality_report_text = classification_report(
        quality_true,
        quality_pred,
        labels=list(range(len(quality_names))),
        target_names=quality_names,
        zero_division=0,
    )

    category_report_dict = classification_report(
        category_true,
        category_pred,
        labels=list(range(len(category_names))),
        target_names=category_names,
        output_dict=True,
        zero_division=0,
    )
    category_report_text = classification_report(
        category_true,
        category_pred,
        labels=list(range(len(category_names))),
        target_names=category_names,
        zero_division=0,
    )

    test_metrics = {
        "test_loss": round(total_loss / max(total_samples, 1), 4),
        "quality_accuracy": round(quality_report_dict["accuracy"], 4),
        "quality_macro_f1": round(
            quality_report_dict["macro avg"]["f1-score"], 4
        ),
        "category_accuracy": round(category_report_dict["accuracy"], 4),
        "category_macro_f1": round(
            category_report_dict["macro avg"]["f1-score"], 4
        ),
        "combined_accuracy_on_graded_images": round(
            combined_correct / max(combined_total, 1), 4
        ),
        "graded_test_images": combined_total,
        "all_category_test_images": len(category_true),
    }

    ensure_dir(Path(config["paths"]["test_metrics_path"]).parent)

    with open(config["paths"]["test_metrics_path"], "w") as file:
        json.dump(test_metrics, file, indent=4)

    with open(config["paths"]["classification_report_path"], "w") as file:
        file.write(quality_report_text)

    with open(config["paths"]["category_classification_report_path"], "w") as file:
        file.write(category_report_text)

    quality_matrix = confusion_matrix(
        quality_true,
        quality_pred,
        labels=list(range(len(quality_names))),
    )
    category_matrix = confusion_matrix(
        category_true,
        category_pred,
        labels=list(range(len(category_names))),
    )

    save_confusion_matrix(
        matrix=quality_matrix,
        labels=quality_names,
        path=config["paths"]["confusion_matrix_path"],
        title="Fruitalyzer Quality Confusion Matrix",
    )
    save_confusion_matrix(
        matrix=category_matrix,
        labels=category_names,
        path=config["paths"]["category_confusion_matrix_path"],
        title="Fruitalyzer Category Confusion Matrix",
    )

    print("\nFinal untouched test results")
    print("----------------------------")
    for key, value in test_metrics.items():
        print(f"{key}: {value}")

    return test_metrics


def main():
    parser = argparse.ArgumentParser(
        description="Train one EfficientNet for quality and fruit category."
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate data and both output shapes, then stop.",
    )
    arguments = parser.parse_args()

    config = load_config("configs/config.yaml")
    set_seed(config["dataset"]["seed"])
    device = get_device(config["training"]["device"])

    save_dir = config["paths"]["save_dir"]
    final_model_path = Path(config["paths"]["model_path"])
    temporary_model_path = final_model_path.with_name(
        f"{final_model_path.stem}.training{final_model_path.suffix}"
    )

    ensure_dir(save_dir)

    print(f"Using device: {device}")
    print("\nLoading and validating quality + category dataset...")

    (
        train_loader,
        val_loader,
        test_loader,
        quality_names,
        category_names,
    ) = get_dataloaders(config)

    if len(quality_names) != 9:
        raise ValueError(f"Expected 9 quality classes, found {len(quality_names)}.")

    if len(category_names) != 6:
        raise ValueError(f"Expected 6 categories, found {len(category_names)}.")

    print("\nQuality labels:")
    for index, name in enumerate(quality_names):
        print(f"{index}: {name}")

    print("\nCategory labels:")
    for index, name in enumerate(category_names):
        print(f"{index}: {name}")

    if arguments.check_only:
        images, quality_labels, category_labels = next(iter(train_loader))
        check_model = build_model(
            num_classes=len(quality_names),
            num_category_classes=len(category_names),
            pretrained=False,
            dropout_rate=config["model"]["dropout_rate"],
        )

        with torch.no_grad():
            quality_outputs, category_outputs = check_model(images)

        print("\nCheck-only results")
        print("------------------")
        print(f"Image batch shape: {tuple(images.shape)}")
        print(f"Quality label shape: {tuple(quality_labels.shape)}")
        print(f"Category label shape: {tuple(category_labels.shape)}")
        print(f"Quality output shape: {tuple(quality_outputs.shape)}")
        print(f"Category output shape: {tuple(category_outputs.shape)}")

        if quality_outputs.shape[1] != 9:
            raise ValueError("Quality head must output 9 classes.")

        if category_outputs.shape[1] != 6:
            raise ValueError("Category head must output 6 classes.")

        print("CHECK PASSED: one EfficientNet is ready for quality + category.")
        return

    # Build without ImageNet download because the existing trained 9-class
    # checkpoint already contains the EfficientNet backbone weights.
    model = build_model(
        num_classes=len(quality_names),
        num_category_classes=len(category_names),
        pretrained=False,
        dropout_rate=config["model"]["dropout_rate"],
    ).to(device)

    if config["model"].get("initialize_from_existing_quality_model", True):
        model = load_existing_quality_weights(
            model=model,
            checkpoint_path=final_model_path,
            device=device,
        )

    quality_weights, category_weights = compute_class_weights(
        train_loader=train_loader,
        num_quality_classes=len(quality_names),
        num_category_classes=len(category_names),
        device=device,
    )

    quality_criterion = nn.CrossEntropyLoss(
        weight=quality_weights,
        label_smoothing=config["training"]["label_smoothing"],
    )
    category_criterion = nn.CrossEntropyLoss(
        weight=category_weights,
        label_smoothing=config["training"]["label_smoothing"],
    )

    metrics_history = []
    best_tracker = {
        "score": -1.0,
        "weights": copy.deepcopy(model.state_dict()),
        "stage": None,
        "epoch": 0,
        "quality_accuracy": 0.0,
        "category_accuracy": 0.0,
    }

    model = configure_training_stage(
        model=model,
        stage_name="stage1_category_head",
        freeze_blocks=config["model"]["freeze_blocks"],
        freeze_batch_norm=config["model"]["freeze_batch_norm"],
    )

    model = run_training_stage(
        stage_name="stage1_category_head",
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        quality_criterion=quality_criterion,
        category_criterion=category_criterion,
        device=device,
        learning_rate=config["training"]["stage1"]["learning_rate"],
        weight_decay=config["training"]["weight_decay"],
        epochs=config["training"]["stage1"]["epochs"],
        patience=config["training"]["stage1"]["patience"],
        scheduler_config=config["training"]["scheduler"],
        loss_weights={
            "quality": config["training"]["stage1"]["quality_loss_weight"],
            "category": config["training"]["stage1"]["category_loss_weight"],
        },
        selection_weights=config["training"]["selection_weights"],
        class_names=quality_names,
        category_names=category_names,
        checkpoint_path=temporary_model_path,
        config=config,
        metrics_history=metrics_history,
        best_tracker=best_tracker,
    )

    model.load_state_dict(best_tracker["weights"])
    model = configure_training_stage(
        model=model,
        stage_name="stage2_multitask_finetune",
        freeze_blocks=config["model"]["freeze_blocks"],
        freeze_batch_norm=config["model"]["freeze_batch_norm"],
    )

    model = run_training_stage(
        stage_name="stage2_multitask_finetune",
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        quality_criterion=quality_criterion,
        category_criterion=category_criterion,
        device=device,
        learning_rate=config["training"]["stage2"]["learning_rate"],
        weight_decay=config["training"]["weight_decay"],
        epochs=config["training"]["stage2"]["epochs"],
        patience=config["training"]["stage2"]["patience"],
        scheduler_config=config["training"]["scheduler"],
        loss_weights={
            "quality": config["training"]["stage2"]["quality_loss_weight"],
            "category": config["training"]["stage2"]["category_loss_weight"],
        },
        selection_weights=config["training"]["selection_weights"],
        class_names=quality_names,
        category_names=category_names,
        checkpoint_path=temporary_model_path,
        config=config,
        metrics_history=metrics_history,
        best_tracker=best_tracker,
    )

    if not temporary_model_path.exists():
        raise RuntimeError("Training ended without creating a valid checkpoint.")

    best_model = build_model(
        num_classes=len(quality_names),
        num_category_classes=len(category_names),
        pretrained=False,
        dropout_rate=config["model"]["dropout_rate"],
    ).to(device)

    best_model = load_checkpoint(
        model=best_model,
        checkpoint_path=temporary_model_path,
        device=device,
    )

    evaluate_test_set(
        model=best_model,
        test_loader=test_loader,
        quality_criterion=quality_criterion,
        category_criterion=category_criterion,
        device=device,
        quality_names=quality_names,
        category_names=category_names,
        config=config,
    )

    # The proven old model stays active until both training and test evaluation
    # finish. Only then is it replaced by the successful single multitask model.
    os.replace(temporary_model_path, final_model_path)
    save_class_mapping(quality_names, config["paths"]["class_mapping_path"])
    save_class_mapping(category_names, config["paths"]["category_mapping_path"])

    print("\nTraining completed successfully.")
    print(f"Best selection score: {best_tracker['score']:.4f}")
    print(
        f"Best validation quality accuracy: "
        f"{best_tracker['quality_accuracy']:.4f}"
    )
    print(
        f"Best validation category accuracy: "
        f"{best_tracker['category_accuracy']:.4f}"
    )
    print(f"Best stage: {best_tracker['stage']}, epoch: {best_tracker['epoch']}")
    print(f"Production model saved at: {final_model_path}")
    print(f"Quality mapping saved at: {config['paths']['class_mapping_path']}")
    print(f"Category mapping saved at: {config['paths']['category_mapping_path']}")


if __name__ == "__main__":
    main()
