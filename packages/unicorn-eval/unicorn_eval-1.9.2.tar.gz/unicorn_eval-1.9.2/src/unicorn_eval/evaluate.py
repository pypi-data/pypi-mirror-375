#  Copyright 2025 Diagnostic Image Analysis Group, Radboudumc, Nijmegen, The Netherlands
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import copy
import gc
import json
import logging
import multiprocessing
import random
from pathlib import Path
from pprint import pformat

import numpy as np
import openslide
import pandas as pd
import SimpleITK as sitk
from dragon_eval import DragonEval
from dragon_eval.evaluation import REGRESSION_EPSILON, TASK_TYPE, EvalType

from unicorn_eval.helpers import get_max_workers
from unicorn_eval.utils import (
    adapt_features,
    evaluate_predictions,
    extract_data,
    extract_embeddings_and_labels,
    normalize_metric,
    write_json_file,
)

INPUT_DIRECTORY = Path("/input")
OUTPUT_DIRECTORY = Path("/output")
GROUNDTRUTH_DIRECTORY = Path("/opt/ml/input/data/ground_truth")


ADAPTOR_SLUGS_DICT = {
    "Task01_classifying_he_prostate_biopsies_into_isup_scores": "adaptor-pathology-classification",
    "Task02_classifying_lung_nodule_malignancy_in_ct": "adaptor-radiology-classification",
    "Task03_predicting_the_time_to_biochemical_recurrence_in_he_prostatectomies": "adaptor-pathology-regression",
    "Task04_predicting_slide_level_tumor_proportion_score_in_ihc_stained_wsi": "adaptor-pathology-classification",
    "Task05_detecting_signet_ring_cells_in_he_stained_wsi_of_gastric_cancer": "adaptor-pathology-detection",
    "Task06_detecting_clinically_significant_prostate_cancer_in_mri_exams": "adaptor-radiology-detection-segmentation",
    "Task07_detecting_lung_nodules_in_thoracic_ct": "adaptor-radiology-detection-points",
    "Task08_detecting_mitotic_figures_in_breast_cancer_wsis": "adaptor-pathology-detection",
    "Task09_segmenting_rois_in_breast_cancer_wsis": "adaptor-pathology-segmentation",
    "Task10_segmenting_lesions_within_vois_in_ct": "adaptor-radiology-segmentation",
    "Task11_segmenting_three_anatomical_structures_in_lumbar_spine_mri": "adaptor-radiology-segmentation",
}

REQUIRES_PROBABILITIES_DICT = {
    "Task01_classifying_he_prostate_biopsies_into_isup_scores": False,
    "Task02_classifying_lung_nodule_malignancy_in_ct": True,
    "Task03_predicting_the_time_to_biochemical_recurrence_in_he_prostatectomies": False,
    "Task04_predicting_slide_level_tumor_proportion_score_in_ihc_stained_wsi": False,
    "Task05_detecting_signet_ring_cells_in_he_stained_wsi_of_gastric_cancer": False,
    "Task06_detecting_clinically_significant_prostate_cancer_in_mri_exams": False,
    "Task07_detecting_lung_nodules_in_thoracic_ct": False,
    "Task08_detecting_mitotic_figures_in_breast_cancer_wsis": False,
    "Task09_segmenting_rois_in_breast_cancer_wsis": False,
    "Task10_segmenting_lesions_within_vois_in_ct": False,
    "Task11_segmenting_three_anatomical_structures_in_lumbar_spine_mri": False,
}

INPUT_SLUGS_DICT = {
    "Task01_classifying_he_prostate_biopsies_into_isup_scores": [
        "prostate-tissue-biopsy-whole-slide-image"
    ],
    "Task02_classifying_lung_nodule_malignancy_in_ct": [
        "chest-ct-region-of-interest-cropout"
    ],
    "Task03_predicting_the_time_to_biochemical_recurrence_in_he_prostatectomies": [
        "prostatectomy-tissue-whole-slide-image"
    ],
    "Task04_predicting_slide_level_tumor_proportion_score_in_ihc_stained_wsi": [
        "ihc-staining-for-pd-l1"
    ],
    "Task05_detecting_signet_ring_cells_in_he_stained_wsi_of_gastric_cancer": [
        "histopathology-region-of-interest-cropout"
    ],
    "Task06_detecting_clinically_significant_prostate_cancer_in_mri_exams": [
        "transverse-t2-prostate-mri",
    ],
    "Task07_detecting_lung_nodules_in_thoracic_ct": [
        "chest-ct",
    ],
    "Task08_detecting_mitotic_figures_in_breast_cancer_wsis": [
        "histopathology-region-of-interest-cropout"
    ],
    "Task09_segmenting_rois_in_breast_cancer_wsis": [
        "histopathology-region-of-interest-cropout"
    ],
    "Task10_segmenting_lesions_within_vois_in_ct": ["stacked-3d-ct-volumes-of-lesions"],
    "Task11_segmenting_three_anatomical_structures_in_lumbar_spine_mri": [
        "sagittal-spine-mri"
    ],
    "Task20_generating_caption_from_wsi": ["he-staining"],
}

