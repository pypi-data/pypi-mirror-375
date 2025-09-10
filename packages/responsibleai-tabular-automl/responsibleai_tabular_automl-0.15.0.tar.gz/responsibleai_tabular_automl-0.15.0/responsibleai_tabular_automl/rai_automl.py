# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.

"""Module for computing and uploading RAI insights for AutoML models."""

import subprocess
import os
import shutil
import time
from typing import Optional
import pandas as pd
import json
import numpy as np
import warnings

from ml_wrappers.model.predictions_wrapper import (
    PredictionsModelWrapperClassification,
    PredictionsModelWrapperRegression,
)

import mlflow
from responsibleai import RAIInsights
from responsibleai.serialization_utilities import serialize_json_safe
from responsibleai.feature_metadata import FeatureMetadata
from pathlib import Path

from responsibleai_tabular_automl._loggerfactory import _LoggerFactory, track

CONDA_YAML = "conda.yaml"

_ai_logger = None


def _get_logger():
    global _ai_logger
    if _ai_logger is None:
        _ai_logger = _LoggerFactory.get_logger(__file__)
    return _ai_logger


_get_logger()


@track(_get_logger)
def _download_job_artifacts_mlflow(job_id: str, output_name: str,
                                   local_path: str = "./"):
    """Download job artifacts using MLflow APIs instead of Azure ML SDK."""
    _ai_logger.info(f"Downloading {output_name} artifacts for job {job_id} "
                    f"using MLflow")

    try:
        from mlflow.tracking import MlflowClient

        # Create MLflow client
        client = MlflowClient()

        # Try to list artifacts first to see what's available
        try:
            artifacts = client.list_artifacts(job_id, output_name)
            if artifacts:
                _ai_logger.info(f"Found artifacts: "
                                f"{[a.path for a in artifacts]}")
            else:
                _ai_logger.info(f"No artifacts found for path: {output_name}")
                # Try listing all artifacts to see what's available
                all_artifacts = client.list_artifacts(job_id)
                _ai_logger.info(f"All available artifacts: "
                                f"{[a.path for a in all_artifacts]}")
        except Exception as e:
            _ai_logger.warning(f"Could not list artifacts: {e}")

        # Download the artifacts
        download_path = client.download_artifacts(job_id, output_name,
                                                  local_path)
        _ai_logger.info(f"Downloaded artifacts to: {download_path}")
        return download_path

    except Exception as e:
        _ai_logger.error(f"MLflow download failed: {e}")

        # Fallback: try to download all artifacts if specific path fails
        try:
            _ai_logger.info("Trying to download all artifacts as fallback")
            client = MlflowClient()
            download_path = client.download_artifacts(job_id, "", local_path)
            _ai_logger.info(f"Downloaded all artifacts to: {download_path}")
            return download_path
        except Exception as e2:
            _ai_logger.error(f"MLflow fallback download also failed: {e2}")
            raise Exception(f"Unable to download {output_name} artifacts "
                            f"using MLflow. Primary error: {e}, "
                            f"Fallback error: {e2}")


