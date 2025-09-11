"""Using `pydantic`_, we define configurations for the package.

Most importantly, these configurations are part of the CLIs that the package provides.
but they also help with programmatically validating and constructing various objects.
Maybe most importantly, the :py:class:`GraphConfig` and :py:class:`ModelConfig` may be
used to precisely and reproducibly define how the function :py:func:`construct_model`
should create lymphatic progression :py:mod:`~lymph.models`.

.. _pydantic: https://docs.pydantic.dev/latest/
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import warnings
from collections.abc import Callable, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Annotated, Any, Literal

import numpy as np
import pandas as pd
import yaml
from loguru import logger
from lydata.loader import LyDataset
from lydata.utils import ModalityConfig
from lymph import graph, models
from lymph.modalities import Pathological
from lymph.types import Model, PatternType
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    FilePath,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)
from pydantic_settings.sources import DEFAULT_PATH

from lyscripts.utils import binom_pmf, flatten, load_model_samples, load_patient_data

FuncNameType = Literal["binomial"]


DIST_MAP: dict[FuncNameType, Callable] = {
    "binomial": binom_pmf,
}


class CrossValidationConfig(BaseModel):
    """Configs for splitting a dataset into cross-validation folds."""

    seed: int = Field(
        default=42,
        description="Seed for the random number generator.",
    )
    folds: int = Field(
        default=5,
        description="Number of folds to split the dataset into.",
    )


class DataConfig(BaseModel):
    """Where to load lymphatic progression data from and how to feed it into a model."""

    source: FilePath | LyDataset = Field(
        description=(
            "Either a path to a CSV file or a config that specifies how and where "
            "to fetch the data from."
        ),
    )
    side: Literal["ipsi", "contra"] | None = Field(
        default=None,
        description="Side of the neck to load data for. Only for Unilateral models.",
    )
    mapping: dict[Literal[0, 1, 2, 3, 4] | str, int | str] = Field(
        default_factory=lambda: {i: "early" if i <= 2 else "late" for i in range(5)},
        description="Optional mapping of numeric T-stages to model T-stages.",
    )

    def load(self, **get_dataframe_kwargs) -> pd.DataFrame:
        """Load data from path or the :py:class:`~lydata.loader.LyDataset`."""
        if isinstance(self.source, LyDataset):
            return self.source.get_dataframe(**get_dataframe_kwargs)

        return load_patient_data(self.source, **get_dataframe_kwargs)

    def get_load_kwargs(self, **read_csv_kwargs: dict[str, Any]) -> dict[str, Any]:
        """Get kwargs for :py:meth:`~lymph.types.Model.load_patient_data`."""
        return {
            "patient_data": self.load(**(read_csv_kwargs or {})),
            **self.model_dump(exclude={"source"}, exclude_none=True),
        }


def check_pattern(value: PatternType) -> Any:
    """Check if the value can be converted to a boolean value."""
    return {lnl: map_to_optional_bool(v) for lnl, v in value.items()}


class DiagnosisConfig(BaseModel):
    """Defines an ipsi- and contralateral diagnosis pattern."""

    ipsi: dict[str, Annotated[PatternType, AfterValidator(check_pattern)]] = Field(
        default={},
        description="Observed diagnoses by different modalities on the ipsi neck.",
        examples=[{"CT": {"II": True, "III": False}}],
    )
    contra: dict[str, Annotated[PatternType, AfterValidator(check_pattern)]] = Field(
        default={},
        description="Observed diagnoses by different modalities on the contra neck.",
    )

    def to_involvement(self, modality: str) -> InvolvementConfig:
        """Convert the diagnosis pattern to an involvement pattern for ``modality``."""
        return InvolvementConfig(
            ipsi=self.ipsi.get(modality, {}),
            contra=self.contra.get(modality, {}),
        )


class DistributionConfig(BaseModel):
    """Configuration defining a distribution over diagnose times."""

    kind: Literal["frozen", "parametric"] = Field(
        default="frozen",
        description="Parametric distributions may be updated.",
    )
    func: FuncNameType = Field(
        default="binomial",
        description="Name of predefined function to use as distribution.",
    )
    params: dict[str, int | float] = Field(
        default={},
        description="Parameters to pass to the predefined function.",
    )


class InvolvementConfig(BaseModel):
    """Config that defines an ipsi- and contralateral involvement pattern."""

    ipsi: Annotated[PatternType, AfterValidator(check_pattern)] = Field(
        default={},
        description="Involvement pattern for the ipsilateral side of the neck.",
        examples=[{"II": True, "III": False}],
    )
    contra: Annotated[PatternType, AfterValidator(check_pattern)] = Field(
        default={},
        description="Involvement pattern for the contralateral side of the neck.",
    )


def retrieve_graph_representation(model: Model) -> graph.Representation:
    """Retrieve the graph representation from a model."""
    if hasattr(model, "graph"):
        return model.graph

    if hasattr(model, "hpv"):
        return retrieve_graph_representation(model.hpv)

    if hasattr(model, "ipsi"):
        return retrieve_graph_representation(model.ipsi)

    if hasattr(model, "ext"):
        return retrieve_graph_representation(model.ext)

    raise ValueError("Model does not have a graph representation.")


class GraphConfig(BaseModel):
    """Specifies how the tumor(s) and LNLs are connected in a DAG."""

    tumor: dict[str, list[str]] = Field(
        description="Define the name of the tumor(s) and which LNLs it/they drain to.",
    )
    lnl: dict[str, list[str]] = Field(
        description="Define the name of the LNL(s) and which LNLs it/they drain to.",
    )

    @classmethod
    def from_model(cls: type, model: Model) -> GraphConfig:
        """Create a ``GraphConfig`` from a ``Model``."""
        graph = retrieve_graph_representation(model)
        return cls(
            tumor={
                name: [edge.child.name for edge in tumor.out]
                for name, tumor in graph.tumors.items()
            },
            lnl={
                name: [edge.child.name for edge in lnl.out]  # noqa
                for name, lnl in graph.lnls.items()
            },
        )


def has_model_symbol(path: Path) -> Path:
    """Check if the Python file at ``path`` defines a symbol named ``model``."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "model"):
        raise ValueError(f"Python file at {path} does not define a symbol 'model'.")

    return path


