# Copyright 2025 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

from typing import Sequence

import pulumi
import pulumi_datarobot as drp

from datarobot_pulumi_utils.schema.custom_models import (
    CustomModelArgs,
    DeploymentArgs,
    RegisteredModelArgs,
)


class CustomModelDeployment(pulumi.ComponentResource):
    def __init__(
        self,
        resource_name: str,
        registered_model_args: RegisteredModelArgs,
        prediction_environment: drp.PredictionEnvironment,
        deployment_args: DeploymentArgs,
        use_case_ids: Sequence[pulumi.Output[str]] | str | None = None,
        custom_model_version_id: pulumi.Input[str] | None = None,
        custom_model_args: CustomModelArgs | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        """
        Deploy a custom model in DataRobot.

        This class performs the following steps:
        1. Registers the custom model.
        2. Deploys the registered model to the specified prediction environment.

        Parameters:
        -----------
        name : str
            The name of this Pulumi resource.
        custom_model : datarobot.CustomModel
            The custom model to be deployed.
        prediction_environment : datarobot.PredictionEnvironment
            The DataRobot PredictionEnvironment object where the model will be deployed.
        registered_model_args : RegisteredModelArgs
            Arguments for registering the model.
        deployment_args : DeploymentArgs
            Arguments for creating the Deployment.
        opts : Optional[pulumi.ResourceOptions]
            Optional Pulumi resource options.
        """
        super().__init__("custom:datarobot:CustomModelDeployment", resource_name, None, opts)
        if (custom_model_version_id and custom_model_args) or (not custom_model_version_id and not custom_model_args):
            raise ValueError("Exactly one of custom_model_version_id and custom_model_args must be specified")

        if custom_model_args:
            custom_model_version_id = drp.CustomModel(
                **custom_model_args.model_dump(exclude_none=True),
                opts=pulumi.ResourceOptions(parent=self),
                use_case_ids=use_case_ids,
            ).version_id

        self.registered_model = drp.RegisteredModel(
            custom_model_version_id=custom_model_version_id,
            **registered_model_args.model_dump(mode="json"),
            opts=pulumi.ResourceOptions(parent=self),
            use_case_ids=use_case_ids,
        )

        self.deployment = drp.Deployment(
            prediction_environment_id=prediction_environment.id,
            registered_model_version_id=self.registered_model.version_id,
            **deployment_args.model_dump(),
            opts=pulumi.ResourceOptions(parent=self),
            use_case_ids=use_case_ids,
        )

        self.register_outputs(
            {
                "custom_model_version_id": custom_model_version_id,
                "registered_model_id": self.registered_model.id,
                "registered_model_version_id": self.registered_model.version_id,
                "deployment_id": self.deployment.id,
            }
        )

    @property
    def id(self) -> pulumi.Output[str]:
        return self.deployment.id

    @property
    def deployment_id(self) -> pulumi.Output[str]:
        return self.deployment.id

    @property
    def registered_model_id(self) -> pulumi.Output[str]:
        return self.registered_model.id

    @property
    def registered_model_version_id(self) -> pulumi.Output[str]:
        return self.registered_model.version_id
