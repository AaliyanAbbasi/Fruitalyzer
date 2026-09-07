#
# import hashlib
# import random
# import re
# from collections import defaultdict
# from pathlib import Path
#
# from PIL import Image
# from torch.utils.data import Dataset, DataLoader
# from torchvision import transforms
#
#
# class FruitQualityDataset(Dataset):
#     """Loads one RGB image and its numeric class label."""
#
#     def __init__(self, samples, transform=None):
#         self.samples = samples
#         self.transform = transform
#
#     def __len__(self):
#         return len(self.samples)
#
#     def __getitem__(self, index):
#         image_path, label, _ = self.samples[index]
#
#         # convert("RGB") keeps grayscale/RGBA files compatible with EfficientNet.
#         with Image.open(image_path) as image:
#             image = image.convert("RGB")
#
#         if self.transform:
#             image = self.transform(image)
#
#         return image, label
#
#
# def file_hash(file_path):
#     """Returns a content hash so exact duplicate files can be detected."""
#     hash_object = hashlib.md5()
#
#     with open(file_path, "rb") as file:
#         for chunk in iter(lambda: file.read(8192), b""):
#             hash_object.update(chunk)
#
#     return hash_object.hexdigest()
#
#
# def get_group_key(file_path):
#     """
#     Groups obvious augmented/copy variants of the same source image.
#
#     Keeping a Roboflow variant and its source image in the same split prevents
#     the model from seeing almost the same photograph in both training and test.
#     The rule intentionally does not remove normal numeric timestamp suffixes.
#     """
#     name = file_path.stem.lower().strip()
#
#     # Roboflow export suffix: image_name.rf.<long hash>
#     name = re.sub(r"\.rf\.[a-f0-9]{16,}$", "", name)
#
#     # Common manually generated augmentation prefixes found in this dataset.
#     prefixes = (
#         "translation_",
#         "saltandpepper_",
#         "rotated_by_30_",
#         "rotated_by_20_",
#         "rotated_by_10_",
#         "rotation_",
#         "flipped_",
#         "brightness_",
#         "contrast_",
#     )
#
#     prefix_removed = True
#     while prefix_removed:
#         prefix_removed = False
#         for prefix in prefixes:
#             if name.startswith(prefix):
#                 name = name[len(prefix):]
#                 prefix_removed = True
#
#     # Windows copy suffixes, without touching real timestamp numbers.
#     name = re.sub(r"\s*-\s*copy(?:\s*\(\d+\))?$", "", name)
#     name = re.sub(r"\s*\(\d{1,2}\)$", "", name)
#
#     return name
#
#
# def resolve_class_folder(dataset_path, dataset_config, fruit, grade):
#     """
#     Converts a logical label such as mango_A into its existing disk folder.
#
#     Example:
#         mango_A -> FruitGrade_Dataset/Mango/Class A
#
#     The actual dataset folders are not renamed, moved or edited.
#     """
#     mapping = dataset_config.get("folder_mapping", {})
#     fruit_mapping = mapping.get(fruit, {})
#
#     fruit_folder = fruit_mapping.get("folder", fruit)
#     grade_folder = fruit_mapping.get("grades", {}).get(grade, grade)
#
#     return dataset_path / fruit_folder / grade_folder
#
#
# def verify_image(file_path):
#     """Checks that Pillow can decode the image without changing the file."""
#     try:
#         with Image.open(file_path) as image:
#             image.verify()
#         return True
#     except (OSError, ValueError):
#         return False
#
#
# def scan_dataset(config):
#     """
#     Reads all configured classes and returns valid, de-duplicated samples.
#
#     Exact duplicates inside one class keep only one copy. If the exact same
#     file exists in different classes, all copies of that hash are excluded
#     because the label is ambiguous and would teach the model contradictory data.
#     """
#     dataset_config = config["dataset"]
#
#     dataset_path = Path(dataset_config["path"])
#     fruits = dataset_config["fruits"]
#     grades = dataset_config["grades"]
#     image_extensions = {extension.lower() for extension in dataset_config["image_extensions"]}
#     min_file_size = dataset_config["min_file_size_bytes"]
#
#     if not dataset_path.exists():
#         raise FileNotFoundError(f"Dataset folder not found: {dataset_path}")
#
#     class_names = []
#     class_to_idx = {}
#     candidates_by_hash = defaultdict(list)
#
#     corrupt_images = []
#     too_small_images = 0
#     unsupported_files = 0
#
#     for fruit in fruits:
#         for grade in grades:
#             class_name = f"{fruit}_{grade}"
#             class_index = len(class_names)
#
#             class_names.append(class_name)
#             class_to_idx[class_name] = class_index
#
#             folder_path = resolve_class_folder(
#                 dataset_path=dataset_path,
#                 dataset_config=dataset_config,
#                 fruit=fruit,
#                 grade=grade,
#             )
#
#             if not folder_path.exists():
#                 raise FileNotFoundError(
#                     f"Missing folder for {class_name}: {folder_path}\n"
#                     "Check dataset.folder_mapping in configs/config.yaml."
#                 )
#
#             for file_path in sorted(folder_path.iterdir()):
#                 if not file_path.is_file():
#                     continue
#
#                 if file_path.suffix.lower() not in image_extensions:
#                     unsupported_files += 1
#                     continue
#
#                 if file_path.stat().st_size < min_file_size:
#                     too_small_images += 1
#                     continue
#
#                 if not verify_image(file_path):
#                     corrupt_images.append(str(file_path))
#                     continue
#
#                 image_hash = file_hash(file_path)
#                 candidates_by_hash[image_hash].append(
#                     {
#                         "path": file_path,
#                         "class_index": class_index,
#                         "class_name": class_name,
#                         "group_key": get_group_key(file_path),
#                     }
#                 )
#
#     samples_by_class = defaultdict(list)
#     duplicate_same_class = 0
#     duplicate_cross_class = []
#
#     for image_hash, records in candidates_by_hash.items():
#         classes_for_hash = {record["class_index"] for record in records}
#
#         if len(classes_for_hash) > 1:
#             duplicate_cross_class.append(
#                 {
#                     "hash": image_hash,
#                     "files": [str(record["path"]) for record in records],
#                     "classes": sorted({record["class_name"] for record in records}),
#                 }
#             )
#             continue
#
#         # Same-class exact duplicates are harmlessly reduced to one sample.
#         first_record = records[0]
#         duplicate_same_class += len(records) - 1
#
#         samples_by_class[first_record["class_index"]].append(
#             (
#                 first_record["path"],
#                 first_record["class_index"],
#                 first_record["group_key"],
#             )
#         )
#
#     total_samples = sum(len(samples) for samples in samples_by_class.values())
#
#     if total_samples == 0:
#         raise ValueError("No valid images found in dataset.")
#
#     print("\nDataset scan report")
#     print("-------------------")
#     for class_name, class_index in class_to_idx.items():
#         class_count = len(samples_by_class[class_index])
#         print(f"{class_name}: {class_count} usable images")
#
#         if class_count == 0:
#             raise ValueError(f"Class has no usable images: {class_name}")
#
#     print(f"\nTotal usable images: {total_samples}")
#     print(f"Same-class exact duplicates skipped: {duplicate_same_class}")
#     print(f"Cross-class duplicate groups excluded: {len(duplicate_cross_class)}")
#     print(f"Corrupt images skipped: {len(corrupt_images)}")
#     print(f"Too-small images skipped: {too_small_images}")
#     print(f"Unsupported files skipped: {unsupported_files}")
#
#     if duplicate_cross_class:
#         print("\nWARNING: Exact same image found in different classes.")
#         print("First 5 ambiguous duplicate groups:")
#         for item in duplicate_cross_class[:5]:
#             print(item)
#
#     if corrupt_images:
#         print("\nFirst 5 corrupt images:")
#         for path in corrupt_images[:5]:
#             print(path)
#
#     return samples_by_class, class_names
#
#
# def stratified_split(samples_by_class, val_split, test_split, seed):
#     """
#     Creates class-balanced train/validation/test splits by related-image group.
#
#     The test set is untouched during training. Grouping prevents obvious
#     augmented variants of one source photograph from leaking across splits.
#     """
#     if val_split < 0 or test_split < 0 or val_split + test_split >= 1:
#         raise ValueError("val_split and test_split must be >= 0 and total less than 1.")
#
#     random_generator = random.Random(seed)
#
#     train_samples = []
#     val_samples = []
#     test_samples = []
#
#     for _, samples in sorted(samples_by_class.items()):
#         groups = defaultdict(list)
#
#         for sample in samples:
#             groups[sample[2]].append(sample)
#
#         grouped_samples = list(groups.values())
#         random_generator.shuffle(grouped_samples)
#
#         total_class_images = len(samples)
#         target_test = round(total_class_images * test_split)
#         target_val = round(total_class_images * val_split)
#
#         class_test = []
#         class_val = []
#         class_train = []
#
#         for group in grouped_samples:
#             if len(class_test) < target_test:
#                 class_test.extend(group)
#             elif len(class_val) < target_val:
#                 class_val.extend(group)
#             else:
#                 class_train.extend(group)
#
#         train_samples.extend(class_train)
#         val_samples.extend(class_val)
#         test_samples.extend(class_test)
#
#     random_generator.shuffle(train_samples)
#     random_generator.shuffle(val_samples)
#     random_generator.shuffle(test_samples)
#
#     return train_samples, val_samples, test_samples
#
#
# def get_train_transform(config):
#     """Mild augmentation suitable for colour/defect-based quality grading."""
#     image_size = config["preprocessing"]["image_size"]
#     mean = config["preprocessing"]["mean"]
#     std = config["preprocessing"]["std"]
#     aug = config["augmentation"]
#
#     transform_list = []
#
#     if aug["random_resized_crop"]["enabled"]:
#         transform_list.append(
#             transforms.RandomResizedCrop(
#                 image_size,
#                 scale=(
#                     aug["random_resized_crop"]["scale_min"],
#                     aug["random_resized_crop"]["scale_max"],
#                 ),
#                 ratio=(0.9, 1.1),
#             )
#         )
#     else:
#         transform_list.append(transforms.Resize((image_size, image_size)))
#
#     if aug["horizontal_flip"]:
#         transform_list.append(transforms.RandomHorizontalFlip(p=0.5))
#
#     transform_list.append(
#         transforms.RandomAffine(
#             degrees=aug["rotation_deg"],
#             translate=(aug.get("translate", 0.0), aug.get("translate", 0.0)),
#         )
#     )
#
#     jitter = aug["color_jitter"]
#     transform_list.append(
#         transforms.ColorJitter(
#             brightness=jitter["brightness"],
#             contrast=jitter["contrast"],
#             saturation=jitter["saturation"],
#             hue=jitter["hue"],
#         )
#     )
#
#     blur = aug["gaussian_blur"]
#     if blur["enabled"]:
#         transform_list.append(
#             transforms.RandomApply(
#                 [
#                     transforms.GaussianBlur(
#                         kernel_size=blur["kernel_size"],
#                         sigma=(blur["sigma_min"], blur["sigma_max"]),
#                     )
#                 ],
#                 p=blur.get("probability", 0.1),
#             )
#         )
#
#     perspective = aug["random_perspective"]
#     if perspective["enabled"]:
#         transform_list.append(
#             transforms.RandomPerspective(
#                 distortion_scale=perspective["distortion_scale"],
#                 p=perspective["probability"],
#             )
#         )
#
#     transform_list.append(transforms.ToTensor())
#     transform_list.append(transforms.Normalize(mean=mean, std=std))
#
#     return transforms.Compose(transform_list)
#
#
# def get_val_transform(config):
#     """Deterministic preprocessing shared by validation, test and inference."""
#     image_size = config["preprocessing"]["image_size"]
#     mean = config["preprocessing"]["mean"]
#     std = config["preprocessing"]["std"]
#
#     return transforms.Compose(
#         [
#             transforms.Resize((image_size, image_size)),
#             transforms.ToTensor(),
#             transforms.Normalize(mean=mean, std=std),
#         ]
#     )
#
#
# def print_split_report(train_samples, val_samples, test_samples, class_names):
#     train_counts = defaultdict(int)
#     val_counts = defaultdict(int)
#     test_counts = defaultdict(int)
#
#     for _, label, _ in train_samples:
#         train_counts[label] += 1
#
#     for _, label, _ in val_samples:
#         val_counts[label] += 1
#
#     for _, label, _ in test_samples:
#         test_counts[label] += 1
#
#     print("\nTrain/Validation/Test split report")
#     print("----------------------------------")
#     for index, class_name in enumerate(class_names):
#         print(
#             f"{class_name}: "
#             f"train={train_counts[index]}, "
#             f"val={val_counts[index]}, "
#             f"test={test_counts[index]}"
#         )
#
#
# def get_dataloaders(config):
#     dataset_config = config["dataset"]
#     training_config = config["training"]
#
#     samples_by_class, class_names = scan_dataset(config)
#
#     train_samples, val_samples, test_samples = stratified_split(
#         samples_by_class=samples_by_class,
#         val_split=dataset_config["val_split"],
#         test_split=dataset_config["test_split"],
#         seed=dataset_config["seed"],
#     )
#
#     print_split_report(train_samples, val_samples, test_samples, class_names)
#
#     train_dataset = FruitQualityDataset(
#         samples=train_samples,
#         transform=get_train_transform(config),
#     )
#
#     val_dataset = FruitQualityDataset(
#         samples=val_samples,
#         transform=get_val_transform(config),
#     )
#
#     test_dataset = FruitQualityDataset(
#         samples=test_samples,
#         transform=get_val_transform(config),
#     )
#
#     train_loader = DataLoader(
#         train_dataset,
#         batch_size=training_config["batch_size"],
#         shuffle=True,
#         num_workers=training_config["num_workers"],
#     )
#
#     val_loader = DataLoader(
#         val_dataset,
#         batch_size=training_config["batch_size"],
#         shuffle=False,
#         num_workers=training_config["num_workers"],
#     )
#
#     test_loader = DataLoader(
#         test_dataset,
#         batch_size=training_config["batch_size"],
#         shuffle=False,
#         num_workers=training_config["num_workers"],
#     )
#
#     return train_loader, val_loader, test_loader, class_names
import hashlib
import random
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