MODEL_OUTPUT_SLUG_DICT = {
    "Task01_classifying_he_prostate_biopsies_into_isup_scores": "image-neural-representation",
    "Task02_classifying_lung_nodule_malignancy_in_ct": "image-neural-representation",
    "Task03_predicting_the_time_to_biochemical_recurrence_in_he_prostatectomies": "image-neural-representation",
    "Task04_predicting_slide_level_tumor_proportion_score_in_ihc_stained_wsi": "image-neural-representation",
    "Task05_detecting_signet_ring_cells_in_he_stained_wsi_of_gastric_cancer": "patch-neural-representation",
    "Task06_detecting_clinically_significant_prostate_cancer_in_mri_exams": "patch-neural-representation",
    "Task07_detecting_lung_nodules_in_thoracic_ct": "patch-neural-representation",
    "Task08_detecting_mitotic_figures_in_breast_cancer_wsis": "patch-neural-representation",
    "Task09_segmenting_rois_in_breast_cancer_wsis": "patch-neural-representation",
    "Task10_segmenting_lesions_within_vois_in_ct": "patch-neural-representation",
    "Task11_segmenting_three_anatomical_structures_in_lumbar_spine_mri": "patch-neural-representation",
    "Task20_generating_caption_from_wsi": "nlp-predictions-dataset",
}

LABEL_SLUG_DICT = {
    "Task01_classifying_he_prostate_biopsies_into_isup_scores": "isup-grade.json",
    "Task02_classifying_lung_nodule_malignancy_in_ct": "lung-nodule-malignancy-risk.json",
    "Task03_predicting_the_time_to_biochemical_recurrence_in_he_prostatectomies": "overall-survival-years.json",
    "Task04_predicting_slide_level_tumor_proportion_score_in_ihc_stained_wsi": "pd-l1-tps-binned.json",
    "Task05_detecting_signet_ring_cells_in_he_stained_wsi_of_gastric_cancer": "cell-classification.json",
    "Task06_detecting_clinically_significant_prostate_cancer_in_mri_exams": "images/transverse-cspca-label/{case_id}.mha",
    "Task07_detecting_lung_nodules_in_thoracic_ct": "nodule-locations.json",
    "Task08_detecting_mitotic_figures_in_breast_cancer_wsis": "mitotic-figures.json",
    "Task09_segmenting_rois_in_breast_cancer_wsis": "images/tumor-stroma-and-other/{case_id}.tif",
    "Task10_segmenting_lesions_within_vois_in_ct": "images/ct-binary-uls/{case_id}.mha",
    "Task11_segmenting_three_anatomical_structures_in_lumbar_spine_mri": "images/sagittal-spine-mr-segmentation/{case_id}.mha",
    "Task20_generating_caption_from_wsi": "nlp-predictions-dataset.json",
}

EXTRA_LABEL_SLUG_DICT = {
    "Task03_predicting_the_time_to_biochemical_recurrence_in_he_prostatectomies": [
        "event.json",
        "cohort.json",
    ],
    "Task07_detecting_lung_nodules_in_thoracic_ct": ["diameter.json"],
}

LANGUAGE_TASK_NAMES = [
    "Task12_predicting_histopathology_sample_origin",
    "Task13_classifying_pulmonary_nodule_presence",
    "Task14_classifying_kidney_abnormality",
    "Task15_hip_kellgren_lawrence_score",
    "Task16_classifying_colon_histopathology_diagnosis",
    "Task17_predicting_lesion_size_measurements",
    "Task18_predicting_prostate_volume_psa_and_psa_density",
    "Task19_anonymizing_report",
]

