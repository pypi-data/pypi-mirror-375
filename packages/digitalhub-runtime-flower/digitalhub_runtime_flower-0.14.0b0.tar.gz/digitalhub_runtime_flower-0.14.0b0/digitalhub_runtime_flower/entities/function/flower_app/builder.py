# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerApp
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.function._base.builder import FunctionFlowerBuilder
from digitalhub_runtime_flower.entities.function.flower_app.entity import FunctionFlowerApp
from digitalhub_runtime_flower.entities.function.flower_app.spec import (
    FunctionSpecFlowerApp,
    FunctionValidatorFlowerApp,
)
from digitalhub_runtime_flower.entities.function.flower_app.status import FunctionStatusFlowerApp
from digitalhub_runtime_flower.entities.function.flower_app.utils import source_check, source_post_check


class FunctionFlowerAppBuilder(FunctionFlowerBuilder, RuntimeEntityBuilderFlowerApp):
    """
    FunctionFlowerApp builder.
    """

    ENTITY_CLASS = FunctionFlowerApp
    ENTITY_SPEC_CLASS = FunctionSpecFlowerApp
    ENTITY_SPEC_VALIDATOR = FunctionValidatorFlowerApp
    ENTITY_STATUS_CLASS = FunctionStatusFlowerApp
    ENTITY_KIND = EntityKinds.FUNCTION_FLOWER_APP.value

    def build(
        self,
        kind: str,
        project: str,
        name: str,
        uuid: str | None = None,
        description: str | None = None,
        labels: list[str] | None = None,
        embedded: bool = False,
        **kwargs,
    ) -> FunctionFlowerApp:
        kwargs = source_check(**kwargs)
        obj = super().build(
            kind,
            project,
            name,
            uuid,
            description,
            labels,
            embedded,
            **kwargs,
        )
        return source_post_check(obj)

    def from_dict(self, obj: dict, validate: bool = True) -> FunctionFlowerApp:
        """
        Create a new object from dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary to create object from.
        validate : bool
            Flag to indicate if arguments must be validated.

        Returns
        -------
        FunctionFlowerApp
            Object instance.
        """
        entity = super().from_dict(obj, validate=validate)
        return source_post_check(entity)

    def _parse_dict(self, obj: dict, validate: bool = True) -> dict:
        """
        Get dictionary and parse it to a valid entity dictionary.

        Parameters
        ----------
        entity : str
            Entity type.
        obj : dict
            Dictionary to parse.

        Returns
        -------
        dict
            A dictionary containing the attributes of the entity instance.
        """
        # Look for source in spec
        if spec_dict := obj.get("spec", {}):
            # Check source
            fab_source = spec_dict.get("fab_source", {})
            if fab_source:
                spec_dict["fab_source"] = source_check(fab_source=fab_source)["fab_source"]
        return super()._parse_dict(obj, validate=validate)
