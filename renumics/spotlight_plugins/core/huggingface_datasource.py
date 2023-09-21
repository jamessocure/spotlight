from typing import List, Optional, Union, cast

import datasets
import numpy as np
from renumics.spotlight import dtypes

from renumics.spotlight.data_source import DataSource
from renumics.spotlight.data_source.decorator import datasource
from renumics.spotlight.dtypes import DType, DTypeMap
from renumics.spotlight.data_source.data_source import ColumnMetadata


_FeatureType = Union[
    datasets.Value,
    datasets.ClassLabel,
    datasets.Sequence,
    datasets.Array2D,
    datasets.Array3D,
    datasets.Array4D,
    datasets.Array5D,
    datasets.Audio,
    datasets.Image,
    datasets.Translation,
    dict,
    list,
]


class UnsupportedFeature(Exception):
    """
    We encountered an unsupported datasets Feature
    """

    def __init__(self, feature: _FeatureType) -> None:
        super().__init__(f"Unsupported HuggingFace Feature: {type(feature)}")


@datasource(datasets.Dataset)
class HuggingfaceDataSource(DataSource):
    _dataset: datasets.Dataset
    _intermediate_dtypes: DTypeMap
    _guessed_dtypes: DTypeMap

    def __init__(self, source: datasets.Dataset):
        super().__init__(source)
        self._dataset = source
        self._intermediate_dtypes = {
            col: _get_intermediate_dtype(feat)
            for col, feat in self._dataset.features.items()
        }
        self._guessed_dtypes = {}
        for col, feat in self._dataset.features.items():
            guessed_dtype = _guess_semantic_dtype(feat)
            if guessed_dtype:
                self._guessed_dtypes[col] = guessed_dtype

    @property
    def column_names(self) -> List[str]:
        return self._dataset.column_names

    @property
    def intermediate_dtypes(self) -> DTypeMap:
        return self._intermediate_dtypes

    def __len__(self) -> int:
        return len(self._dataset)

    @property
    def semantic_dtypes(self) -> DTypeMap:
        return self._guessed_dtypes

    def get_generation_id(self) -> int:
        return 0

    def get_uid(self) -> str:
        return self._dataset._fingerprint

    def get_name(self) -> str:
        return self._dataset.builder_name

    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        if isinstance(indices, slice):
            if indices == slice(None):
                raw_values = self._dataset.data[column_name]
            else:
                # TODO: handle slices
                assert False
        else:
            raw_values = self._dataset.data[column_name].take(indices)

        feature = self._dataset.features[column_name]
        if isinstance(feature, datasets.Audio) or isinstance(feature, datasets.Image):
            return np.array(
                [
                    value["path"].as_py()
                    if value["bytes"].as_py() is None
                    else value["bytes"].as_py()
                    for value in raw_values
                ],
                dtype=object,
            )
        if isinstance(feature, dict):
            return np.array(
                [value["bytes"].as_py() for value in raw_values], dtype=object
            )
        if isinstance(feature, datasets.Sequence):
            return raw_values.to_numpy()
        else:
            return raw_values.to_numpy()

    def get_column_metadata(self, _: str) -> ColumnMetadata:
        return ColumnMetadata(nullable=True, editable=False)


def _guess_semantic_dtype(feature: _FeatureType) -> Optional[DType]:
    if isinstance(feature, datasets.Audio):
        return dtypes.audio_dtype
    if isinstance(feature, datasets.Image):
        return dtypes.image_dtype
    if isinstance(feature, datasets.Sequence):
        if isinstance(feature.feature, datasets.Value):
            if feature.length != -1:
                return dtypes.embedding_dtype
    return None


def _get_intermediate_dtype(feature: _FeatureType) -> DType:
    if isinstance(feature, datasets.Value):
        hf_dtype = cast(datasets.Value, feature).dtype
        if hf_dtype == "bool":
            return dtypes.bool_dtype
        elif hf_dtype == "int8":
            return dtypes.int_dtype
        elif hf_dtype == "int16":
            return dtypes.int_dtype
        elif hf_dtype == "int32":
            return dtypes.int_dtype
        elif hf_dtype == "int64":
            return dtypes.int_dtype
        elif hf_dtype == "float16":
            return dtypes.float_dtype
        elif hf_dtype == "float32":
            return dtypes.float_dtype
        elif hf_dtype == "float64":
            return dtypes.float_dtype
        elif hf_dtype.startswith("time32"):
            return dtypes.datetime_dtype
        elif hf_dtype.startswith("time64"):
            return dtypes.datetime_dtype
        elif hf_dtype.startswith("timestamp"):
            return dtypes.datetime_dtype
        elif hf_dtype.startswith("date32"):
            return dtypes.datetime_dtype
        elif hf_dtype.startswith("date64"):
            return dtypes.datetime_dtype
        elif hf_dtype.startswith("duration"):
            return dtypes.float_dtype
        elif hf_dtype.startswith("decimal"):
            return dtypes.float_dtype
        elif hf_dtype == "binary":
            return dtypes.bytes_dtype
        elif hf_dtype == "large_binary":
            return dtypes.bytes_dtype
        elif hf_dtype == "string":
            return dtypes.str_dtype
        elif hf_dtype == "large_string":
            return dtypes.str_dtype
        else:
            raise UnsupportedFeature(feature)
    elif isinstance(feature, datasets.ClassLabel):
        return dtypes.CategoryDType(categories=cast(datasets.ClassLabel, feature).names)
    elif isinstance(feature, datasets.Audio):
        return dtypes.file_dtype
    elif isinstance(feature, datasets.Image):
        return dtypes.file_dtype
    elif isinstance(feature, datasets.Sequence):
        if isinstance(feature.feature, datasets.Value):
            return dtypes.array_dtype
        else:
            raise UnsupportedFeature(feature)
    elif isinstance(feature, dict):
        if len(feature) == 2 and "bytes" in feature and "path" in feature:
            return dtypes.file_dtype
        else:
            raise UnsupportedFeature(feature)
    else:
        raise UnsupportedFeature(feature)
