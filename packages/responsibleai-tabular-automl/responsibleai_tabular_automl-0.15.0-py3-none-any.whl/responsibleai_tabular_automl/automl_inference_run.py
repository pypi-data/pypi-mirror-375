# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.

"""Script for computing AutoML data on remote compute."""
from typing import Tuple, Dict, Any, List, Optional
import pandas as pd
import pickle
import json
import os
from azureml.core import Run
from azureml.automl.core.constants import FeatureType
from azureml.automl.runtime.shared._parqueter import Parqueter
from interpret_community.common.serialization_utils import _serialize_json_safe

import mlflow


# TODO:- Move to take dependency on raiutils for this function once the
#        package takes dependency on raiutils.
def generate_random_sample(
    dataset: pd.DataFrame,
    target_column: str,
    number_samples: int,
    is_classification: Optional[bool] = False,
) -> pd.DataFrame:
    """
    Pick random samples of data from dataset.
    :param dataset: Input dataset.
    :type X: pd.DataFrame
    :param target_column: The name of the column which may be used in case of
        stratified splitting.
    :type target_column: str
    :param number_samples: The number of intended samples in the sampled data
    :type number_samples: int
    :param is_classification: If this is a classification scenario and we
        should do a stratified split based on the column target_column.
    :type is_classification: bool
    :return: Sub-sample of input dataset
    :rtype: pd.DataFrame
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split

    from raiutils.exceptions import UserConfigValidationException

    if not isinstance(dataset, pd.DataFrame):
        raise UserConfigValidationException(
            "Expecting a pandas dataframe for generating a dataset sample."
        )

    if not isinstance(target_column, str):
        raise UserConfigValidationException(
            "Expecting a string for target_column."
        )

    if not isinstance(number_samples, int):
        raise UserConfigValidationException(
            "Expecting an integer for number_samples."
        )

    if not isinstance(is_classification, bool):
        raise UserConfigValidationException(
            "Expecting a boolean for is_classification."
        )

    if target_column not in dataset.columns.tolist():
        raise UserConfigValidationException(
            "The column {0} is not present in dataset".format(target_column)
        )

    if number_samples <= 0:
        raise UserConfigValidationException(
            "The number_samples should be greater than zero."
        )

    n_samples = len(dataset)
    if n_samples <= number_samples:
        return dataset

    target = dataset[target_column].values
    try:
        stratified_split = target if is_classification else None
        (
            dataset_sampled,
            _,
        ) = train_test_split(
            dataset,
            train_size=number_samples,
            random_state=777,
            stratify=stratified_split,
        )
    except Exception:
        # in case stratification fails, fall back to non-stratify train/test
        # split
        (
            dataset_sampled,
            _,
        ) = train_test_split(
            dataset, random_state=777, train_size=number_samples
        )

    return dataset_sampled


def automl_download_raw_data(parent_run_id: str) -> Tuple[Any, Any, Any, Any]:
    run = Run.get_context()
    parent_run = run.experiment.workspace.get_run(parent_run_id)

    # Get the train data
    x_raw_filename = "X_raw.df.parquet"
    parent_run.download_file(
        "outputs/_automl_internal/" + x_raw_filename, x_raw_filename
    )
    X_raw = pd.read_parquet(x_raw_filename)
    X_raw.describe()

    try:
        # Get train target
        y_filename = "y_raw.npys.parquet"
        parent_run.download_file(
            "outputs/_automl_internal/" + y_filename, y_filename
        )
        y = pd.read_parquet(y_filename).values
    except Exception:
        # Get train target
        y_filename = "y_raw.pkl"
        parent_run.download_file(
            "outputs/_automl_internal/" + y_filename, y_filename
        )
        y = pickle.load(open(y_filename, "rb"))

    try:
        # Get the validation data
        x_raw_valid_filename = "X_raw_valid.df.parquet"
        parent_run.download_file(
            "outputs/_automl_internal/" + x_raw_valid_filename,
            x_raw_valid_filename,
        )
        X_raw_valid = pd.read_parquet(x_raw_valid_filename)
        X_raw_valid.describe()
    except Exception:
        # Get validation target
        x_valid_filename = "X_raw_valid.pkl"
        parent_run.download_file(
            "outputs/_automl_internal/" + x_valid_filename, x_valid_filename
        )
        X_raw_valid = pickle.load(open(x_valid_filename, "rb"))
        # X_raw_valid.describe()

    try:
        # Get validation target
        y_valid_filename = "y_raw_valid.npys.parquet"
        parent_run.download_file(
            "outputs/_automl_internal/" + y_valid_filename, y_valid_filename
        )
        y_valid = pd.read_parquet(y_valid_filename).values
    except Exception:
        # Get validation target
        y_valid_filename = "y_raw_valid.pkl"
        parent_run.download_file(
            "outputs/_automl_internal/" + y_valid_filename, y_valid_filename
        )
        y_valid = pickle.load(open(y_valid_filename, "rb"))

    if y_valid is None:
        print("No validation target set")

    if X_raw_valid is None:
        print("No validation set")
        target_column, task_type = get_automl_task_type_and_target_column_name(
            parent_run_id
        )
        train = X_raw.copy()
        train[target_column] = y

        test = generate_random_sample(
            train,
            target_column=target_column,
            number_samples=5000,
            is_classification=(task_type == "classification"),
        )

        X_raw_valid = test.drop(columns=[target_column])
        y_valid = test[target_column]
    elif len(X_raw_valid) > 5000:
        print("Validation set greater than 5000")
        target_column, task_type = get_automl_task_type_and_target_column_name(
            parent_run_id
        )
        test = X_raw_valid.copy()
        test[target_column] = y_valid

        test_sampled = generate_random_sample(
            test,
            target_column=target_column,
            number_samples=5000,
            is_classification=(task_type == "classification"),
        )

        X_raw_valid = test_sampled.drop(columns=[target_column])
        y_valid = test_sampled[target_column]

    return X_raw, y, X_raw_valid, y_valid


def get_automl_task_type_and_target_column_name(
    parent_run_id: str,
) -> Tuple[str, str]:
    run = Run.get_context()
    parent_run = run.experiment.workspace.get_run(parent_run_id)
    automl_settings = json.loads(
        parent_run.properties["AMLSettingsJsonString"]
    )
    target_column = automl_settings["label_column_name"]
    task_type = automl_settings["task_type"]
    return target_column, task_type


def get_feature_summary_and_dropped_feature_types(
    child_run_id: str,
) -> Tuple[Dict[str, Any], List[str]]:
    run = Run.get_context()
    child_run = run.experiment.workspace.get_run(child_run_id)
    featurization_summary_filename = "featurization_summary.json"
    child_run.download_file(
        "outputs/" + featurization_summary_filename,
        featurization_summary_filename,
    )

    f = open(featurization_summary_filename, "r")
    file_content = f.read()
    file_content = file_content.replace("NaN", "null")
    summaries = json.loads(file_content)
    f.close()
    summaries

    feature_type_to_feature_name_dict = {}
    for feature in FeatureType.FULL_SET:
        feature_type_to_feature_name_dict[feature] = []

    for summary in summaries:
        feature_type_to_feature_name_dict[summary["TypeDetected"]].append(
            summary["RawFeatureName"]
        )

    return feature_type_to_feature_name_dict, list(FeatureType.DROP_SET)


def get_inference_results(
    parent_run_id: str,
    child_run_id: str,
    X_raw: pd.DataFrame,
    X_raw_valid: pd.DataFrame,
) -> Tuple[Any, Any, Any, Any]:
    run = Run.get_context()
    _, task_type = get_automl_task_type_and_target_column_name(parent_run_id)
    child_run = run.experiment.workspace.get_run(child_run_id)
    child_run.download_files("outputs/mlflow-model", ".")
    model = mlflow.sklearn.load_model("./outputs/mlflow-model/")
    preds = model.predict(X_raw)
    preds_valid = model.predict(X_raw_valid)
    if task_type == "classification":
        preds_proba = model.predict_proba(X_raw)
        preds_valid_proba = model.predict_proba(X_raw_valid)
        if isinstance(preds_proba, pd.DataFrame):
            preds_proba = preds_proba.values
        if isinstance(preds_valid_proba, pd.DataFrame):
            preds_valid_proba = preds_valid_proba.values
    else:
        preds_proba = None
        preds_valid_proba = None
    return preds, preds_valid, preds_proba, preds_valid_proba


def get_model_classes(child_run_id: str) -> Any:
    run = Run.get_context()
    child_run = run.experiment.workspace.get_run(child_run_id)
    child_run.download_files("outputs/mlflow-model", ".")
    model = mlflow.sklearn.load_model("./outputs/mlflow-model/")
    if hasattr(model, "classes_"):
        classes = _serialize_json_safe(list(model.classes_))
        return classes
    else:
        return None


def upload_rai_artifacts_to_automl_child_run_internal(
    parent_run_id: str, child_run_id: str
) -> None:
    X_raw, y, X_raw_valid, y_valid = automl_download_raw_data(parent_run_id)
    target_column, task_type = get_automl_task_type_and_target_column_name(
        parent_run_id
    )
    (
        feature_type_to_feature_name_dict,
        feature_types_dropped,
    ) = get_feature_summary_and_dropped_feature_types(child_run_id)
    preds, preds_valid, preds_proba, preds_valid_proba = get_inference_results(
        parent_run_id, child_run_id, X_raw, X_raw_valid
    )
    classes = get_model_classes(child_run_id)

    os.makedirs("rai", exist_ok=True)

    Parqueter.dump_numpy_array(preds, "rai/predictions.npy.parquet")
    Parqueter.dump_numpy_array(preds_valid, "rai/predictions_test.npy.parquet")

    if task_type == "classification":
        Parqueter.dump_numpy_array(
            preds_proba, "rai/prediction_probabilities.npy.parquet"
        )
        Parqueter.dump_numpy_array(
            preds_valid_proba,
            "rai/prediction_test_probabilities.npy.parquet",
        )

    train = X_raw.copy()
    train[target_column] = y

    test = X_raw_valid.copy()
    test[target_column] = y_valid

    Parqueter.dump_pandas_dataframe(train, "rai/train.df.parquet")
    Parqueter.dump_pandas_dataframe(test, "rai/test.df.parquet")

    metadata = {
        "feature_type_summary": feature_type_to_feature_name_dict,
        "feature_type_dropped": feature_types_dropped,
        "target_column": target_column,
        "task_type": task_type,
        "classes": classes,
    }

    with open("rai/metadata.json", "w") as fp:
        json.dump(metadata, fp)

    run = Run.get_context()
    child_run = run.experiment.workspace.get_run(child_run_id)
    child_run.upload_folder("outputs/rai", "rai")


def upload_rai_artifacts_to_automl_child_run(
    parent_run_id: str, child_run_id: str
) -> None:
    try:
        from azureml.automl.runtime.rai import (
            inference_run as rai_inference_run,
        )

        execute_using_automl_sdk = True
    except ImportError:
        execute_using_automl_sdk = False

    if execute_using_automl_sdk:
        print("Using automl to compute prerequisites")
        rai_inference_run.upload_rai_artifacts_to_automl_child_run(
            parent_run_id, child_run_id
        )
    else:
        print("Using proxy script for automl to compute prerequisites")
        upload_rai_artifacts_to_automl_child_run_internal(
            parent_run_id, child_run_id
        )


upload_rai_artifacts_to_automl_child_run(
    "<<automl_parent_run_id>>", "<<automl_child_run_id>>"
)
