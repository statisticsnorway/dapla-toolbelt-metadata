"""Tests for the DatasetParser class."""

import io

import pandas as pd
import pyarrow as pa
import pytest
from datadoc_model.all_optional.model import DataType
from datadoc_model.all_optional.model import LanguageStringType
from datadoc_model.all_optional.model import LanguageStringTypeItem
from datadoc_model.all_optional.model import Variable
from pyarrow import parquet as pq
from upath import UPath

from dapla_metadata.datasets.dataset_parser import KNOWN_ARRAY_TYPES
from dapla_metadata.datasets.dataset_parser import KNOWN_BOOLEAN_TYPES
from dapla_metadata.datasets.dataset_parser import KNOWN_DATETIME_TYPES
from dapla_metadata.datasets.dataset_parser import KNOWN_FLOAT_TYPES
from dapla_metadata.datasets.dataset_parser import KNOWN_INTEGER_TYPES
from dapla_metadata.datasets.dataset_parser import KNOWN_STRING_TYPES
from dapla_metadata.datasets.dataset_parser import DatasetParser
from dapla_metadata.datasets.dataset_parser import DatasetParserParquet
from tests.datasets.constants import TEST_PARQUET_FILEPATH
from tests.datasets.constants import TEST_PARQUET_GZIP_FILEPATH
from tests.datasets.constants import TEST_SAS7BDAT_FILEPATH


def test_use_abstract_class_directly():
    with pytest.raises(TypeError):
        DatasetParser().get_fields()  # ty:ignore[missing-argument]


@pytest.mark.parametrize(
    "local_parser",
    [
        DatasetParser.for_file(TEST_PARQUET_FILEPATH),
        DatasetParser.for_file(TEST_PARQUET_GZIP_FILEPATH),
    ],
)
def test_get_fields_parquet(local_parser: DatasetParserParquet):
    expected_fields = [
        Variable(short_name="pers_id", data_type=DataType.STRING),
        Variable(short_name="tidspunkt", data_type=DataType.DATETIME),
        Variable(short_name="sivilstand", data_type=DataType.STRING),
        Variable(short_name="alm_inntekt", data_type=DataType.INTEGER),
        Variable(short_name="sykepenger", data_type=DataType.INTEGER),
        Variable(short_name="ber_bruttoformue", data_type=DataType.INTEGER),
        Variable(short_name="fullf_utdanning", data_type=DataType.STRING),
        Variable(short_name="hoveddiagnose", data_type=DataType.STRING),
    ]

    assert local_parser.get_fields() == expected_fields


@pytest.mark.parametrize(
    "local_parser",
    [
        DatasetParser.for_file(TEST_PARQUET_FILEPATH),
        DatasetParser.for_file(TEST_PARQUET_GZIP_FILEPATH),
    ],
)
def test_get_concrete_data_types_parquet(local_parser: DatasetParserParquet):
    expected_fields = {
        "alm_inntekt": "int64",
        "ber_bruttoformue": "int64",
        "fullf_utdanning": "string",
        "hoveddiagnose": "string",
        "pers_id": "string",
        "sivilstand": "string",
        "sykepenger": "int64",
        "tidspunkt": "timestamp[us]",
    }

    assert local_parser.get_concrete_data_types() == expected_fields


def test_get_fields_sas7bdat():
    expected_fields = [
        Variable(
            short_name="tekst",
            name=LanguageStringType(
                [LanguageStringTypeItem(languageCode="nb", languageText="Tekst")],
            ),
            data_type=DataType.STRING,
        ),
        Variable(
            short_name="tall",
            name=LanguageStringType(
                [LanguageStringTypeItem(languageCode="nb", languageText="Tall")],
            ),
            data_type=DataType.FLOAT,
        ),
        Variable(
            short_name="dato",
            name=LanguageStringType(
                [LanguageStringTypeItem(languageCode="nb", languageText="Dato")],
            ),
            data_type=DataType.DATETIME,
        ),
    ]

    reader = DatasetParser.for_file(TEST_SAS7BDAT_FILEPATH)
    fields = reader.get_fields()

    assert fields == expected_fields


@pytest.mark.parametrize("file", ["my_dataset.csv", "my_dataset.xlsx", "my_dataset"])
def test_dataset_parser_unsupported_files(file: UPath):
    with pytest.raises(NotImplementedError):
        DatasetParser.for_file(UPath(file))