TASK_TYPE.update(
    {
        "Task12_predicting_histopathology_sample_origin": EvalType.NONORDINAL_MULTI_CLASS_CLASSIFICATION,
        "Task13_classifying_pulmonary_nodule_presence": EvalType.BINARY_CLASSIFICATION,
        "Task14_classifying_kidney_abnormality": EvalType.BINARY_CLASSIFICATION,
        "Task15_hip_kellgren_lawrence_score": EvalType.NONORDINAL_MULTI_CLASS_CLASSIFICATION,
        "Task16_classifying_colon_histopathology_diagnosis": EvalType.BINARY_CLASSIFICATION_NON_SHARED_TASK,
        "Task17_predicting_lesion_size_measurements": EvalType.REGRESSION,
        "Task18_predicting_prostate_volume_psa_and_psa_density": EvalType.REGRESSION,
        "Task19_anonymizing_report": EvalType.TEXT_TARGET,
    }
)

REGRESSION_EPSILON.update(
    {
        "Task17_predicting_lesion_size_measurements": 4,
        "Task18_predicting_prostate_volume_psa_and_psa_density": np.array(
            [4, 0.4, 0.04]
        ),
    }
)


def process(job):
    """Processes a single algorithm job, looking at the outputs"""

    embeddings = None
    prediction = None
    coordinates = None
    spacing = None
    patch_size = None
    patch_spacing = None
    image_size = None
    image_spacing = None
    image_origin = None
    image_direction = None
    feature_grid_resolution = None

    report = "Processing:\n"
    report += pformat(job)
    report += "\n"

    mapping_path = GROUNDTRUTH_DIRECTORY / "mapping.csv"
    try:
        mapping = pd.read_csv(
            mapping_path, dtype={"case_id": str}
        )  # ensure case_id is string to enable leading zeros
    except FileNotFoundError:
        # if the mapping file is not found, we assume that the evaluation is for a language task
        # and we do not need the mapping
        logging.error(f"{mapping_path} not found, cannot group by task.")
        return {}

    image_name = None
    for slug_inputs in INPUT_SLUGS_DICT.values():
        for slug_input in slug_inputs:
            try:
                image_name = get_image_name(
                    values=job["inputs"],
                    slug=slug_input,
                )
            except Exception as e:
                continue

    if image_name is None:
        # if no image_name is found, it corresponds to a pure language task
        # for which we already have written the metrics
        return None

    case_name = Path(image_name).stem

    # remove suffixes "_adc", "_t2w", and "_hbv" from the case name if present
    for suffix in ["_adc", "_t2w", "_hbv"]:
        if case_name.endswith(suffix):
            case_name = case_name[: -len(suffix)]

    case_info = mapping[mapping.case_id == case_name]
    if case_info.empty:
        raise ValueError(f"Case {case_name} not found in mapping.")

    task_name = case_info.task_name.values[0]
    modality = case_info.modality.values[0]

    if modality == "vision":

        prediction = None
        slug_embedding = MODEL_OUTPUT_SLUG_DICT[task_name]

        # find the location of the results
        location_neural_representation = get_file_location(
            job_pk=job["pk"],
            values=job["outputs"],
            slug=slug_embedding,
        )

        # read the results
        neural_representations = load_json_file(
            location=location_neural_representation,
        )

        features = []
        if slug_embedding == "image-neural-representation":
            for neural_representation in neural_representations:
                feature = neural_representation["features"]
                feature = np.array(feature).astype(np.float32)
                features.append(feature)
            embeddings = np.concatenate(features)

        elif slug_embedding == "patch-neural-representation":
            # TODO: better handle the case when there are multiple encoded inputs for a case
            # right now we concatenate the features
            # and use the first coordinates, spacing, patch_size, image_size, and image_spacing
            first = True
            for neural_representation in neural_representations:
                (
                    feature,
                    curr_coordinates,
                    curr_spacing,
                    curr_patch_size,
                    curr_patch_spacing,
                    curr_feature_grid_resolution,
                    curr_image_size,
                    curr_image_spacing,
                    curr_image_origin,
                    curr_image_direction,
                ) = extract_data(neural_representation)
                features.append(feature)
                if first:
                    coordinates = curr_coordinates
                    spacing = curr_spacing
                    patch_size = curr_patch_size
                    patch_spacing = curr_patch_spacing
                    feature_grid_resolution = curr_feature_grid_resolution
                    image_size = curr_image_size
                    image_spacing = curr_image_spacing
                    image_origin = curr_image_origin
                    image_direction = curr_image_direction
                    first = False
                else:
                    assert np.all(
                        coordinates == curr_coordinates
                    ), "Coordinates do not match between images of the same case"
                    assert np.all(
                        spacing == curr_spacing
                    ), "Spacing does not match between images of the same case"
                    assert np.all(
                        patch_size == curr_patch_size
                    ), "Patch size does not match between images of the same case"
                    assert np.all(
                        patch_spacing == curr_patch_spacing
                    ), "Patch spacing does not match between images of the same case"
                    assert np.all(
                        image_size == curr_image_size
                    ), "Image size does not match between images of the same case"
                    assert np.all(
                        image_spacing == curr_image_spacing
                    ), "Image spacing does not match between images of the same case"
                    assert np.all(
                        image_origin == curr_image_origin
                    ), "Image origin does not match between images of the same case"
                    assert np.all(
                        image_direction == curr_image_direction
                    ), "Image direction does not match between images of the same case"
            embeddings = np.concatenate(features)

    elif modality == "vision-language":

        model_output_slug = MODEL_OUTPUT_SLUG_DICT[task_name]

        # find the location of the results
        location_prediction = get_file_location(
            job_pk=job["pk"],
            values=job["outputs"],
            slug=model_output_slug,
        )

        # read the results
        prediction = load_json_file(
            location=location_prediction,
        )[0]

    case_specific_ground_truth_dir = GROUNDTRUTH_DIRECTORY / task_name / case_name

    slug_label = LABEL_SLUG_DICT[task_name]
    label_path = case_specific_ground_truth_dir / slug_label

    label_size, label_origin, label_spacing, label_direction = None, None, None, None
    if label_path.suffix == ".json":
        label = load_json_file(location=label_path)
    elif label_path.suffix == ".tif":
        label_path = Path(str(label_path).replace("{case_id}", case_name))
        label = load_tif_file(location=label_path)
    elif label_path.suffix == ".mha":
        label_path = Path(str(label_path).replace("{case_id}", case_name))
        label, label_size, label_origin, label_spacing, label_direction = load_mha_file(
            path=label_path,
        )
    else:
        raise ValueError(f"Unsupported file format: {label_path.suffix}")

    extra_labels = None
    extra_slug_labels = EXTRA_LABEL_SLUG_DICT.get(task_name, [])
    use_extra_labels = len(extra_slug_labels) > 0
    if use_extra_labels:
        extra_labels = {}
        for extra_slug_label in extra_slug_labels:
            slug_name = Path(extra_slug_label).stem
            extra_label_path = case_specific_ground_truth_dir / extra_slug_label
            if extra_label_path.exists():
                extra_labels[slug_name] = load_json_file(location=extra_label_path)
            else:
                logging.warning(f"extra label file not found: {extra_label_path}")
                extra_labels[slug_name] = None

        # convert extra_labels dictionary to a structured numpy array
        dtype = [(key, type(value)) for key, value in extra_labels.items()]
        extra_labels = np.array([tuple(extra_labels.values())], dtype=dtype)

    case_info_dict = case_info.to_dict(orient="records")[0]
    case_info_dict["embeddings"] = embeddings
    case_info_dict["coordinates"] = coordinates
    case_info_dict["spacing"] = spacing
    case_info_dict["image_spacing"] = image_spacing
    case_info_dict["image_size"] = image_size
    case_info_dict["image_origin"] = image_origin
    case_info_dict["image_direction"] = image_direction
    case_info_dict["patch_size"] = patch_size
    case_info_dict["patch_spacing"] = patch_spacing
    case_info_dict["feature_grid_resolution"] = feature_grid_resolution
    case_info_dict["prediction"] = prediction
    case_info_dict["label"] = label
    case_info_dict["extra_labels"] = extra_labels
    case_info_dict["label_spacing"] = label_spacing
    case_info_dict["label_size"] = label_size
    case_info_dict["label_origin"] = label_origin
    case_info_dict["label_direction"] = label_direction

    return case_info_dict


