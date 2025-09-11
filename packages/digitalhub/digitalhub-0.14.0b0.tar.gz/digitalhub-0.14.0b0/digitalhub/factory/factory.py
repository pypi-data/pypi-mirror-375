# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.factory.enums import FactoryEnum
from digitalhub.factory.utils import import_module, list_runtimes
from digitalhub.utils.exceptions import BuilderError

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.builder import EntityBuilder
    from digitalhub.entities._base.entity.entity import Entity
    from digitalhub.entities._base.entity.metadata import Metadata
    from digitalhub.entities._base.entity.spec import Spec, SpecValidator
    from digitalhub.entities._base.entity.status import Status
    from digitalhub.entities._base.runtime_entity.builder import RuntimeEntityBuilder
    from digitalhub.runtimes._base import Runtime
    from digitalhub.runtimes.builder import RuntimeBuilder


class Factory:
    """
    Factory for creating and managing entity and runtime builders.

    This class implements the Factory pattern to manage the creation of
    entities and runtimes through their respective builders. It maintains
    separate registries for entity and runtime builders.

    Many function arguments are called kind_to_build_from to avoid overwriting
    kind in kwargs.

    Attributes
    ----------
    _entity_builders : dict[str, EntityBuilder | RuntimeEntityBuilder]
        Registry of instantiated entity builders indexed by kind.
    _runtime_builders : dict[str, RuntimeBuilder]
        Registry of instantiated runtime builders indexed by kind.

    Notes
    -----
    All builder methods may raise BuilderError if the requested kind
    is not found in the registry.
    """

    def __init__(self):
        self._entity_builders: dict[str, EntityBuilder | RuntimeEntityBuilder] = {}
        self._runtime_builders: dict[str, RuntimeBuilder] = {}
        self._entities_registered = False
        self._runtimes_registered = False

    def add_entity_builder(self, name: str, builder: type[EntityBuilder | RuntimeEntityBuilder]) -> None:
        """
        Register an entity builder.

        Parameters
        ----------
        name : str
            The unique identifier for the builder.
        builder : type[EntityBuilder] | type[RuntimeEntityBuilder]
            The builder class to register. It will be instantiated immediately.

        Returns
        -------
        None

        Raises
        ------
        BuilderError
            If a builder with the same name already exists.
        """
        if name in self._entity_builders:
            raise BuilderError(f"Builder {name} already exists.")
        self._entity_builders[name] = builder()

    def add_runtime_builder(self, name: str, builder: type[RuntimeBuilder]) -> None:
        """
        Register a runtime builder.

        Parameters
        ----------
        name : str
            The unique identifier for the builder.
        builder : type[RuntimeBuilder]
            The builder class to register. It will be instantiated immediately.

        Returns
        -------
        None

        Raises
        ------
        BuilderError
            If a builder with the same name already exists.
        """
        if name in self._runtime_builders:
            raise BuilderError(f"Builder {name} already exists.")
        self._runtime_builders[name] = builder()

    def build_entity_from_params(self, **kwargs) -> Entity:
        """
        Build an entity from parameters.

        Parameters
        ----------
        **kwargs
            Entity parameters.

        Returns
        -------
        Entity
            Entity object.
        """
        try:
            kind = kwargs["kind"]
        except KeyError:
            raise BuilderError("Missing 'kind' parameter.")
        builder = self._get_entity_builder(kind)
        return builder.build(**kwargs)

    def build_entity_from_dict(self, obj: dict) -> Entity:
        """
        Build an entity from a dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary with entity data.

        Returns
        -------
        Entity
            Entity object.
        """
        try:
            kind = obj["kind"]
        except KeyError:
            raise BuilderError("Missing 'kind' parameter.")
        builder = self._get_entity_builder(kind)
        return builder.from_dict(obj)

    def build_spec(self, kind_to_build_from: str, **kwargs) -> Spec:
        """
        Build an entity spec.

        Parameters
        ----------
        kind_to_build_from : str
            Entity type.
        **kwargs
            Additional spec parameters.

        Returns
        -------
        Spec
            Spec object.
        """
        builder = self._get_entity_builder(kind_to_build_from)
        return builder.build_spec(**kwargs)

    def build_metadata(self, kind_to_build_from: str, **kwargs) -> Metadata:
        """
        Build an entity metadata.

        Parameters
        ----------
        kind_to_build_from : str
            Entity type.
        **kwargs
            Additional metadata parameters.

        Returns
        -------
        Metadata
            Metadata object.
        """
        builder = self._get_entity_builder(kind_to_build_from)
        return builder.build_metadata(**kwargs)

    def build_status(self, kind_to_build_from: str, **kwargs) -> Status:
        """
        Build an entity status.

        Parameters
        ----------
        kind_to_build_from : str
            Entity type.
        **kwargs
            Additional status parameters.

        Returns
        -------
        Status
            Status object.
        """
        builder = self._get_entity_builder(kind_to_build_from)
        return builder.build_status(**kwargs)

    def build_runtime(self, kind_to_build_from: str, project: str) -> Runtime:
        """
        Build a runtime.

        Parameters
        ----------
        kind_to_build_from : str
            Runtime type.
        project : str
            Project name.

        Returns
        -------
        Runtime
            Runtime object.
        """
        builder = self._get_runtime_builder(kind_to_build_from)
        return builder.build(project=project)

    def get_entity_type_from_kind(self, kind: str) -> str:
        """
        Get entity type from builder.

        Parameters
        ----------
        kind : str
            Entity type.

        Returns
        -------
        str
            Entity type.
        """
        builder = self._get_entity_builder(kind)
        return builder.get_entity_type()

    def get_executable_kind(self, kind: str) -> str:
        """
        Get executable kind.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        str
            Executable kind.
        """
        builder = self._get_entity_builder(kind)
        return builder.get_executable_kind()

    def get_action_from_task_kind(self, kind: str, task_kind: str) -> str:
        """
        Get action from task.

        Parameters
        ----------
        kind : str
            Kind.
        task_kind : str
            Task kind.

        Returns
        -------
        str
            Action.
        """
        builder = self._get_entity_builder(kind)
        return builder.get_action_from_task_kind(task_kind)

    def get_task_kind_from_action(self, kind: str, action: str) -> list[str]:
        """
        Get task kinds from action.

        Parameters
        ----------
        kind : str
            Kind.
        action : str
            Action.

        Returns
        -------
        list of str
            Task kinds.
        """
        builder = self._get_entity_builder(kind)
        return builder.get_task_kind_from_action(action)

    def get_run_kind_from_action(self, kind: str, action: str) -> str:
        """
        Get run kind.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        str
            Run kind.
        """
        builder = self._get_entity_builder(kind)
        return builder.get_run_kind_from_action(action)

    def get_all_kinds(self, kind: str) -> list[str]:
        """
        Get all kinds.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        list of str
            All kinds.
        """
        builder = self._get_entity_builder(kind)
        return builder.get_all_kinds()

    def get_spec_validator(self, kind: str) -> SpecValidator:
        """
        Get spec validators.

        Parameters
        ----------
        kind : str
            Kind.

        Returns
        -------
        SpecValidator
            Spec validator.
        """
        builder = self._get_entity_builder(kind)
        return builder.get_spec_validator()

    def _get_entity_builder(self, kind: str) -> EntityBuilder | RuntimeEntityBuilder:
        """
        Return the entity builder for the given kind, ensuring lazy runtime registration.

        Raises
        ------
        BuilderError
            If no builder exists for the specified kind.
        """
        if not self._entities_registered:
            self._ensure_entities_registered()
        if kind not in self._entity_builders:
            if not self._runtimes_registered:
                self._ensure_runtimes_registered()
            if kind not in self._entity_builders:
                raise BuilderError(f"Entity builder for kind '{kind}' not found.")
        return self._entity_builders[kind]

    def _get_runtime_builder(self, kind: str) -> RuntimeBuilder:
        """
        Return the runtime builder for the given kind, ensuring lazy runtime registration.

        Raises
        ------
        BuilderError
            If no builder exists for the specified kind.
        """
        if kind not in self._runtime_builders:
            if not self._runtimes_registered:
                self._ensure_runtimes_registered()
            if kind not in self._runtime_builders:
                raise BuilderError(f"Runtime builder for kind '{kind}' not found.")
        return self._runtime_builders[kind]

    def _ensure_entities_registered(self) -> None:
        """
        Ensure core entities are registered on-demand.

        Returns
        -------
        None
        """
        if self._entities_registered:
            return
        try:
            self._register_entities()
            self._entities_registered = True
        except Exception as e:
            # Avoid repeated attempts; surface as BuilderError for consistency
            self._entities_registered = True
            raise BuilderError(f"Failed to register core entities: {e}")

    def _register_entities(self) -> None:
        """
        Register core entity builders into the factory.

        Imports the core entities module and registers all entity
        builders with the global factory instance.

        Returns
        -------
        None
        """
        try:
            module = import_module(FactoryEnum.REG_ENTITIES.value)

            # Register core entities
            for k, b in getattr(module, FactoryEnum.REG_ENTITIES_VAR.value, []):
                self.add_entity_builder(k, b)

        except Exception as e:
            raise RuntimeError("Error registering core entities.") from e

    def _ensure_runtimes_registered(self) -> None:
        """
        Ensure runtime entities are registered on-demand.

        Returns
        -------
        None
        """
        if self._runtimes_registered:
            return
        try:
            self._register_runtimes_entities()
            self._runtimes_registered = True
        except Exception as e:
            # If registration fails, mark as attempted to avoid infinite loops
            self._runtimes_registered = True
            raise BuilderError(f"Failed to register runtime entities: {e}")

    def _register_runtimes_entities(self) -> None:
        """
        Register all runtime builders and their entities into the factory.

        Imports each runtime package and registers its entity and runtime
        builders with the global factory instance.

        Returns
        -------
        None
        """
        try:
            for package in list_runtimes():
                module = import_module(package)

                # Register workflows, functions, tasks and runs entities builders
                for k, b in getattr(module, FactoryEnum.REG_ENTITIES_VAR.value, []):
                    self.add_entity_builder(k, b)

                # Register runtime builders
                for k, b in getattr(module, FactoryEnum.REG_RUNTIME_VAR.value, []):
                    self.add_runtime_builder(k, b)
        except Exception as e:
            raise RuntimeError("Error registering runtime entities.") from e


factory = Factory()