@track(_get_logger)
def _compute_and_upload_rai_insights_internal(automl_child_run_id: str):
    # Get the AutoML job and download RAI files using MLflow
    print("Generating RAI insights for AutoML child run")
    _ai_logger.info("Generating RAI insights for AutoML child run")

    # Download RAI outputs using MLflow
    try:
        _download_job_artifacts_mlflow(automl_child_run_id, "rai", "./")
        _ai_logger.info("RAI artifacts download completed")
    except Exception as e:
        _ai_logger.error(f"Failed to download RAI artifacts: {e}")
        raise

    # Find RAI artifacts - check common locations
    rai_base_path = None
    possible_paths = [
        # Most common for v2 SDK
        "outputs/rai",
        # Alternative v2 SDK structure
        "artifacts/outputs/rai",
        # Direct download
        "rai"
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.path.exists(f"{path}/metadata.json"):
            rai_base_path = path
            _ai_logger.info(f"Found RAI artifacts at: {rai_base_path}")
            break

    if not rai_base_path:
        # Search for metadata.json as fallback
        _ai_logger.error(
            "Could not find RAI artifacts in expected locations")
        for root, dirs, files in os.walk("."):
            if "metadata.json" in files and "rai" in root.lower():
                rai_base_path = root
                _ai_logger.info(f"Found RAI artifacts at: {rai_base_path}")
                break

        if not rai_base_path:
            raise FileNotFoundError(
                "RAI artifacts with metadata.json not found")

    # Ensure outputs/rai structure for the rest of the code
    if rai_base_path != "outputs/rai":
        os.makedirs("outputs", exist_ok=True)
        if os.path.exists("outputs/rai"):
            shutil.rmtree("outputs/rai")
        shutil.copytree(rai_base_path, "outputs/rai")
        _ai_logger.info(
            f"Copied RAI artifacts from {rai_base_path} to outputs/rai")

    metadata = None
    with open("outputs/rai/metadata.json", "r") as fp:
        metadata = json.load(fp)

    train = pd.read_parquet("outputs/rai/train.df.parquet")
    test = pd.read_parquet("outputs/rai/test.df.parquet")
    train_predictions = pd.read_parquet(
        "outputs/rai/predictions.npy.parquet"
    ).values
    test_predictions = pd.read_parquet(
        "outputs/rai/predictions_test.npy.parquet"
    ).values

    if metadata["task_type"] == "classification":
        train_prediction_probabilities = pd.read_parquet(
            "outputs/rai/prediction_probabilities.npy.parquet"
        ).values
        test_prediction_probabilities = pd.read_parquet(
            "outputs/rai/prediction_test_probabilities.npy.parquet"
        ).values
    else:
        train_prediction_probabilities = None
        test_prediction_probabilities = None

    target_column_name = metadata["target_column"]
    task_type = metadata["task_type"]
    classes = metadata["classes"]

    categorical_features = (
        metadata["feature_type_summary"]["Categorical"]
        + metadata["feature_type_summary"]["CategoricalHash"]
    )
    dropped_features = (
        metadata["feature_type_summary"]["Hashes"]
        + metadata["feature_type_summary"]["AllNan"]
        + metadata["feature_type_summary"]["Ignore"]
    )
    datetime_features = metadata["feature_type_summary"]["DateTime"]
    text_features = metadata["feature_type_summary"]["Text"]

    X_test = test.drop(columns=[target_column_name])
    X_train = train.drop(columns=[target_column_name])
    if len(dropped_features) > 0:
        X_test = X_test.drop(columns=dropped_features)
        X_train = X_train.drop(columns=dropped_features)
    all_data = pd.concat([X_test, X_train])
    model_predict_output = np.concatenate(
        (test_predictions, train_predictions)
    )

    if metadata["task_type"] == "classification":
        model_predict_proba_output = np.concatenate(
            (test_prediction_probabilities, train_prediction_probabilities)
        )
        model_wrapper = PredictionsModelWrapperClassification(
            all_data, model_predict_output, model_predict_proba_output,
            should_construct_pandas_query=False
        )
    else:
        model_wrapper = PredictionsModelWrapperRegression(
            all_data, model_predict_output,
            should_construct_pandas_query=False
        )

    train = train.drop(columns=dropped_features)
    test = test.drop(columns=dropped_features)
    if len(text_features) == 0 and len(datetime_features) == 0:
        _ai_logger.info(
            "Generating RAI insights for {} samples.".format(len(test))
        )
        feature_metadata = FeatureMetadata(
            categorical_features=categorical_features)
        rai_insights = RAIInsights(
            model=model_wrapper,
            train=train,
            test=test,
            target_column=target_column_name,
            task_type=task_type,
            classes=classes,
            feature_metadata=feature_metadata
        )
        rai_insights.explainer.add()
        rai_insights.error_analysis.add()
        rai_insights.compute()
        rai_insights.save("dashboard")

        # Upload artifacts using MLflow
        mlflow.log_artifacts("dashboard", "dashboard")

        rai_data = rai_insights.get_data()
        rai_dict = serialize_json_safe(rai_data)
        ux_json_path = Path("ux_json")
        ux_json_path.mkdir(parents=True, exist_ok=True)
        json_filename = ux_json_path / "dashboard.json"
        with open(json_filename, "w") as json_file:
            json.dump(rai_dict, json_file)

        # Upload UX JSON using MLflow
        mlflow.log_artifacts("ux_json", "ux_json")

        # Tag the run using MLflow
        mlflow.set_tag("model_rai", "True")
        print("Successfully generated and uploaded the RAI insights")
        _ai_logger.info("Successfully generated and uploaded the RAI insights")
    else:
        warnings.warn(
            "Currently RAI is not supported for "
            "text and datetime features"
        )
        _ai_logger.info(
            "Currently RAI is not supported for "
            "text and datetime features"
        )
        # Tag using MLflow
        mlflow.set_tag("model_rai_datetime_text", "True")


@track(_get_logger)
def _create_project_folder(
    automl_parent_run_id: str, automl_child_run_id: str
):
    project_folder = "./automl_experiment_submit_folder"

    os.makedirs(project_folder, exist_ok=True)

    # Comment the code below (next three lines only) when executing the
    # script model_generate_rai.py
    dir_path = os.path.dirname(os.path.realpath(__file__))
    rai_script_path = os.path.join(dir_path, "automl_inference_run.py")
    shutil.copy(rai_script_path, project_folder)

    # Uncomment the line below when executing the script model_generate_rai.py
    # shutil.copy("automl_inference_run.py", project_folder)

    script_file_name = os.path.join(project_folder, "automl_inference_run.py")

    # Open the sample script for modification
    with open(script_file_name, "r") as cefr:
        content = cefr.read()

    content = content.replace("<<automl_parent_run_id>>", automl_parent_run_id)

    content = content.replace("<<automl_child_run_id>>", automl_child_run_id)

    # Write sample file into your script folder.
    with open(script_file_name, "w") as cefw:
        cefw.write(content)

    return project_folder


def call_with_output(command):
    success = False
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT
        ).decode()
        success = True
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    except Exception as e:
        # check_call can raise other exceptions, such as FileNotFoundError
        output = str(e)
    return (success, output)


