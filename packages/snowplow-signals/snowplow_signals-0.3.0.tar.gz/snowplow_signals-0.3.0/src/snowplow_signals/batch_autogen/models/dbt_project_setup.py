import json
import os
from typing import Literal

import typer
from typing_extensions import Annotated

from snowplow_signals.batch_autogen.models.base_config_generator import (
    BaseConfigGenerator,
    DbtBaseConfig,
)
from snowplow_signals.batch_autogen.models.batch_source_config import (
    BatchSourceConfig,
)
from snowplow_signals.cli_logging import get_logger

from ...api_client import ApiClient
from ...models import AttributeGroupResponse
from ..utils.utils import WarehouseType, filter_latest_model_version_by_name

logger = get_logger(__name__)


class DbtProjectSetup:
    """
    Base class for setting up the base dbt project(s) including the base config.
    """

    target_type: WarehouseType

    def __init__(
        self,
        api_client: ApiClient,
        target_type: WarehouseType,
        repo_path: Annotated[str, typer.Option()] = "customer_repo",
        attribute_group_name: str | None = None,
        attribute_group_version: int | None = None,
    ):
        self.api_client = api_client
        self.repo_path = repo_path
        self.attribute_group_name = attribute_group_name
        self.attribute_group_version = attribute_group_version
        self.target_type = target_type

    def create_project_directories(
        self,
        setup_project_name: str,
        base_config: DbtBaseConfig,
        batch_source_config: dict,
    ):
        # Create project-specific output directory
        project_output_dir = os.path.join(self.repo_path, setup_project_name, "configs")
        if not os.path.exists(project_output_dir):
            os.makedirs(project_output_dir)
        base_config_path = os.path.join(project_output_dir, "base_config.json")
        with open(base_config_path, "w") as f:
            json.dump(base_config.model_dump(), f, indent=4)
        logger.success(f"📄 Base config file generated for {setup_project_name}")
        batch_source_config_path = os.path.join(
            project_output_dir, "batch_source_config.json"
        )
        with open(batch_source_config_path, "w") as f:
            json.dump(batch_source_config, f, indent=4)
        logger.success(
            f"📄 Batch source config file generated for {setup_project_name}"
        )

    def _get_attribute_view_project_config(
        self,
        attribute_view: AttributeGroupResponse,
    ) -> DbtBaseConfig:
        generator = BaseConfigGenerator(
            data=attribute_view, target_type=self.target_type
        )
        return generator.create_base_config()

    def _get_default_batch_source_config(
        self, attribute_view: AttributeGroupResponse
    ) -> BatchSourceConfig:
        """
        Creates a pre-populated config file for users to fill out for the sync.
        """

        return BatchSourceConfig(
            database="",
            wh_schema="",
            table=f"{attribute_view.name}_{attribute_view.version}_attributes",
            name=f"{attribute_view.name}_{attribute_view.version}_attributes",
            timestamp_field="valid_at_tstamp",
            created_timestamp_column="lower_limit",
            description=f"Table containing attributes for {attribute_view.name}_{attribute_view.version} view",
            tags={},
            owner="",
        )

    def setup_all_projects(self):
        """Sets up dbt files for one or all projects."""

        attribute_views = self._get_attribute_views()
        for attribute_view in attribute_views:
            # Skip attribute groups that have no attributes (i.e., only sync existing tables)
            if (not attribute_view.attributes) and attribute_view.fields:
                logger.info(
                    f"Skipping batch attribute group '{attribute_view.name}_{attribute_view.version}' as it has no attributes and only fields."
                )
                continue
            view_project_name = f"{attribute_view.name}_{attribute_view.version}"
            project_config = self._get_attribute_view_project_config(attribute_view)
            batch_source_config = self._get_default_batch_source_config(
                attribute_view
            ).model_dump(mode="json", exclude_none=True)
            self.create_project_directories(
                view_project_name, project_config, batch_source_config
            )

        return True

    def _fetch_attribute_views(self) -> list[AttributeGroupResponse]:
        attribute_views = self.api_client.make_request(
            method="GET",
            endpoint="registry/attribute_groups/",
            params={"offline": True, "property_syntax": self.target_type},
        )
        return [AttributeGroupResponse.model_validate(view) for view in attribute_views]

    def _get_attribute_views(self) -> list[AttributeGroupResponse]:
        logger.info("🔗 Fetching attribute groups from API")
        all_attribute_views = self._fetch_attribute_views()
        logger.debug(
            f"Received API response: {[view.model_dump_json() for view in all_attribute_views]}"
        )
        if len(all_attribute_views) == 0:
            raise ValueError("No attribute groups available.")
        latest_views = filter_latest_model_version_by_name(all_attribute_views)
        # Filter by project name if specified
        if self.attribute_group_name:
            if not self.attribute_group_version:
                project_views = [
                    view
                    for view in latest_views
                    if view.name == self.attribute_group_name
                ]
                if not project_views:
                    raise ValueError(
                        f"No project/attribute group found with name: {self.attribute_group_name}"
                    )
                return project_views
            else:
                project_views = [
                    view
                    for view in all_attribute_views
                    if view.name == self.attribute_group_name
                    and view.version == self.attribute_group_version
                ]
                if not project_views:
                    raise ValueError(
                        f"No project/attribute group found with name: {self.attribute_group_name} and version: {self.attribute_group_version}"
                    )
                return project_views
        else:
            return latest_views