def get_symmetry_kwargs(model: Model) -> dict[str, Any]:
    """Get the symmetry kwargs from a model."""
    if isinstance(model, models.Unilateral | models.HPVUnilateral):
        raise TypeError("Unilateral models do not have symmetry kwargs.")

    if hasattr(model, "ext"):
        return get_symmetry_kwargs(model.ext)

    return getattr(model, "is_symmetric", {})


class ModelConfig(BaseModel):
    """Define which of the ``lymph`` models to use and how to set them up."""

    external_file: Annotated[FilePath, AfterValidator(has_model_symbol)] | None = Field(
        default=None,
        description="Path to a Python file that defines a model.",
    )
    class_name: Literal["Unilateral", "Bilateral", "Midline"] = Field(
        default="Unilateral",
        description="Name of the model class to use.",
    )
    constructor: Literal["binary", "trinary"] = Field(
        default="binary",
        description="Trinary models differentiate btw. micro- and macroscopic disease.",
    )
    max_time: int = Field(
        default=10,
        description="Max. number of time-steps to evolve the model over.",
    )
    named_params: Sequence[str] = Field(
        default=None,
        description=(
            "Subset of valid model parameters a sampler may provide in the form of a "
            "dictionary to the model instead of as an array. Or, after sampling, with "
            "this list, one may safely recover which parameter corresponds to which "
            "index in the sample."
        ),
    )
    kwargs: dict[str, Any] = Field(
        default={},
        description="Additional keyword arguments to pass to the model constructor.",
    )

    @classmethod
    def from_model(cls: type, model: Model) -> ModelConfig:
        """Create a ``ModelConfig`` from a ``Model``."""
        warnings.warn(
            message=(
                "Not all kwargs passed at initialization can be recovered into a "
                "config. Make sure to manually double-check the config."
            ),
            category=UserWarning,
            stacklevel=2,
        )

        if getattr(model, "_named_params", None):
            additional_kwargs = {"named_params": list(model.named_params)}
        else:
            additional_kwargs = {}

        try:
            additional_kwargs["is_symmetric"] = get_symmetry_kwargs(model)
        except TypeError:
            pass

        if isinstance(model, models.Midline):
            additional_kwargs["use_midext_evo"] = model.use_midext_evo
            additional_kwargs["use_central"] = hasattr(model, "_central")
            additional_kwargs["use_mixing"] = hasattr(model, "mixing_param")

            if not hasattr(model, "_unknown"):
                additional_kwargs["marginalize_unknown"] = False

        return cls(
            class_name=model.__class__.__name__,
            constructor="trinary" if model.is_trinary else "binary",
            max_time=model.max_time,
            kwargs=additional_kwargs,
        )


