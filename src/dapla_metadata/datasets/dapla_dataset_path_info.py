"""Extract info from a path following SSB's dataset naming convention."""

from __future__ import annotations

import logging
import pathlib
import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Final
from typing import Literal

import arrow
from cloudpathlib import GSPath
from datadoc_model.all_optional.model import DataSetState

if TYPE_CHECKING:
    import datetime
    import os
    from datetime import date

logger = logging.getLogger(__name__)

GS_PREFIX_FROM_PATHLIB = "gs:/"


@dataclass
class DateFormat(ABC):
    """A super class for date formats."""

    name: str
    regex_pattern: str
    arrow_pattern: str
    timeframe: Literal["year", "month", "day", "week"]

    @abstractmethod
    def get_floor(self, period_string: str) -> date | None:
        """Abstract method implemented in the child class.

        Return the first date of the timeframe period.

        Args:
            period_string: A string representing the timeframe period.
        """

    @abstractmethod
    def get_ceil(self, period_string: str) -> date | None:
        """Abstract method implemented in the child class.

        Return the last date of the timeframe period.

        Args:
            period_string: A string representing the timeframe period.
        """


@dataclass
class IsoDateFormat(DateFormat):
    """A subclass of Dateformat with relevant patterns for ISO dates."""

    def get_floor(self, period_string: str) -> date | None:
        """Return first date of timeframe period defined in ISO date format.

        Examples:
            >>> ISO_YEAR_MONTH.get_floor("1980-08")
            datetime.date(1980, 8, 1)

            >>> ISO_YEAR.get_floor("2021")
            datetime.date(2021, 1, 1)
        """
        return arrow.get(period_string, self.arrow_pattern).floor(self.timeframe).date()

    def get_ceil(self, period_string: str) -> date | None:
        """Return last date of timeframe period defined in ISO date format.

        Examples:
            >>> ISO_YEAR.get_ceil("1921")
            datetime.date(1921, 12, 31)

            >>> ISO_YEAR_MONTH.get_ceil("2021-05")
            datetime.date(2021, 5, 31)
        """
        return arrow.get(period_string, self.arrow_pattern).ceil(self.timeframe).date()


ISO_YEAR = IsoDateFormat(
    name="ISO_YEAR",
    regex_pattern=r"^\d{4}$",
    arrow_pattern="YYYY",
    timeframe="year",
)
ISO_YEAR_MONTH = IsoDateFormat(
    name="ISO_YEAR_MONTH",
    regex_pattern=r"^\d{4}\-\d{2}$",
    arrow_pattern="YYYY-MM",
    timeframe="month",
)
ISO_YEAR_MONTH_DAY = IsoDateFormat(
    name="ISO_YEAR_MONTH_DAY",
    regex_pattern=r"^\d{4}\-\d{2}\-\d{2}$",
    arrow_pattern="YYYY-MM-DD",
    timeframe="day",
)
ISO_YEAR_WEEK = IsoDateFormat(
    name="ISO_YEAR_WEEK",
    regex_pattern=r"^\d{4}\-{0,1}W\d{2}$",
    arrow_pattern="W",
    timeframe="week",
)


