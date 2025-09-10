# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.
import pytest
import mlflow

from responsibleai_tabular_automl.rai_automl import (
    _compute_and_upload_rai_insights_internal,
)


class TestRAIAutoML:
    def setup_method(self):
        """Setup MLflow for Azure ML integration tests"""
        # Azure ML workspace details
        self.subscription_id = "a75ae43f-9f72-4699-ba66-d3a173cfe082"
        self.resource_group = "ilmatdpv2rg3"
        self.workspace_name = "ilmatdpv2ws3"

        # Set MLflow tracking URI directly to Azure ML workspace
        mlflow_tracking_uri = (
            f"azureml://eastus2.api.azureml.ms/mlflow/v2.0/subscriptions/"
            f"{self.subscription_id}/resourceGroups/{self.resource_group}/"
            f"providers/Microsoft.MachineLearningServices/workspaces/"
            f"{self.workspace_name}"
        )
        print("Setting MLflow tracking URI to: " + mlflow_tracking_uri)
        mlflow.set_tracking_uri(mlflow_tracking_uri)

    @pytest.mark.skip(
        "Skipping since it is not possible to "
        "run this test in build pipeline"
    )
    def test_compute_and_upload_rai_insights_internal_classification(self):
        automl_child_job_id = "kind_school_qhhbw3yygm_3"

        # Start MLflow run for tracking
        with mlflow.start_run():
            # Function now only takes the child run ID (automl_child_job_id)
            _compute_and_upload_rai_insights_internal(automl_child_job_id)