def print_directory_contents(path: Path | str):
    path = Path(path)
    for child in path.iterdir():
        if child.is_dir():
            print_directory_contents(child)
        else:
            logging.info(str(child))


def read_adaptors():
    # read the adaptors that are used for this submission
    adaptors = {}
    for task_name, slug in ADAPTOR_SLUGS_DICT.items():
        adaptor_path = INPUT_DIRECTORY / f"{slug}.json"
        if adaptor_path.exists():
            with open(adaptor_path) as f:
                adaptors[task_name] = json.loads(f.read())
    return adaptors


def read_predictions(input_dir: Path, case_names: list[str]):
    # the prediction file tells us the location of the users' predictions
    with open(input_dir / "predictions.json") as f:
        predictions = json.loads(f.read())

    filtered_predictions = []
    for prediction in predictions:
        case_name = None
        for slug_inputs in INPUT_SLUGS_DICT.values():
            for slug_input in slug_inputs:
                try:
                    image_name = get_image_name(
                        values=prediction["inputs"], slug=slug_input
                    )
                    case_name = Path(image_name).stem
                    # remove suffixes "_adc", "_t2w", and "_hbv" from the case name if present
                    for suffix in ["_adc", "_t2w", "_hbv", "_tissue"]:
                        if case_name.endswith(suffix):
                            case_name = case_name[: -len(suffix)]
                    break
                except Exception:
                    continue
            if case_name:
                break

        if case_name is None:
            # skip if we can't determine case name (language task)
            continue
        if case_name in case_names:
            filtered_predictions.append(prediction)

    # free up memory
    del predictions
    gc.collect()

    return filtered_predictions