@track(_get_logger)
def execute_automl_inference_script(automl_child_run_id: str):
    # Get the AutoML job and download model artifacts using MLflow
    print("Generating predictions for AutoML model")
    _ai_logger.info("Generating predictions for AutoML model")

    command = ["pip", "list"]
    success, output = call_with_output(command)

    # Download conda.yaml using MLflow
    try:
        _download_job_artifacts_mlflow(automl_child_run_id, "mlflow-model",
                                       "./")

        # Find conda.yaml in common locations
        conda_yaml_candidates = [
            CONDA_YAML,
            f"outputs/mlflow-model/{CONDA_YAML}",
            f"artifacts/outputs/mlflow-model/{CONDA_YAML}",
            f"mlflow-model/{CONDA_YAML}"
        ]

        conda_yaml_path = None
        for candidate in conda_yaml_candidates:
            if os.path.exists(candidate):
                conda_yaml_path = candidate
                _ai_logger.info(f"Found conda.yaml at: {conda_yaml_path}")
                break

        # Search for conda.yaml if not found in expected locations
        if not conda_yaml_path:
            _ai_logger.info("Searching for conda.yaml in downloaded files...")
            for root, dirs, files in os.walk("."):
                if CONDA_YAML in files:
                    conda_yaml_path = os.path.join(root, CONDA_YAML)
                    _ai_logger.info(f"Found conda.yaml at: {conda_yaml_path}")
                    break

        if conda_yaml_path and conda_yaml_path != CONDA_YAML:
            shutil.copy(conda_yaml_path, CONDA_YAML)
            _ai_logger.info("Copied conda.yaml to working directory")
        elif not conda_yaml_path:
            raise FileNotFoundError("conda.yaml not found")

    except Exception as e:
        _ai_logger.error(f"Failed to download conda.yaml: {e}")
        raise Exception(
            f"Unable to download conda.yaml needed for environment setup: {e}")

    automl_env_name = "automl_env_" + str(time.time())
    command = [
        "conda",
        "env",
        "create",
        "--name",
        automl_env_name,
        "--file",
        os.path.join(CONDA_YAML),
    ]
    success, output = call_with_output(command)

    if not success:
        _ai_logger.error("Error creating conda environment")
        raise Exception(output)

    command = [
        "conda",
        "env",
        "config",
        "vars",
        "set",
        ("LD_LIBRARY_PATH=/opt/miniconda/envs/"
            f"{automl_env_name}/lib:$LD_LIBRARY_PATH"),
        "--name",
        automl_env_name
    ]
    success, output = call_with_output(command)

    if not success:
        _ai_logger.error("Error prepending conda "
                         "environment lib to LD_LIBRARY_PATH")
        raise Exception(output)

    inference_script_name = (
        "./automl_experiment_submit_folder" + "/automl_inference_run.py"
    )
    command = [
        "conda",
        "run",
        "-n",
        automl_env_name,
        "python",
        inference_script_name,
    ]
    success, output = call_with_output(command)

    if not success:
        _ai_logger.error("Error running automl script in conda environment")
        raise Exception(output)

    command = ["conda", "env", "remove", "--name", automl_env_name, "-y"]
    success, output = call_with_output(command)
    print("Successfully generated predictions for AutoML model")
    _ai_logger.info("Successfully generated predictions for AutoML model")


@track(_get_logger)
def compute_and_upload_rai_insights(
    automl_parent_run_id: Optional[str] = None,
    automl_child_run_id: Optional[str] = None,
):
    print("The automl child run-id is: " + str(automl_child_run_id))
    _ai_logger.info("The automl child run-id is: " + str(automl_child_run_id))
    print("The automl parent run-id is: " + str(automl_parent_run_id))

    # Get current run id
    current_run_id = os.environ.get("AZUREML_RUN_ID")
    print("The current run-id is: " + str(current_run_id))

    _ai_logger.info(
        "Creating local conda environment to compute AutoML artifacts."
    )
    # Create conda env from native commands and submit script
    _create_project_folder(
        automl_parent_run_id, automl_child_run_id
    )

    execute_automl_inference_script(automl_child_run_id)

    _compute_and_upload_rai_insights_internal(automl_child_run_id)


# Uncomment the line below when executing the script model_generate_rai.py
# compute_and_upload_rai_insights("<<parent_run_id>>", "<<child_run_id>>")