def test_transform_datatype_unknown_type():
    assert DatasetParser.transform_data_type("definitely not a known data type") is None


@pytest.mark.parametrize(
    ("expected", "concrete_type"),
    [
        *[(DataType.INTEGER, i) for i in KNOWN_INTEGER_TYPES],
        *[(DataType.FLOAT, i) for i in KNOWN_FLOAT_TYPES],
        *[(DataType.STRING, i) for i in KNOWN_STRING_TYPES],
        *[(DataType.DATETIME, i) for i in KNOWN_DATETIME_TYPES],
        *[(DataType.BOOLEAN, i) for i in KNOWN_BOOLEAN_TYPES],
    ],
)
def test_transform_datatype(expected: DataType, concrete_type: str):
    assert DatasetParser.transform_data_type(concrete_type) == expected


@pytest.mark.parametrize(
    ("expected", "element_types"),
    [
        (DataType.ARRAY_INTEGER_, KNOWN_INTEGER_TYPES),
        (DataType.ARRAY_FLOAT_, KNOWN_FLOAT_TYPES),
        (DataType.ARRAY_STRING_, KNOWN_STRING_TYPES),
        (DataType.ARRAY_DATETIME_, KNOWN_DATETIME_TYPES),
        (DataType.ARRAY_BOOLEAN_, KNOWN_BOOLEAN_TYPES),
    ],
)
@pytest.mark.parametrize("array_type", KNOWN_ARRAY_TYPES)
def test_transform_array_datatype(
    expected: DataType,
    element_types: tuple[str, ...],
    array_type: str,
):
    for element_type in element_types:
        assert (
            DatasetParser.transform_data_type(array_type.format(element_type))
            == expected
        )


def test_parse_array_type(tmp_path):
    df = pd.DataFrame({"col1": [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5]]})
    output_path = tmp_path / "test_parse_array_type.parquet"
    df.to_parquet(output_path, engine="pyarrow")
    fields = DatasetParser.for_file(output_path).get_fields()
    assert fields[0].short_name == "col1"
    assert fields[0].data_type == DataType.ARRAY_INTEGER_


def test_parse_parquet_array_types(tmp_path):
    array_columns = [
        ("strings", pa.list_(pa.string()), [["a", "b"], [None]]),
        ("integers", pa.list_(pa.int64()), [[1, 2], [None]]),
        (
            "datetimes",
            pa.list_(pa.timestamp("us")),
            [[pd.Timestamp("2026-01-01")], [None]],
        ),
        ("booleans", pa.list_(pa.bool_()), [[True, False], [None]]),
        ("floats", pa.list_(pa.float64()), [[1.5, 2.5], [None]]),
    ]
    schema = pa.schema(
        [pa.field(name, array_type) for name, array_type, _ in array_columns],
    )
    table = pa.Table.from_arrays(
        [pa.array(values, type=array_type) for _, array_type, values in array_columns],
        schema=schema,
    )
    output_path = tmp_path / "array_types.parquet"
    pq.write_table(table, output_path)

    parser = DatasetParser.for_file(output_path)

    assert parser.get_fields() == [
        Variable(short_name="strings", data_type=DataType.ARRAY_STRING_),
        Variable(short_name="integers", data_type=DataType.ARRAY_INTEGER_),
        Variable(short_name="datetimes", data_type=DataType.ARRAY_DATETIME_),
        Variable(short_name="booleans", data_type=DataType.ARRAY_BOOLEAN_),
        Variable(short_name="floats", data_type=DataType.ARRAY_FLOAT_),
    ]


@pytest.fixture
def parquet_with_index_column(tmp_path):
    """Create a parquet file with a column called __index_level_0__."""
    test_data = pd.read_csv(
        io.StringIO(
            """a	b
1	4
2	5
3	6
""",
        ),
        sep="\t",
    )

    output_path = tmp_path / "test_with_index.parquet"
    test_data.query("b % 2 == 0").to_parquet(output_path, engine="pyarrow")
    return output_path


def test_parquet_with_index_column(parquet_with_index_column: UPath):
    fields = DatasetParser.for_file(parquet_with_index_column).get_fields()
    assert not any(f.short_name == "__index_level_0__" for f in fields)