def get_image_name(*, values, slug):
    # this tells us the user-provided name of the input or output image
    for value in values:
        if value["interface"]["slug"] == slug:
            return value["image"]["name"]

    raise RuntimeError(f"Image with interface {slug} not found!")


def get_interface_relative_path(*, values, slug):
    # gets the location of the interface relative to the input or output
    for value in values:
        if value["interface"]["slug"] == slug:
            return value["interface"]["relative_path"]

    raise RuntimeError(f"Value with interface {slug} not found!")


def get_file_location(*, job_pk, values, slug):
    # where a job's output file will be located in the evaluation container
    relative_path = get_interface_relative_path(values=values, slug=slug)
    return INPUT_DIRECTORY / job_pk / "output" / relative_path


def load_json_file(*, location):
    # reads a json file
    with open(location) as f:
        return json.loads(f.read())


def load_tif_file(*, location):
    slide = openslide.OpenSlide(location)
    logging.info(f"Image dimensions: {slide.dimensions}")
    level_0 = slide.read_region((0, 0), 0, slide.dimensions)
    #   save_tif(level_0, location.stem)
    level_0_np = np.array(level_0)
    class_labels = level_0_np[:, :, 0]  # shape: (H, W)
    return class_labels


def load_mha_file(*, path: Path | str):
    class_labels = sitk.ReadImage(str(path))

    if class_labels is None:
        raise ValueError("Failed to load class labels from MHA file.")

    return (
        sitk.GetArrayFromImage(class_labels),
        list(class_labels.GetSize()),
        list(class_labels.GetOrigin()),
        list(class_labels.GetSpacing()),
        list(class_labels.GetDirection()),
    )


def write_combined_metrics(
    *, metric_dict: dict[str, dict], save_predictions: bool = True
) -> None:
    metrics = {"metrics": {}, "normalized_metrics": {}}
    predictions = {"predictions": []}

    for task_name, task_metrics in metric_dict.items():
        for metric_name, metric_value in task_metrics["metrics"].items():
            task_identifier = task_name.split("_")[0]
            metrics["metrics"][f"{task_identifier}_{metric_name}"] = metric_value
            metrics["normalized_metrics"][f"{task_identifier}_{metric_name}"] = (
                normalize_metric(task_name, metric_value)
            )

        for metric_name, metric_value in task_metrics.get(
            "additional_metrics", {}
        ).items():
            task_identifier = task_name.split("_")[0]
            metrics["metrics"][f"{task_identifier}_{metric_name}"] = metric_value

        if save_predictions:
            case_prediction = [
                p.tolist() if isinstance(p, np.ndarray) else p
                for p in task_metrics["predictions"]
            ]
            predictions["predictions"].extend(case_prediction)

    # aggregate metrics when there are multiple tasks
    metrics["metrics"]["mean"] = np.mean(
        [metric_value for _, metric_value in metrics["normalized_metrics"].items()]
    )

    logging.info(f"metrics={metrics}")
    write_json_file(
        location=OUTPUT_DIRECTORY / "metrics.json",
        content=metrics,
    )

    if save_predictions:
        write_json_file(
            location=OUTPUT_DIRECTORY / "predictions.json",
            content=predictions,
        )


def reformat_language_metrics(metrics: dict) -> dict:
    """
    Reformat the language metrics to match the expected format for write_combined_metrics.
    """
    # If empty, return an empty dictionary
    if not metrics:
        return {}
    else:
        return {
            task: {"metrics": {task: values["mean"]}}
            for task, values in metrics["aggregates"].items()
            if task != "overall"
        }


