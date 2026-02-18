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
    match optional.DataType(datadoc_data_type):
        case optional.DataType.ARRAY:
            raise TypeError("Not supported")  # noqa: EM101, TRY003
        case optional.DataType.BOOLEAN:
            return pa.bool8()
        case optional.DataType.DATETIME:
            return pa.date32()
        case optional.DataType.FLOAT:
            return pa.float32()
        case optional.DataType.INTEGER:
            return pa.int32()
        case optional.DataType.STRING:
            return pa.string()


def create_dataset_for_metadata_document(
    metadata_document: UPath, output_dataset_path: UPath | None = None
) -> UPath:
    """Create a parquet file with the structure described by the metadata document.

    Useful for happy path testing.
    """

    def raiser(exception: Exception):
        """Workaround to raise exception from ternary."""
        raise exception

    meta = Datadoc(metadata_document_path=metadata_document)
    schema = pa.schema(
        [
            (
                str(v.short_name),
                get_arrow_data_type(
                    v.data_type
                    or raiser(
                        ValueError(f"None data type encountered for {v.short_name}")
                    )
                ),
            )
            for v in meta.variables
        ]
    )
    if output_dataset_path is None:
        output_dataset_path = build_dataset_path(metadata_document)
    parquet.write_table(table=schema.empty_table(), where=str(output_dataset_path))
    return output_dataset_path