@dataclass
class SsbDateFormat(DateFormat):
    """A subclass of Dateformat with relevant patterns for SSB unique dates.

    Attributes:
        ssb_dates: A dictionary where keys are date format strings and values
                    are corresponding date patterns specific to SSB.
    """

    ssb_dates: dict

    def get_floor(self, period_string: str) -> date | None:
        """Return first date of the timeframe period defined in SSB date format.

        Convert SSB format to date-string and return the first date.

        Args:
            period_string: A string representing the timeframe period in
                SSB format.

        Returns:
            The first date of the period if the period_string is a valid
            SSB format, otherwise None.

        Example:
            >>> SSB_BIMESTER.get_floor("2003B8")
            None

            >>> SSB_BIMESTER.get_floor("2003B4")
            datetime.date(2003, 7, 1)

            >>> SSB_BIMESTER.get_floor("2003-B4")
            datetime.date(2003, 7, 1)
        """
        try:
            year = period_string[:4]
            month = self.ssb_dates[period_string[-2:]]["start"]
            period = year + month
            return arrow.get(period, self.arrow_pattern).floor(self.timeframe).date()
        except KeyError:
            logger.exception("Error while converting to SSB date format")
            return None

    def get_ceil(self, period_string: str) -> date | None:
        """Return last date of the timeframe period defined in SSB date format.

        Convert SSB format to date-string and return the last date.

        Args:
            period_string: A string representing the timeframe period in SSB
                            format.

        Returns:
            The last date of the period if the period_string is a valid SSB format,
            otherwise None.

        Example:
            >>> SSB_TRIANNUAL.get_ceil("1999T11")
            None

            >>> SSB_HALF_YEAR.get_ceil("2024H1")
            datetime.date(2024, 6, 30)

            >>> SSB_HALF_YEAR.get_ceil("2024-H1")
            datetime.date(2024, 6, 30)
        """
        try:
            year = period_string[:4]
            month = self.ssb_dates[period_string[-2:]]["end"]
            period = year + month
            return arrow.get(period, self.arrow_pattern).ceil(self.timeframe).date()
        except KeyError:
            return None


SSB_BIMESTER = SsbDateFormat(
    name="SSB_BIMESTER",
    regex_pattern=r"^\d{4}-?[B]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "B1": {
            "start": "01",
            "end": "02",
        },
        "B2": {
            "start": "03",
            "end": "04",
        },
        "B3": {
            "start": "05",
            "end": "06",
        },
        "B4": {
            "start": "07",
            "end": "08",
        },
        "B5": {
            "start": "09",
            "end": "10",
        },
        "B6": {
            "start": "11",
            "end": "12",
        },
    },
)

SSB_QUARTERLY = SsbDateFormat(
    name="SSB_QUARTERLY",
    regex_pattern=r"^\d{4}-?[Q]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "Q1": {
            "start": "01",
            "end": "03",
        },
        "Q2": {
            "start": "04",
            "end": "06",
        },
        "Q3": {
            "start": "07",
            "end": "09",
        },
        "Q4": {
            "start": "10",
            "end": "12",
        },
    },
)

SSB_TRIANNUAL = SsbDateFormat(
    name="SSB_TRIANNUAL",
    regex_pattern=r"^\d{4}-?[T]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "T1": {
            "start": "01",
            "end": "04",
        },
        "T2": {
            "start": "05",
            "end": "08",
        },
        "T3": {
            "start": "09",
            "end": "12",
        },
    },
)
SSB_HALF_YEAR = SsbDateFormat(
    name="SSB_HALF_YEAR",
    regex_pattern=r"^\d{4}-?[H]\d{1}$",
    arrow_pattern="YYYYMM",
    timeframe="month",
    ssb_dates={
        "H1": {
            "start": "01",
            "end": "06",
        },
        "H2": {
            "start": "07",
            "end": "12",
        },
    },
)

SUPPORTED_DATE_FORMATS: list[IsoDateFormat | SsbDateFormat] = [
    ISO_YEAR,
    ISO_YEAR_MONTH,
    ISO_YEAR_MONTH_DAY,
    ISO_YEAR_WEEK,
    SSB_BIMESTER,
    SSB_QUARTERLY,
    SSB_TRIANNUAL,
    SSB_HALF_YEAR,
]


def categorize_period_string(period: str) -> IsoDateFormat | SsbDateFormat:
    """Categorize a period string into one of the supported date formats.

    Args:
        period: A string representing the period to be categorized.

    Returns:
        An instance of either IsoDateFormat or SsbDateFormat depending on the
        format of the input period string.

    Raises:
        NotImplementedError: If the period string is not recognized as either an
            ISO or SSB date format.

    Examples:
        >>> date_format = categorize_period_string('2022-W01')
        >>> date_format.name
        ISO_YEAR_WEEK

        >>> date_format = categorize_period_string('1954T2')
        >>> date_format.name
        SSB_TRIANNUAL

        >>> categorize_period_string('unknown format')
        Traceback (most recent call last):
        ...
        NotImplementedError: Period format unknown format is not supported
    """
    for date_format in SUPPORTED_DATE_FORMATS:
        if re.match(date_format.regex_pattern, period):
            return date_format

    msg = f"Period format {period} is not supported"
    raise NotImplementedError(
        msg,
    )