def prepare_predictions_language(input_dir: Path, output_dir: Path, gt_dir: Path):
    """
    Map the predictions with random filenames to the correct task and fold.

    New behavior:
    - If a prediction file matches a GT task except for a few missing cases:
        * If missing <= 5% of that task's total UIDs, we fill the gaps by
          duplicating a randomly chosen existing prediction and replacing only
          the 'uid' field with each missing UID.
        * If missing > 5%, we raise a ValueError.
    - If a prediction file contains UIDs not present in the matched GT task,
      we warn and skip that file.
    """
    task_uids = {}
    logging.info(f"Scanning ground truth directory: {gt_dir}")
    for gt_file in gt_dir.rglob("*.json"):
        if any(task_name in str(gt_file) for task_name in LANGUAGE_TASK_NAMES):
            with open(gt_file, "r") as f:
                entries = json.load(f)
            matched_task = next(
                task for task in LANGUAGE_TASK_NAMES if task in str(gt_file)
            )
            uids = set(entry["uid"] for entry in entries)
            task_uids[matched_task] = uids
            logging.info(
                f"→ Found GT task '{matched_task}' with {len(uids)} UIDs from {gt_file}"
            )

    for pred_file in input_dir.rglob("*/output/nlp-predictions-dataset.json"):
        if pred_file.name in ["predictions.json", "inputs.json"]:
            continue

        logging.info(f"\nProcessing prediction file: {pred_file}")
        with open(pred_file, "r") as f:
            entries = json.load(f)

        uids = set(entry["uid"] for entry in entries)
        matched = False

        for task, gt_uids in task_uids.items():
            # Only proceed if all predicted UIDs are part of this GT task.
            extra_uids = uids - gt_uids
            if extra_uids:
                # This prediction file cannot belong to this task.
                continue

            # Check how many are missing vs GT.
            missing_uids = gt_uids - uids
            total_gt = len(gt_uids)

            if not missing_uids and uids == gt_uids:
                # Perfect match
                output_file = (
                    output_dir / f"{task}-fold0" / "nlp-predictions-dataset.json"
                )
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w") as f:
                    json.dump(entries, f)
                logging.info(
                    f"✓ Matched to task '{task}', wrote {len(entries)} entries → {output_file}"
                )
                matched = True
                break

            # If we reach here, there are no extra UIDs, but some may be missing.
            if missing_uids:
                missing_ratio = len(missing_uids) / float(total_gt)
                percent = round(missing_ratio * 100, 3)

                if missing_ratio > 0.05:
                    # Too many missing → error
                    raise ValueError(
                        f"Prediction file {pred_file} matched task '{task}' but is missing "
                        f"{len(missing_uids)}/{total_gt} UIDs ({percent}%), which exceeds the 5% threshold."
                    )

                # Fill small gaps by duplicating a random existing prediction and replacing only the 'uid'.
                logging.info(
                    f"• '{task}' missing {len(missing_uids)}/{total_gt} UIDs ({percent}%). "
                    f"Filling gaps by duplicating random predictions."
                )
                if not entries:
                    raise ValueError(
                        f"Cannot fill missing UIDs for {pred_file}: no existing entries to sample from."
                    )

                for missing_uid in missing_uids:
                    template = copy.deepcopy(random.choice(entries))
                    template["uid"] = missing_uid
                    entries.append(template)

                # Sanity: now we should match exactly
                final_uids = set(e["uid"] for e in entries)
                assert (
                    final_uids == gt_uids
                ), "Internal error: after gap-filling, UIDs still do not match GT."

                output_file = (
                    output_dir / f"{task}-fold0" / "nlp-predictions-dataset.json"
                )
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w") as f:
                    json.dump(entries, f)
                logging.info(
                    f"✓ Matched to task '{task}' after filling, wrote {len(entries)} entries → {output_file}"
                )
                matched = True
                break

        if not matched:
            logging.info(
                f"⚠ No matching ground truth found for {pred_file} "
                f"(either extra UIDs present or task mismatch). "
                f"Pred UID count = {len(uids)}"
            )


