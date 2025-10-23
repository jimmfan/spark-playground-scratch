# pip install skl2onnx
from typing import List, Tuple, Dict, Optional
import re
from skl2onnx.common.data_types import (
    FloatTensorType, StringTensorType, Int64TensorType, BooleanTensorType
)

def hive_type_to_onnx_tensor(
    hive_type: str,
    *,
    force_float_numeric: bool = True,   # recommended for sklearn pipelines
    decimals_as: str = "float",         # "float" (recommended) or "int64" (if you pre-scale decimals)
    per_feature_shape = (None, 1),
):
    """Map a Hive type string to an ONNX TensorType (factory)."""
    t = hive_type.strip().lower()

    # strings
    if t == "string" or t.startswith("varchar") or t.startswith("char"):
        return StringTensorType(list(per_feature_shape))

    # booleans (included for completeness)
    if t in {"boolean", "bool"}:
        return BooleanTensorType(list(per_feature_shape))

    # integers
    if t in {"tinyint", "smallint", "int", "integer", "bigint"}:
        if force_float_numeric:
            return FloatTensorType(list(per_feature_shape))
        return Int64TensorType(list(per_feature_shape))

    # floating point
    if t in {"float", "double", "real", "double precision"}:
        return FloatTensorType(list(per_feature_shape))  # ONNX/sklearn expects float32

    # decimals
    if t.startswith("decimal"):  # decimal(p,s)
        if decimals_as == "int64":
            # Use this only if you pre-scale to integers (e.g., cents) before inference.
            return Int64TensorType(list(per_feature_shape))
        return FloatTensorType(list(per_feature_shape))

    # dates/timestamps/others -> treat as string unless you convert upstream
    if t in {"date", "timestamp"}:
        return StringTensorType(list(per_feature_shape))

    # fallback
    return StringTensorType(list(per_feature_shape))


def build_initial_types_from_fields(
    fields: List[Dict[str, str]],
    *,
    force_float_numeric: bool = True,
    decimals_as: str = "float",        # "float" or "int64"
    sanitize_names: bool = True,       # ONNX input names should avoid spaces/punct
    per_feature_shape = (None, 1),
) -> Tuple[List[Tuple[str, object]], Dict[str, str], Dict[str, str]]:
    """
    Convert a simple list of Hive-like fields into skl2onnx initial_types.

    fields format:
        [{"name": "col1", "type": "string"},
         {"name": "col2", "type": "int"},
         {"name": "amount", "type": "decimal(18,2)"},
         {"name": "ratio", "type": "double"}, ...]

    Returns:
        initial_types: [(onnx_input_name, TensorType([None,1])), ...]
        name_map:      {original_name -> onnx_input_name}
        type_map:      {original_name -> normalized_hive_type}
    """
    initial_types: List[Tuple[str, object]] = []
    name_map: Dict[str, str] = {}
    type_map: Dict[str, str] = {}

    for f in fields:
        orig = str(f["name"])
        hive_t = str(f["type"]).strip().lower()

        # sanitize ONNX input names (no spaces/special chars)
        if sanitize_names:
            onnx_name = re.sub(r"\W+", "_", orig).strip("_")
            if not onnx_name:
                onnx_name = f"col_{abs(hash(orig)) % (10**8)}"
        else:
            onnx_name = orig

        tensor_type = hive_type_to_onnx_tensor(
            hive_t,
            force_float_numeric=force_float_numeric,
            decimals_as=decimals_as,
            per_feature_shape=per_feature_shape,
        )

        initial_types.append((onnx_name, tensor_type))
        name_map[orig] = onnx_name
        type_map[orig] = hive_t

    return initial_types, name_map, type_map