class DaplaDatasetPathInfo:
    """Extract info from a path following SSB's dataset naming convention."""

    def __init__(self, dataset_path: str | os.PathLike[str]) -> None:
        """Digest the path so that it's ready for further parsing."""
        self.dataset_string = str(dataset_path)
        self.dataset_path = pathlib.Path(dataset_path)
        self.dataset_name_sections = self.dataset_path.stem.split("_")
        self._period_strings = self._extract_period_strings(self.dataset_name_sections)

    @staticmethod
    def _get_period_string_indices(dataset_name_sections: list[str]) -> list[int]:
        """Get all the indices at which period strings are found in list.

        Args:
            dataset_name_sections: A list of strings representing sections of a
                dataset name.

        Returns:
            A list of indices where period strings are found within the
            dataset_name_sections.

        Examples:
            >>> DaplaDatasetPathInfo._get_period_string_indices(['kommune', 'p2022', 'v1'])
            [1]

            >>> DaplaDatasetPathInfo._get_period_string_indices(['kommune', 'p2022-01', 'p2023-06', 'v1'])
            [1, 2]

            >>> DaplaDatasetPathInfo._get_period_string_indices(['kommune', 'p1990Q1', 'v1'])
            [1]

            >>> DaplaDatasetPathInfo._get_period_string_indices(['varehandel','v1'])
            []
        """

        def insert_p(regex: str) -> str:
            r"""Insert a 'p' as the second character.

            Args:
                regex: A string representing the regular expression pattern to be
                    modified.

            Returns:
                The modified regular expression pattern with 'p' inserted as the
                second character.

            Examples:
                >>> insert_p(r"^\d{4}[H]\d{1}$")
                '^p\d{4}[H]\d{1}$'
            """
            return regex[:1] + "p" + regex[1:]

        return [
            i
            for i, x in enumerate(dataset_name_sections)
            if any(
                re.match(insert_p(date_format.regex_pattern), x)
                for date_format in SUPPORTED_DATE_FORMATS
            )
        ]

    @staticmethod
    def _extract_period_strings(dataset_name_sections: list[str]) -> list[str]:
        """Extract period strings from dataset name sections.

        Iterates over the dataset name sections and returns a list of strings
        that match the year regex, stripping the first character. This extracts
        the year periods from the dataset name.

        Args:
            dataset_name_sections: A list of strings representing sections of a
                dataset name.

        Returns:
            A list of extracted period strings, with the first character stripped
            from each match.

        Examples:
            >>> DaplaDatasetPathInfo._extract_period_strings(['p2022', 'kommune', 'v1'])
            ['2022']

            >>> DaplaDatasetPathInfo._extract_period_strings(['p2022-01', 'p2023-06', 'kommune', 'v1'])
            ['2022-01', '2023-06']

            >>> DaplaDatasetPathInfo._extract_period_strings(['p1990Q1', 'kommune', 'v1'])
            ['1990Q1']

            >>> DaplaDatasetPathInfo._extract_period_strings(['p1990-Q1', 'kommune', 'v1'])
            ['1990-Q1']

            >>> DaplaDatasetPathInfo._extract_period_strings(['varehandel','v1'])
            []
        """
        return [
            dataset_name_sections[i][1:]
            for i in DaplaDatasetPathInfo._get_period_string_indices(
                dataset_name_sections,
            )
        ]

    def _extract_period_string_from_index(self, index: int) -> str | None:
        """Extract a period string by its index from the list of period strings.

        Args:
            index: The index of the period string to extract.

        Returns:
            The extracted period string if it exists, otherwise None.
        """
        try:
            return self._period_strings[index]
        except IndexError:
            return None

    def _extract_norwegian_dataset_state_path_part(
        self,
        dataset_state: DataSetState,
    ) -> set:
        """Extract the Norwegian dataset state path part.

        Args:
            dataset_state: The dataset state.

        Returns:
            A set of variations of the Norwegian dataset state path part.
        """
        norwegian_mappings = {
            "SOURCE_DATA": "kildedata",
            "INPUT_DATA": "inndata",
            "PROCESSED_DATA": "klargjorte_data",
            "STATISTICS": "statistikk",
            "OUTPUT_DATA": "utdata",
        }
        norwegian_state = norwegian_mappings.get(dataset_state.name)
        if norwegian_state:
            state_name = norwegian_state.lower().replace("_", " ")
            return {state_name.replace(" ", "-"), state_name.replace(" ", "_")}
        return set()

    @property
    def bucket_name(
        self,
    ) -> str | None:
        """Extract the bucket name from the dataset path.

        Returns:
            The bucket name or None if the dataset path is not a GCS path nor ssb bucketeer path.

        Examples:
            >>> DaplaDatasetPathInfo('gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet').bucket_name
            ssb-staging-dapla-felles-data-delt

            >>> DaplaDatasetPathInfo(pathlib.Path('gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet')).bucket_name
            ssb-staging-dapla-felles-data-delt

            >>> DaplaDatasetPathInfo('gs:/ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet').bucket_name
            ssb-staging-dapla-felles-data-delt

            >>> DaplaDatasetPathInfo('ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet').bucket_name
            None

            >>> DaplaDatasetPathInfo('ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet').bucket_name
            None

            >>> DaplaDatasetPathInfo('buckets/ssb-staging-dapla-felles-data-delt/stat/utdata/person_data_p2021_v2.parquet').bucket_name
            ssb-staging-dapla-felles-data-delt

            >>> DaplaDatasetPathInfo('buckets/ssb-staging-dapla-felles-data-delt/person_data_p2021_v2.parquet').bucket_name
            ssb-staging-dapla-felles-data-delt

            >>> DaplaDatasetPathInfo('home/work/buckets/ssb-staging-dapla-felles-produkt/stat/utdata/person_data_p2021_v2.parquet').bucket_name
            ssb-staging-dapla-felles-produkt
        """
        prefix: str | None = None
        dataset_string = str(self.dataset_string)
        if GSPath.cloud_prefix in self.dataset_string:
            prefix = GSPath.cloud_prefix
            _, bucket_and_rest = dataset_string.split(prefix, 1)
        elif GS_PREFIX_FROM_PATHLIB in self.dataset_string:
            prefix = GS_PREFIX_FROM_PATHLIB
            _, bucket_and_rest = self.dataset_string.split(prefix, 1)
        elif "buckets/" in self.dataset_string:
            prefix = "buckets/"
            _, bucket_and_rest = self.dataset_string.split(prefix, 1)
        else:
            return None

        return pathlib.Path(
            bucket_and_rest,
        ).parts[0]

    @property
    def dataset_short_name(
        self,
    ) -> str | None:
        """Extract the dataset short name from the filepath.

        The dataset short name is defined as the first section of the stem, up to
        the period information or the version information if no period information
        is present.

        Returns:
            The extracted dataset short name if it can be determined, otherwise
            None.

        Examples:
            >>> DaplaDatasetPathInfo('prosjekt/befolkning/klargjorte_data/person_data_v1.parquet').dataset_short_name
            person_data

            >>> DaplaDatasetPathInfo('befolkning/inndata/sykepenger_p2022Q1_p2022Q2_v23.parquet').dataset_short_name
            sykepenger

            >>> DaplaDatasetPathInfo('my_data/simple_dataset_name.parquet').dataset_short_name
            simple_dataset_name

            >>> DaplaDatasetPathInfo('gs:/ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet').dataset_short_name
            person_data

            >>> DaplaDatasetPathInfo('buckets/ssb-staging-dapla-felles-data-delt/stat/utdata/folk_data_p2021_v2.parquet').dataset_short_name
            folk_data

            >>> DaplaDatasetPathInfo('buckets/ssb-staging-dapla-felles-data-delt/stat/utdata/dapla/bus_p2021_v2.parquet').dataset_short_name
            bus
        """
        if self.contains_data_from or self.contains_data_until:
            short_name_sections = self.dataset_name_sections[
                : min(
                    DaplaDatasetPathInfo._get_period_string_indices(
                        self.dataset_name_sections,
                    ),
                )
            ]
        elif self.dataset_version:
            short_name_sections = self.dataset_name_sections[:-1]
        else:
            short_name_sections = self.dataset_name_sections

        return "_".join(short_name_sections)

    @property
    def contains_data_from(self) -> datetime.date | None:
        """The earliest date from which data in the dataset is relevant for.

        Returns:
            The earliest relevant date for the dataset if available, otherwise None.
        """
        period_string = self._extract_period_string_from_index(0)
        if not period_string or (
            len(self._period_strings) > 1 and period_string > self._period_strings[1]
        ):
            return None
        date_format = categorize_period_string(period_string)
        return date_format.get_floor(period_string)

    @property
    def contains_data_until(self) -> datetime.date | None:
        """The latest date until which data in the dataset is relevant for.

        Returns:
            The latest relevant date for the dataset if available, otherwise None.
        """
        first_period_string = self._extract_period_string_from_index(0)
        second_period_string = self._extract_period_string_from_index(1)
        period_string = second_period_string or first_period_string
        if not period_string or (
            second_period_string
            and first_period_string is not None
            and second_period_string < first_period_string
        ):
            return None
        date_format = categorize_period_string(period_string)
        return date_format.get_ceil(period_string)

    @property
    def dataset_state(
        self,
    ) -> DataSetState | None:
        """Extract the dataset state from the path.

        We assume that files are saved in the Norwegian language as specified by
        SSB.

        Returns:
            The extracted dataset state if it can be determined from the path,
            otherwise None.

        Examples:
            >>> DaplaDatasetPathInfo('klargjorte_data/person_data_v1.parquet').dataset_state
            <DataSetState.PROCESSED_DATA: 'PROCESSED_DATA'>

            >>> DaplaDatasetPathInfo('klargjorte-data/person_data_v1.parquet').dataset_state
            <DataSetState.PROCESSED_DATA: 'PROCESSED_DATA'>

            >>> DaplaDatasetPathInfo('utdata/min_statistikk/person_data_v1.parquet').dataset_state
            <DataSetState.OUTPUT_DATA: 'OUTPUT_DATA'>

            >>> DaplaDatasetPathInfo('buckets/bucket_name/stat_name/inndata/min_statistikk/person_data_v1.parquet').dataset_state
            <DataSetState.INPUT_DATA: 'INPUT_DATA'>

            >>> DaplaDatasetPathInfo('my_special_data/person_data_v1.parquet').dataset_state
            None
        """
        dataset_path_parts = set(self.dataset_path.parts)
        for state in DataSetState:
            norwegian_variations = self._extract_norwegian_dataset_state_path_part(
                state,
            )
            if norwegian_variations.intersection(dataset_path_parts):
                return state
        return None

    @property
    def dataset_version(
        self,
    ) -> str | None:
        """Extract version information if exists in filename.

        Returns:
            The extracted version information if available in the filename,
            otherwise None.

        Examples:
            >>> DaplaDatasetPathInfo('person_data_v1.parquet').dataset_version
            '1'

            >>> DaplaDatasetPathInfo('person_data_v20.parquet').dataset_version
            '20'

            >>> DaplaDatasetPathInfo('person_data.parquet').dataset_version
            None

            >>> DaplaDatasetPathInfo('buckets/bucket_name/stat_name/inndata/min_statistikk/person_data_v1.parquet').dataset_version
            '1'

            >>> DaplaDatasetPathInfo('buckets/bucket_name/stat_name/inndata/min_statistikk/person_data.parquet').dataset_version
            None
        """
        minimum_elements_in_file_name: Final[int] = 2
        minimum_characters_in_version_string: Final[int] = 2
        if len(self.dataset_name_sections) >= minimum_elements_in_file_name:
            last_filename_element = str(self.dataset_name_sections[-1])
            if (
                len(last_filename_element) >= minimum_characters_in_version_string
                and last_filename_element[0:1] == "v"
                and last_filename_element[1:].isdigit()
            ):
                return last_filename_element[1:]
        return None

    def _get_left_parts(
        self,
        dataset_path_parts: list[str],
        state_index: int,
    ) -> list[str]:
        """Retrieve the path parts before the dataset state, considering bucket prefixes."""
        bucket_prefix = {"gs:", "buckets"}
        left_parts = dataset_path_parts[:state_index]

        # Stop checking beyond the bucket prefix
        prefix_intersection = bucket_prefix & set(left_parts)
        if prefix_intersection:
            first_prefix = min(
                left_parts.index(prefix) for prefix in prefix_intersection
            )
            left_parts = left_parts[first_prefix:]

        return (
            []
            if left_parts == ["/"]
            or (left_parts[0] in bucket_prefix and len(left_parts) <= 2)
            else left_parts
        )

    @property
    def statistic_short_name(
        self,
    ) -> str | None:
        """Extract the statistical short name from the filepath.

        Extract the statistical short name from the filepath either after bucket name or right before the
        dataset state based on the Dapla filepath naming convention.

        Returns:
            The extracted statistical short name if it can be determined,
            otherwise None.

        Examples:
            >>> DaplaDatasetPathInfo('prosjekt/befolkning/klargjorte_data/person_data_v1.parquet').statistic_short_name
            befolkning

            >>> DaplaDatasetPathInfo('buckets/prosjekt/befolkning/person_data_v1.parquet').statistic_short_name
            befolkning

            >>> DaplaDatasetPathInfo('befolkning/inndata/person_data_v1.parquet').statistic_short_name
            befolkning

            >>> DaplaDatasetPathInfo('buckets/bucket_name/stat_name/inndata/min_statistikk/person_data.parquet').statistic_short_name
            stat_name

            >>> DaplaDatasetPathInfo('buckets/stat_name/utdata/person_data.parquet').statistic_short_name
            None

            >>> DaplaDatasetPathInfo('befolkning/person_data.parquet').statistic_short_name
            None

            >>> DaplaDatasetPathInfo('buckets/produkt/befolkning/utdata/person_data.parquet').statistic_short_name
            befolkning

            >>> DaplaDatasetPathInfo('resources/buckets/produkt/befolkning/utdata/person_data.parquet').statistic_short_name
            befolkning

            >>> DaplaDatasetPathInfo('gs://statistikk/produkt/klargjorte-data/persondata_p1990-Q1_p2023-Q4_v1/aar=2019/data.parquet').statistic_short_name
            produkt

            >>> DaplaDatasetPathInfo('gs://statistikk/produkt/persondata_p1990-Q1_p2023-Q4_v1/aar=2019/data.parquet').statistic_short_name
            None

            >>> DaplaDatasetPathInfo('buckets/ssb-staging-dapla-felles-data-delt/person_data_p2021_v2.parquet').statistic_short_name
            None
        """
        if not self.dataset_state:
            if self.bucket_name:
                parts = self.dataset_path.parent.parts

                if self.bucket_name not in parts:
                    return None

                # Find the index of bucket_name in the path
                bucket_name_index = self.dataset_path.parent.parts.index(
                    self.bucket_name,
                )

                # If there are parts after bucket_name, return the part immediately after it
                if len(self.dataset_path.parent.parts) > bucket_name_index + 1:
                    return self.dataset_path.parent.parts[bucket_name_index + 1]

            return None

        dataset_state_names = self._extract_norwegian_dataset_state_path_part(
            self.dataset_state,
        )
        dataset_path_parts = list(self.dataset_path.parts)

        for state in dataset_state_names:
            if state not in dataset_path_parts:
                continue

            index = dataset_path_parts.index(state)

            if index == 0:
                continue

            left_parts = self._get_left_parts(dataset_path_parts, index)

            if not left_parts:
                return None

            return dataset_path_parts[index - 1]

        return None

    def path_complies_with_naming_standard(self) -> bool:
        """Check if path is valid according to SSB standard.

        Read more about SSB naming convention in the Dapla manual:
        https://manual.dapla.ssb.no/statistikkere/navnestandard.html

        Returns:
            True if the path conforms to the SSB naming standard, otherwise False.
        """
        return bool(
            self.dataset_state
            and self.statistic_short_name
            and self.contains_data_from
            and self.contains_data_until
            and self.dataset_version,
        )