def evaluate_language_predictions():
    input_dir = (
        INPUT_DIRECTORY
        if INPUT_DIRECTORY.exists()
        else Path("unicorn/test-predictions")
    )
    # Make a temp folder
    temp_metric_output_path = Path("/opt/app/predictions/language_results/metrics.json")
    temp_metric_output_path.parent.mkdir(parents=True, exist_ok=True)
    workdir = (
        Path("/opt/app/predictions")
        if Path("/opt/app/predictions").exists()
        else Path("unicorn/workdir")
    )
    prepare_predictions_language(
        input_dir=input_dir,
        output_dir=workdir,
        gt_dir=GROUNDTRUTH_DIRECTORY,
    )

    # determine which task we are evaluating
    files = list(GROUNDTRUTH_DIRECTORY.glob("*.json"))
    task_names = [
        path.stem.replace(".json", "")
        for path in files
        if path.stem.replace(".json", "") in LANGUAGE_TASK_NAMES
    ]

    if task_names:
        # evaluate
        DragonEval(
            ground_truth_path=GROUNDTRUTH_DIRECTORY,
            predictions_path=workdir,
            output_file=temp_metric_output_path,
            folds=[0],
            tasks=task_names,
        ).evaluate()

        # load the metrics
        with open(temp_metric_output_path, "r") as f:
            return json.load(f)

    else:
        logging.info("No language tasks found in the ground truth files.")
        return {}


def process_task_in_subprocess(
    task_name, mapping, adaptors, save_predictions, metrics_path
):
    logging.info(f"Processing task in subprocess: {task_name}")

    # identify task cases to filter predictions
    task_case_names = mapping[mapping["task_name"] == task_name]["case_id"].tolist()
    task_predictions = read_predictions(
        input_dir=INPUT_DIRECTORY, case_names=task_case_names
    )

    # process the task's predictions in parallel
    max_workers = get_max_workers()
    pool = multiprocessing.Pool(processes=max_workers)
    processed_results = pool.map(process, task_predictions)
    pool.close()
    pool.join()

    task_results = extract_embeddings_and_labels(processed_results, task_name)
    del task_predictions
    del processed_results
    gc.collect()

    if task_results is None:
        logging.info(f"No results found for task {task_name}, skipping.")
        logging.info("=+=" * 10)

    else:

        modality = task_results["modality"]
        case_labels = task_results["case_labels"]
        case_ids = task_results["case_ids"]
        task_type = task_results["task_type"]

        if modality == "vision":

            # ensure we have an adaptor for this task
            if task_name not in adaptors:
                raise Exception(f"No adaptor found for task {task_name}")

            adaptor_name = adaptors[task_name]
            return_probabilities = REQUIRES_PROBABILITIES_DICT[task_name]

            global_patch_size = task_results["global_patch_size"]
            global_patch_spacing = task_results["global_patch_spacing"]
            feature_grid_resolution = task_results["feature_grid_resolution"]

            shot_embeddings = task_results["shot_embeddings"]
            shot_labels = task_results["shot_labels"]
            shot_extra_labels = task_results["shot_extra_labels"]
            shot_ids = task_results["shot_ids"]
            shot_image_sizes = task_results["shot_image_sizes"]
            shot_image_spacings = task_results["shot_image_spacings"]
            shot_image_origins = task_results["shot_image_origins"]
            shot_image_directions = task_results["shot_image_directions"]
            shot_patch_sizes = task_results["shot_patch_sizes"]
            shot_patch_spacings = task_results["shot_patch_spacings"]
            shot_label_spacings = task_results["shot_label_spacings"]
            shot_label_origins = task_results["shot_label_origins"]
            shot_label_directions = task_results["shot_label_directions"]

            case_embeddings = task_results["case_embeddings"]
            case_extra_labels = task_results["case_extra_labels"]
            case_image_sizes = task_results["cases_image_sizes"]
            case_image_spacings = task_results["cases_image_spacings"]
            case_image_origins = task_results["cases_image_origins"]
            case_image_directions = task_results["cases_image_directions"]
            case_patch_sizes = task_results["cases_patch_sizes"]
            case_patch_spacings = task_results["cases_patch_spacings"]
            case_label_sizes = task_results["cases_label_sizes"]
            case_label_spacings = task_results["cases_label_spacings"]
            case_label_origins = task_results["cases_label_origins"]
            case_label_directions = task_results["cases_label_directions"]

            if task_type in ["classification", "regression"]:
                save_predictions = True
                if len(shot_embeddings.shape) > 2:
                    shot_embeddings = shot_embeddings.squeeze(1)
                if len(case_embeddings.shape) > 2:
                    case_embeddings = case_embeddings.squeeze(1)

            predictions = adapt_features(
                adaptor_name=adaptor_name,
                task_type=task_type,
                shot_features=shot_embeddings,
                shot_names=shot_ids,
                shot_labels=shot_labels,
                test_features=case_embeddings,
                shot_coordinates=task_results["shot_coordinates"],
                test_coordinates=task_results["cases_coordinates"],
                test_names=case_ids,
                global_patch_size=global_patch_size,
                global_patch_spacing=global_patch_spacing,
                shot_patch_sizes=shot_patch_sizes,
                test_patch_sizes=case_patch_sizes,
                shot_patch_spacings=shot_patch_spacings,
                test_patch_spacings=case_patch_spacings,
                feature_grid_resolution=feature_grid_resolution,
                test_image_sizes=case_image_sizes,
                shot_extra_labels=shot_extra_labels,
                test_image_spacing=case_image_spacings,
                test_image_origins=case_image_origins,
                test_image_directions=case_image_directions,
                test_label_spacing=case_label_spacings,
                test_label_origins=case_label_origins,
                test_label_directions=case_label_directions,
                test_label_sizes=case_label_sizes,
                shot_image_sizes=shot_image_sizes,
                shot_image_spacing=shot_image_spacings,
                shot_image_origins=shot_image_origins,
                shot_image_directions=shot_image_directions,
                shot_label_spacing=shot_label_spacings,
                shot_label_origins=shot_label_origins,
                shot_label_directions=shot_label_directions,
                return_probabilities=return_probabilities,
            )
            del (
                shot_embeddings,
                case_embeddings,
                shot_labels,
                shot_extra_labels,
                shot_ids,
                shot_image_sizes,
                shot_image_spacings,
                shot_image_origins,
                shot_image_directions,
                shot_patch_sizes,
                shot_patch_spacings,
                shot_label_spacings,
                shot_label_origins,
                shot_label_directions,
                case_image_sizes,
                case_image_spacings,
                case_image_origins,
                case_image_directions,
                case_patch_sizes,
                case_patch_spacings,
                case_label_sizes,
                case_label_spacings,
                case_label_origins,
                case_label_directions,
            )
            gc.collect()

        elif modality == "vision-language":
            predictions = [pred["text"] for pred in task_results["prediction"]]
            case_labels = [
                label["text"] for case in task_results["case_labels"] for label in case
            ]
            case_extra_labels = None

        else:
            raise ValueError(f"Unsupported modality: {modality}")

        metrics = evaluate_predictions(
            task_name=task_name,
            case_ids=case_ids,
            test_predictions=predictions,
            test_labels=case_labels,
            test_extra_labels=case_extra_labels,
            save_predictions=save_predictions,
        )

        # save metrics
        write_json_file(location=metrics_path, content=metrics)

        del task_results, predictions, case_labels, case_ids
        if "case_extra_labels" in locals():
            del case_extra_labels
        gc.collect()