def modalityconfig_from_model(model: Model, modality_name: str) -> ModalityConfig:
    """Create a ``ModalityConfig`` from a ``Model``."""
    modality = model.get_modality(modality_name)
    return ModalityConfig(
        spec=modality.spec,
        sens=modality.sens,
        kind="pathological" if isinstance(modality, Pathological) else "clinical",
    )


class DeprecatedModelConfig(BaseModel):
    """Model configuration prior to ``lyscripts`` major version 1.

    This is implemented for backwards compatibility. Its sole job is to translate
    the outdated settings format into the new one. Note that the only stuff that needs
    to be translated is the model configuration itself and the distributions for
    marginalization over diagnosis times. The :py:class:`~GraphConfig` is still
    compatible.
    """

    first_binom_prob: float = Field(
        description="Fixed parameter for first binomial dist over diagnosis times.",
        ge=0.0,
        le=1.0,
    )
    max_t: int = Field(
        description="Max. number of time-steps to evolve the model over.",
        gt=0,
    )
    t_stages: list[int | str] = Field(
        description=(
            "List of T-stages to marginalize over in the scenario. The old format "
            "assumed all T-stages except the first one to be parametric. Only binomial "
            "distributions are supported."
        ),
    )
    class_: Literal["Unilateral", "Bilateral", "Midline", "MidlineBilateral"] = Field(
        description="Name of the model class. Only binary models are supported.",
        alias="class",
    )
    kwargs: dict[str, Any] = Field(
        default={},
        description="Additional keyword arguments to pass to the model constructor.",
    )

    def model_post_init(self, __context):
        """Issue a deprecation warning."""
        warnings.warn(
            message="The 'DeprecatedModelConfig' is deprecated.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        if "Midline" in self.class_:
            self.class_ = "Midline"
            warnings.warn(
                "Model may not be recreated as expected due to extra parameter "
                "`midext_prob`. Make sure to manually handle edge cases.",
                stacklevel=2,
            )
        return super().model_post_init(__context)

    def translate(self) -> tuple[ModelConfig, dict[int | str, DistributionConfig]]:
        """Translate the deprecated model config to the new format."""
        old_kwargs = self.kwargs.copy()
        new_kwargs = {"use_midext_evo": False} if "Midline" in self.class_ else {}

        if (tumor_spread := old_kwargs.pop("base_symmetric")) is not None:
            new_kwargs["is_symmetric"] = new_kwargs.get("is_symmetric", {})
            new_kwargs["is_symmetric"]["tumor_spread"] = tumor_spread

        if (lnl_spread := old_kwargs.pop("trans_symmetric")) is not None:
            new_kwargs["is_symmetric"] = new_kwargs.get("is_symmetric", {})
            new_kwargs["is_symmetric"]["lnl_spread"] = lnl_spread

        new_kwargs.update(old_kwargs)

        model_config = ModelConfig(
            class_name=self.class_,
            constructor="binary",
            max_time=self.max_t,
            kwargs=new_kwargs,
        )

        distribution_configs = {}
        for i, t_stage in enumerate(self.t_stages):
            distribution_configs[t_stage] = DistributionConfig(
                kind="frozen" if i == 0 else "parametric",
                func="binomial",
                params={"p": self.first_binom_prob},
            )

        return model_config, distribution_configs


class SamplingConfig(BaseModel):
    """Settings to configure the MCMC sampling."""

    storage_file: Path = Field(
        description="Path to HDF5 file store results or load last state.",
    )
    history_file: Path | None = Field(
        default=None,
        description="Path to store the burn-in metrics (as CSV file).",
    )
    dataset: str = Field(
        default="mcmc",
        description="Name of the dataset in the HDF5 file.",
    )
    cores: int | None = Field(
        gt=0,
        default=os.cpu_count(),
        description=(
            "Number of cores to use for parallel sampling. If `None`, no parallel "
            "processing is used."
        ),
    )
    seed: int = Field(
        default=42,
        description="Seed for the random number generator.",
    )
    walkers_per_dim: int = Field(
        default=20,
        description="Number of walkers per parameter space dimension.",
    )
    check_interval: int = Field(
        default=50,
        description="Check for convergence each time after this many steps.",
    )
    trust_factor: float = Field(
        default=50.0,
        description=(
            "Trust the autocorrelation time only when it's smaller than this factor "
            "times the length of the chain."
        ),
    )
    relative_thresh: float = Field(
        default=0.05,
        description="Relative threshold for convergence.",
    )
    burnin_steps: int | None = Field(
        default=None,
        description=(
            "Number of burn-in steps to take. If None, burn-in runs until convergence."
        ),
    )
    num_steps: int | None = Field(
        default=100,
        description=("Number of steps to take in the MCMC sampling."),
    )
    thin_by: int = Field(
        default=10,
        description="How many samples to draw before for saving one.",
    )
    inverse_temp: float = Field(
        default=1.0,
        description=(
            "Inverse temperature for thermodynamic integration. Note that this is not "
            "yet fully implemented."
        ),
    )

    def load(self, thin: int = 1) -> np.ndarray:
        """Load the samples from the HDF5 file.

        Note that the ``thin`` represents another round of thinning and is usually
        not necessary if the samples were already thinned during the sampling process.
        """
        return load_model_samples(
            file_path=self.storage_file,
            name=self.dataset,
            thin=thin,
        )


def geometric_schedule(num: int, *_a) -> np.ndarray:
    """Create a geometric sequence of ``num`` numbers from 0 to 1."""
    log_seq = np.logspace(0.0, 1.0, num)
    shifted_seq = log_seq - 1.0
    return shifted_seq / 9.0


def linear_schedule(num: int, *_a) -> np.ndarray:
    """Create a linear sequence of ``num`` numbers from 0 to 1.

    Equivalent to the :py:func:`power_schedule` with ``power=1``.
    """
    return np.linspace(0.0, 1.0, num)


def power_schedule(num: int, power: float, *_a) -> np.ndarray:
    """Create a power sequence of ``num`` numbers from 0 to 1.

    This is essentially a :py:func:`linear_schedule` of ``num`` numbers from 0 to 1,
    but each number is raised to the power of ``power``.
    """
    lin_seq = np.linspace(0.0, 1.0, num)
    return lin_seq**power


SCHEDULES = {
    "geometric": geometric_schedule,
    "linear": linear_schedule,
    "power": power_schedule,
}


class ScheduleConfig(BaseModel):
    """Configuration for generating a schedule of inverse temperatures."""

    method: Literal["geometric", "linear", "power"] = Field(
        default="power",
        description="Method to generate the inverse temperature schedule.",
    )
    num: int = Field(
        default=32,
        description="Number of inverse temperatures in the schedule.",
    )
    power: float = Field(
        default=4.0,
        description="If a power schedule is chosen, use this as power.",
    )
    values: list[float] | None = Field(
        default=None,
        description=(
            "List of inverse temperatures to use instead of generating a schedule. "
            "If a list is provided, the other parameters are ignored."
        ),
    )

    def get_schedule(self) -> np.ndarray:
        """Get the inverse temperature schedule as a numpy array."""
        if self.values is not None:
            logger.debug("Using provided inverse temperature values.")
            schedule = np.array(self.values)
        else:
            logger.debug(f"Generating inverse temperature schedule with {self.method}.")
            func = SCHEDULES[self.method]
            schedule = func(self.num, self.power)

        logger.info(f"Generated inverse temperature schedule: {schedule}")
        return schedule


def map_to_optional_bool(value: Any) -> Any:
    """Try to convert the options in the `PatternType` to a boolean value."""
    if value in [True, "involved", 1]:
        return True

    if value in [False, "healthy", 0]:
        return False

    return value


class ScenarioConfig(BaseModel):
    """Define a scenario for which e.g. prevalences and risks may be computed."""

    t_stages: list[int | str] = Field(
        description="List of T-stages to marginalize over in the scenario.",
        examples=[["early"], [3, 4]],
    )
    t_stages_dist: list[float] = Field(
        default=[1.0],
        description="Distribution over T-stages to use for marginalization.",
        examples=[[1.0], [0.6, 0.4]],
    )
    midext: bool | None = Field(
        default=None,
        description="Whether the patient's tumor extends over the midline.",
    )
    mode: Literal["HMM", "BN"] = Field(
        default="HMM",
        description="Which underlying model architecture to use.",
    )
    involvement: InvolvementConfig = InvolvementConfig()
    diagnosis: DiagnosisConfig = DiagnosisConfig()

    def model_post_init(self, __context: Any) -> None:
        """Interpolate and normalize the distribution."""
        self.interpolate()
        self.normalize()

    def interpolate(self):
        """Interpolate the distribution to the number of ``t_stages``."""
        if len(self.t_stages) != len(self.t_stages_dist):
            new_x = np.linspace(0.0, 1.0, len(self.t_stages))
            old_x = np.linspace(0.0, 1.0, len(self.t_stages_dist))
            # cast to list to make ``__eq__`` work
            self.t_stages_dist = np.interp(new_x, old_x, self.t_stages_dist).tolist()

    def normalize(self):
        """Normalize the distribution to sum to 1."""
        if not np.isclose(np.sum(self.t_stages_dist), 1.0):
            self.t_stages_dist = (
                np.array(self.t_stages_dist) / np.sum(self.t_stages_dist)
            ).tolist()  # cast to list to make ``__eq__`` work


def _construct_model_from_external(path: Path) -> Model:
    """Construct a model from a Python file."""
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    logger.info(f"Loaded model from {path}. This ignores model and graph configs.")
    return module.model


def construct_model(
    model_config: ModelConfig,
    graph_config: GraphConfig,
) -> Model:
    """Construct a model from a ``model_config``.

    The default/expected use of this is to specify a model class from the
    `lymph`_ package and pass the necessary arguments to its constructor.
    However, it is also possible to load a model from an external Python file via the
    ``external`` attribute of the ``model_config`` argument. In this case, a symbol
    with name ``model`` must be defined in the file that is to be loaded.

    .. note::

        No check is performed on the model's compatibility with the command/pipeline
        it is used in. It is assumed the model complies with the
        :py:class:`model type <lymph.types.Model>` specifications of the `lymph`_
        package.

    .. _lymph: https://lymph-model.readthedocs.io/stable/
    """
    if model_config.external_file is not None:
        return _construct_model_from_external(model_config.external_file)

    cls = getattr(models, model_config.class_name)
    constructor = getattr(cls, model_config.constructor)
    model = constructor(
        graph_dict=flatten(graph_config.model_dump()),
        max_time=model_config.max_time,
        named_params=model_config.named_params,
        **model_config.kwargs,
    )
    logger.info(f"Constructed model: {model}")
    return model


def add_distributions(
    model: Model,
    configs: dict[str | int, DistributionConfig],
    mapping: dict[FuncNameType, Callable] | None = None,
    inplace: bool = False,
) -> Model:
    """Construct and add distributions over diagnose times to a ``model``."""
    if not inplace:
        model = deepcopy(model)
        logger.debug("Created deepcopy of model.")

    mapping = mapping or DIST_MAP

    for t_stage, dist_config in configs.items():
        if dist_config.kind == "frozen":
            support = np.arange(model.max_time + 1)
            dist = mapping[dist_config.func](support, **dist_config.params)
        elif dist_config.kind == "parametric":
            dist = mapping[dist_config.func]
        else:
            raise ValueError(f"Unknown distribution kind: {dist_config.kind}")

        model.set_distribution(t_stage, dist)
        if dist_config.kind == "parametric" and dist_config.params:
            params = {f"{t_stage}_{k}": v for k, v in dist_config.params.items()}
            model.set_params(**params)

        logger.debug(f"Set {dist_config.kind} distribution for '{t_stage}': {dist}")

    logger.info(f"Added {len(configs)} distributions to model: {model}")
    return model


def add_modalities(
    model: Model,
    modalities: dict[str, ModalityConfig],
    inplace: bool = False,
) -> Model:
    """Add ``modalities`` to a ``model``."""
    if not inplace:
        model = deepcopy(model)
        logger.debug("Created deepcopy of model.")

    for modality, modality_config in modalities.items():
        model.set_modality(modality, **modality_config.model_dump())
        logger.debug(f"Added modality {modality} to model: {modality_config}")

    logger.info(f"Added {len(modalities)} modalities to model: {model}")
    return model


def add_data(
    model: Model,
    path: Path,
    side: Literal["ipsi", "contra"],
    mapping: dict[Literal[0, 1, 2, 3, 4], int | str] | None = None,
    inplace: bool = False,
) -> Model:
    """Add data to a ``model``."""
    data = pd.read_csv(path, header=[0, 1, 2])
    logger.debug(f"Loaded data from {path}: Shape: {data.shape}")

    kwargs = {"patient_data": data, "mapping": mapping}
    if isinstance(model, models.Unilateral):
        kwargs["side"] = side

    if not inplace:
        model = deepcopy(model)
        logger.debug("Created deepcopy of model.")

    model.load_patient_data(**kwargs)
    logger.info(f"Added data to model: {model}")
    return model


PathType = Path | str | Sequence[Path | str]


class DynamicYamlConfigSettingsSource(YamlConfigSettingsSource):
    """YAML config source that allows dynamic file path specification.

    This is heavily inspired by `this comment`_ in the discussion on a related issue
    of the `pydantic-settings`_ GitHub repository.

    Essentially, this little hack allows a user to specify a one or multiple YAML files
    from which the CLI should read configurations. Normally, `pydantic-settings` only
    allows hard-coding the location of these config files.

    .. _this comment: https://github.com/pydantic/pydantic-settings/issues/259#issuecomment-2549444286
    .. _pydantic-settings: https://github.com/pydantic/pydantic-settings
    """

    def __init__(
        self,
        settings_cls,
        yaml_file: PathType | None = DEFAULT_PATH,
        yaml_file_encoding: str | None = None,
        yaml_file_path_field: str = "configs",
    ) -> None:
        """Allow getting the YAML file path from any key in the current state.

        The argument ``yaml_file_path_field`` should be the :py:class:`BaseSettings`
        field that contains the path(s) to the YAML file(s).

        Note that all config files must have a ``version: 1`` key in them to be
        recognized as valid config files.
        """
        self.yaml_file_path_field = yaml_file_path_field
        super().__init__(settings_cls, yaml_file, yaml_file_encoding)

    def _read_file(self, file_path: Path) -> dict[str, Any]:
        """Read the YAML and raise exception when ``version: 1`` not found."""
        with open(file_path, encoding=self.yaml_file_encoding) as yaml_file:
            data = yaml.safe_load(yaml_file) or {}
            if data.get("version") != 1:
                raise ValueError(
                    f"Config file {file_path} does not have a 'version: 1' key. "
                    "For compatibility reasons, all config files must have this key.",
                )
            return data

    def __call__(self) -> dict[str, Any]:
        """Reload the config files from the paths in the current state."""
        yaml_file_to_reload = self.current_state.get(
            self.yaml_file_path_field,
            self.yaml_file_path,
        )
        logger.debug(f"Reloading YAML files from {yaml_file_to_reload} (if it exists).")
        self.__init__(
            settings_cls=self.settings_cls,
            yaml_file=yaml_file_to_reload,
            yaml_file_encoding=self.yaml_file_encoding,
            yaml_file_path_field=self.yaml_file_path_field,
        )
        return super().__call__()

    def __repr__(self) -> str:
        """Return a string representation of the source."""
        return (
            self.__class__.__name__
            + "("
            + f"yaml_file={self.yaml_file_path!r}, "
            + f"yaml_file_encoding={self.yaml_file_encoding!r}, "
            + f"yaml_file_path_field={self.yaml_file_path_field!r}"
            + ")"
        )


class BaseCLI(BaseSettings):
    """Base settings class for all CLI scripts to inherit from."""

    model_config = ConfigDict(yaml_file="config.yaml", extra="ignore")

    configs: list[Path] = Field(
        default=["config.yaml"],
        description=(
            "Path to the YAML file(s) that contain the configuration(s). Configs from "
            "YAML files may be overwritten by command line arguments. When multiple "
            "files are specified, the configs are merged in the order they are given. "
            "Note that every config file must have a `version: 1` key in it."
        ),
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Add the dynamic YAML config source to the CLI settings."""
        dynamic_yaml_config_source = DynamicYamlConfigSettingsSource(
            settings_cls=settings_cls,
            yaml_file_path_field="configs",
            yaml_file_encoding="utf-8",
        )
        logger.debug(f"Created {dynamic_yaml_config_source = }")
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            dynamic_yaml_config_source,
        )
