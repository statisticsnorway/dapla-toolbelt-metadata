import pyarrow as pa
from datadoc_model.all_optional import model as optional
from datadoc_model.required import model as required
from pyarrow import parquet
from upath.core import UPath

from dapla_metadata.datasets.core import Datadoc
from dapla_metadata.datasets.utility.utils import build_dataset_path


def get_arrow_data_type(
    datadoc_data_type: optional.DataType | required.DataType,
) -> pa.DataType:
    arrow_data_types: dict[optional.DataType, pa.DataType] = {
        optional.DataType.ARRAY_STRING_: pa.list_(pa.string()),
        optional.DataType.ARRAY_INTEGER_: pa.list_(pa.int32()),
        optional.DataType.ARRAY_DATETIME_: pa.list_(pa.date32()),
        optional.DataType.ARRAY_BOOLEAN_: pa.list_(pa.bool8()),
        optional.DataType.ARRAY_FLOAT_: pa.list_(pa.float32()),
        optional.DataType.BOOLEAN: pa.bool8(),
        optional.DataType.DATETIME: pa.date32(),
        optional.DataType.FLOAT: pa.float32(),
        optional.DataType.INTEGER: pa.int32(),
        optional.DataType.STRING: pa.string(),
    }

    try:
        return arrow_data_types[optional.DataType(datadoc_data_type)]
    except KeyError as error:
        raise TypeError("Not supported") from error  # noqa: EM101, TRY003


def create_dataset_for_metadata_document(
    metadata_document: UPath, output_dataset_path: UPath | None = None
) -> UPath:
    """Create a parquet file with the structure described by the metadata document.

    Useful for happy path testing.
    """
    meta = Datadoc(metadata_document_path=metadata_document)
    fields: list[tuple[str, pa.DataType]] = []
    for variable in meta.variables:
        if variable.short_name is None:
            error_message = "None short name encountered"
            raise ValueError(error_message)
        if variable.data_type is None:
            error_message = f"None data type encountered for {variable.short_name}"
            raise ValueError(error_message)
        fields.append(
            (
                variable.short_name,
                get_arrow_data_type(variable.data_type),
            )
        )
    schema = pa.schema(fields)
    if output_dataset_path is None:
        output_dataset_path = build_dataset_path(metadata_document)
    parquet.write_table(table=schema.empty_table(), where=str(output_dataset_path))
    return output_dataset_path