def main():
    logging.info("Input folder contents:")
    print_directory_contents(INPUT_DIRECTORY)
    logging.info("=+=" * 10)
    logging.info("Groundtruth folder contents:")
    print_directory_contents(GROUNDTRUTH_DIRECTORY)
    logging.info("=+=" * 10)

    print("Evaluating language predictions")
    task_metrics = reformat_language_metrics(evaluate_language_predictions())
    print("=+=" * 10)

    metrics = {}
    adaptors = read_adaptors()

    # get mapping to determine list of tasks to evaluate
    mapping_path = GROUNDTRUTH_DIRECTORY / "mapping.csv"
    try:
        mapping = pd.read_csv(mapping_path, dtype={"case_id": str})
        all_tasks = mapping["task_name"].unique()
        save_predictions = False

        for task_name in all_tasks:
            print(f"Processing task: {task_name} (in subprocess)")
            metrics_path = OUTPUT_DIRECTORY / f"{task_name}.json"
            p = multiprocessing.Process(
                target=process_task_in_subprocess,
                args=(task_name, mapping, adaptors, save_predictions, metrics_path),
            )
            p.start()
            p.join()
            if metrics_path.exists():
                with open(metrics_path, "r") as f:
                    metrics = json.load(f)
                    task_metrics[task_name] = metrics
                print(f"Completed processing task: {task_name}")
                print("=+=" * 10)

        logging.info(f"Writing metrics for {len(task_metrics)} tasks...")
        write_combined_metrics(metric_dict=task_metrics, save_predictions=False)
        logging.info("Metrics written successfully.")
        return 0

    except FileNotFoundError:
        logging.info(f"Writing metrics for {len(task_metrics)} tasks...")
        write_combined_metrics(metric_dict=task_metrics, save_predictions=False)
        logging.info("Metrics written successfully.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