class FruitQualityDataset(Dataset):
    """Loads one image with quality and category targets for one model."""

    def __init__(self, samples, transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, quality_label, category_label, _, _ = self.samples[index]

        with Image.open(image_path) as image:
            image = image.convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, quality_label, category_label


def file_hash(file_path):
    """Returns a content hash so exact duplicate files can be detected."""
    hash_object = hashlib.md5()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hash_object.update(chunk)

    return hash_object.hexdigest()


def get_group_key(file_path):
    """Groups obvious augmented/copy variants to prevent split leakage."""
    name = file_path.stem.lower().strip()

    name = re.sub(r"\.rf\.[a-f0-9]{16,}$", "", name)

    prefixes = (
        "translation_",
        "saltandpepper_",
        "rotated_by_30_",
        "rotated_by_20_",
        "rotated_by_10_",
        "rotation_",
        "flipped_",
        "brightness_",
        "contrast_",
    )

    prefix_removed = True
    while prefix_removed:
        prefix_removed = False
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                prefix_removed = True

    name = re.sub(r"\s*-\s*copy(?:\s*\(\d+\))?$", "", name)
    name = re.sub(r"\s*\(\d{1,2}\)$", "", name)

    return name


def verify_image(file_path):
    """Checks that Pillow can decode the image without changing the file."""
    try:
        with Image.open(file_path) as image:
            image.verify()
        return True
    except (OSError, ValueError):
        return False


def normalize_grade_folder(folder_name):
    """Converts A/Class A style folder names to grade A, B or C."""
    normalized = folder_name.strip().lower().replace("_", " ")
    mapping = {
        "a": "A",
        "class a": "A",
        "b": "B",
        "class b": "B",
        "c": "C",
        "class c": "C",
    }
    return mapping.get(normalized)


def infer_quality_label(file_path, source_folder, fruit, quality_to_idx):
    """
    Uses A/B/C subfolders when present in a new category folder.

    Direct images remain category-only and receive quality index -1. Their
    variety data still trains the category head without inventing grade labels.
    """
    relative_path = file_path.relative_to(source_folder)

    for folder_name in reversed(relative_path.parts[:-1]):
        grade = normalize_grade_folder(folder_name)
        if grade:
            label = f"{fruit}_{grade}"
            if label not in quality_to_idx:
                raise ValueError(f"Unknown inferred quality label: {label}")
            return label

    return None


def scan_dataset(config):
    """
    Scans old graded folders and new variety folders without editing the data.

    Samples use:
      quality index: 0..8, or -1 when a new image has no A/B/C label
      category index: red_apple, green_apple, banana, chaunsa, sindhri, anwar_ratol
    """
    dataset_config = config["dataset"]
    dataset_path = Path(dataset_config["path"])
    quality_names = dataset_config["quality_classes"]
    category_names = dataset_config["category_classes"]
    image_extensions = {
        extension.lower() for extension in dataset_config["image_extensions"]
    }
    min_file_size = dataset_config["min_file_size_bytes"]

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset folder not found: {dataset_path}")

    quality_to_idx = {name: index for index, name in enumerate(quality_names)}
    category_to_idx = {name: index for index, name in enumerate(category_names)}

    candidates_by_hash = defaultdict(list)
    raw_source_counts = defaultdict(int)
    corrupt_images = []
    too_small_images = 0
    unsupported_files = 0

    for source in dataset_config["sources"]:
        source_name = source["name"]
        source_folder = dataset_path / Path(source["folder"])
        fruit = source["fruit"]
        category_name = source["category"]
        fixed_quality_name = source.get("quality_label")
        infer_grade = source.get("infer_grade_from_subfolders", False)

        if category_name not in category_to_idx:
            raise ValueError(f"Unknown category in config: {category_name}")

        if fixed_quality_name is not None and fixed_quality_name not in quality_to_idx:
            raise ValueError(f"Unknown quality label in config: {fixed_quality_name}")

        if not source_folder.exists():
            raise FileNotFoundError(
                f"Missing dataset source '{source_name}': {source_folder}"
            )

        for file_path in sorted(source_folder.rglob("*")):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in image_extensions:
                unsupported_files += 1
                continue

            raw_source_counts[source_name] += 1

            if file_path.stat().st_size < min_file_size:
                too_small_images += 1
                continue

            if not verify_image(file_path):
                corrupt_images.append(str(file_path))
                continue

            quality_name = fixed_quality_name
            if quality_name is None and infer_grade:
                quality_name = infer_quality_label(
                    file_path=file_path,
                    source_folder=source_folder,
                    fruit=fruit,
                    quality_to_idx=quality_to_idx,
                )

            quality_index = (
                quality_to_idx[quality_name] if quality_name is not None else -1
            )
            category_index = category_to_idx[category_name]
            image_hash = file_hash(file_path)

            candidates_by_hash[image_hash].append(
                {
                    "path": file_path,
                    "quality_index": quality_index,
                    "quality_name": quality_name,
                    "category_index": category_index,
                    "category_name": category_name,
                    "source_name": source_name,
                    "group_key": f"{source_name}:{get_group_key(file_path)}",
                }
            )

    samples_by_stratum = defaultdict(list)
    usable_source_counts = defaultdict(int)
    duplicate_same_label = 0
    ambiguous_duplicates = []

    for image_hash, records in candidates_by_hash.items():
        category_indices = {record["category_index"] for record in records}
        labeled_quality_indices = {
            record["quality_index"]
            for record in records
            if record["quality_index"] >= 0
        }

        # Contradictory category or grade labels make the image unsafe.
        if len(category_indices) > 1 or len(labeled_quality_indices) > 1:
            ambiguous_duplicates.append(
                {
                    "hash": image_hash,
                    "files": [str(record["path"]) for record in records],
                    "quality_labels": sorted(
                        {
                            record["quality_name"]
                            for record in records
                            if record["quality_name"] is not None
                        }
                    ),
                    "categories": sorted(
                        {record["category_name"] for record in records}
                    ),
                }
            )
            continue

        # Prefer the record containing a real grade if an unlabeled copy also exists.
        sorted_records = sorted(
            records,
            key=lambda record: record["quality_index"] >= 0,
            reverse=True,
        )
        selected = sorted_records[0]
        duplicate_same_label += len(records) - 1

        stratum_key = (
            selected["source_name"],
            selected["quality_index"],
            selected["category_index"],
        )

        sample = (
            selected["path"],
            selected["quality_index"],
            selected["category_index"],
            selected["group_key"],
            selected["source_name"],
        )
        samples_by_stratum[stratum_key].append(sample)
        usable_source_counts[selected["source_name"]] += 1

    total_samples = sum(len(samples) for samples in samples_by_stratum.values())
    if total_samples == 0:
        raise ValueError("No valid images found in dataset.")

    print("\nDataset scan report")
    print("-------------------")
    for source in dataset_config["sources"]:
        source_name = source["name"]
        print(
            f"{source_name}: raw={raw_source_counts[source_name]}, "
            f"usable={usable_source_counts[source_name]}"
        )

    print(f"\nTotal usable images: {total_samples}")
    print(f"Same-label exact duplicates skipped: {duplicate_same_label}")
    print(f"Ambiguous duplicate groups excluded: {len(ambiguous_duplicates)}")
    print(f"Corrupt images skipped: {len(corrupt_images)}")
    print(f"Too-small images skipped: {too_small_images}")
    print(f"Unsupported files skipped: {unsupported_files}")

    if ambiguous_duplicates:
        print("\nWARNING: Exact image found with contradictory labels.")
        print("First 5 ambiguous duplicate groups:")
        for item in ambiguous_duplicates[:5]:
            print(item)

    if corrupt_images:
        print("\nFirst 5 corrupt images:")
        for path in corrupt_images[:5]:
            print(path)

    return samples_by_stratum, quality_names, category_names


def stratified_split(samples_by_stratum, val_split, test_split, seed):
    """Splits related image groups while preserving every source/label stratum."""
    if val_split < 0 or test_split < 0 or val_split + test_split >= 1:
        raise ValueError("val_split and test_split must total less than 1.")

    random_generator = random.Random(seed)
    train_samples = []
    val_samples = []
    test_samples = []

    for _, samples in sorted(samples_by_stratum.items(), key=lambda item: str(item[0])):
        groups = defaultdict(list)
        for sample in samples:
            groups[sample[3]].append(sample)

        grouped_samples = list(groups.values())
        random_generator.shuffle(grouped_samples)

        total_images = len(samples)
        target_test = round(total_images * test_split)
        target_val = round(total_images * val_split)

        stratum_test = []
        stratum_val = []
        stratum_train = []

        for group in grouped_samples:
            if len(stratum_test) < target_test:
                stratum_test.extend(group)
            elif len(stratum_val) < target_val:
                stratum_val.extend(group)
            else:
                stratum_train.extend(group)

        train_samples.extend(stratum_train)
        val_samples.extend(stratum_val)
        test_samples.extend(stratum_test)

    random_generator.shuffle(train_samples)
    random_generator.shuffle(val_samples)
    random_generator.shuffle(test_samples)

    return train_samples, val_samples, test_samples


def expand_training_categories(train_samples, category_names, targets, seed):
    """
    Adds training-only virtual copies for small new categories.

    Each repeated sample receives a new random transform whenever loaded. No
    image file is created, and validation/test data are never augmented.
    """
    random_generator = random.Random(seed)
    expanded_samples = list(train_samples)
    category_to_idx = {name: index for index, name in enumerate(category_names)}

    print("\nTraining-only category augmentation")
    print("-----------------------------------")

    for category_name, target_count in targets.items():
        if category_name not in category_to_idx:
            raise ValueError(f"Unknown virtual target category: {category_name}")

        category_index = category_to_idx[category_name]
        originals = [
            sample for sample in train_samples if sample[2] == category_index
        ]

        if not originals:
            raise ValueError(
                f"Cannot augment {category_name}: no training samples found."
            )

        before_count = len(originals)
        required = max(0, int(target_count) - before_count)

        for _ in range(required):
            expanded_samples.append(random_generator.choice(originals))

        print(
            f"{category_name}: original_train={before_count}, "
            f"effective_train={before_count + required}"
        )

    random_generator.shuffle(expanded_samples)
    return expanded_samples


def get_train_transform(config):
    """Mild augmentation that preserves colour and surface defect signals."""
    image_size = config["preprocessing"]["image_size"]
    mean = config["preprocessing"]["mean"]
    std = config["preprocessing"]["std"]
    aug = config["augmentation"]

    transform_list = []

    if aug["random_resized_crop"]["enabled"]:
        transform_list.append(
            transforms.RandomResizedCrop(
                image_size,
                scale=(
                    aug["random_resized_crop"]["scale_min"],
                    aug["random_resized_crop"]["scale_max"],
                ),
                ratio=(0.9, 1.1),
            )
        )
    else:
        transform_list.append(transforms.Resize((image_size, image_size)))

    if aug["horizontal_flip"]:
        transform_list.append(transforms.RandomHorizontalFlip(p=0.5))

    transform_list.append(
        transforms.RandomAffine(
            degrees=aug["rotation_deg"],
            translate=(aug.get("translate", 0.0), aug.get("translate", 0.0)),
        )
    )

    jitter = aug["color_jitter"]
    transform_list.append(
        transforms.ColorJitter(
            brightness=jitter["brightness"],
            contrast=jitter["contrast"],
            saturation=jitter["saturation"],
            hue=jitter["hue"],
        )
    )

    blur = aug["gaussian_blur"]
    if blur["enabled"]:
        transform_list.append(
            transforms.RandomApply(
                [
                    transforms.GaussianBlur(
                        kernel_size=blur["kernel_size"],
                        sigma=(blur["sigma_min"], blur["sigma_max"]),
                    )
                ],
                p=blur.get("probability", 0.1),
            )
        )

    transform_list.extend(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )

    return transforms.Compose(transform_list)


def get_val_transform(config):
    """Deterministic preprocessing shared by validation, test and inference."""
    image_size = config["preprocessing"]["image_size"]
    mean = config["preprocessing"]["mean"]
    std = config["preprocessing"]["std"]

    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )


def print_split_report(train_samples, val_samples, test_samples, quality_names, category_names):
    """Prints quality and category distributions before virtual augmentation."""
    quality_counts = {
        "train": defaultdict(int),
        "val": defaultdict(int),
        "test": defaultdict(int),
    }
    category_counts = {
        "train": defaultdict(int),
        "val": defaultdict(int),
        "test": defaultdict(int),
    }

    for split_name, samples in (
        ("train", train_samples),
        ("val", val_samples),
        ("test", test_samples),
    ):
        for _, quality_label, category_label, _, _ in samples:
            if quality_label >= 0:
                quality_counts[split_name][quality_label] += 1
            category_counts[split_name][category_label] += 1

    print("\nQuality split report")
    print("--------------------")
    for index, class_name in enumerate(quality_names):
        print(
            f"{class_name}: train={quality_counts['train'][index]}, "
            f"val={quality_counts['val'][index]}, test={quality_counts['test'][index]}"
        )

    print("\nCategory split report")
    print("---------------------")
    for index, category_name in enumerate(category_names):
        print(
            f"{category_name}: train={category_counts['train'][index]}, "
            f"val={category_counts['val'][index]}, "
            f"test={category_counts['test'][index]}"
        )


def get_dataloaders(config):
    dataset_config = config["dataset"]
    training_config = config["training"]

    samples_by_stratum, quality_names, category_names = scan_dataset(config)

    train_samples, val_samples, test_samples = stratified_split(
        samples_by_stratum=samples_by_stratum,
        val_split=dataset_config["val_split"],
        test_split=dataset_config["test_split"],
        seed=dataset_config["seed"],
    )

    print_split_report(
        train_samples=train_samples,
        val_samples=val_samples,
        test_samples=test_samples,
        quality_names=quality_names,
        category_names=category_names,
    )

    train_samples = expand_training_categories(
        train_samples=train_samples,
        category_names=category_names,
        targets=config["augmentation"].get("virtual_training_targets", {}),
        seed=dataset_config["seed"],
    )

    train_dataset = FruitQualityDataset(
        samples=train_samples,
        transform=get_train_transform(config),
    )
    val_dataset = FruitQualityDataset(
        samples=val_samples,
        transform=get_val_transform(config),
    )
    test_dataset = FruitQualityDataset(
        samples=test_samples,
        transform=get_val_transform(config),
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=training_config["batch_size"],
        shuffle=True,
        num_workers=training_config["num_workers"],
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=training_config["batch_size"],
        shuffle=False,
        num_workers=training_config["num_workers"],
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=training_config["batch_size"],
        shuffle=False,
        num_workers=training_config["num_workers"],
    )

    return train_loader, val_loader, test_loader, quality_names, category_names
