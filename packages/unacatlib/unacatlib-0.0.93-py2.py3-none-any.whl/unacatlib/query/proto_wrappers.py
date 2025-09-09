from typing import List, Optional
from unacatlib.unacast.catalog.v3 import (
    DataReference as DataReferenceProto,
    GetDataReferenceResponse as GetDataReferenceResponseProto,
    ListDataReferencesResponse as ListDataReferencesResponseProto,
    ListRecordsResponse,
    FieldDefinition,
    Record,
    SearchFieldValuesResponse,
)
from unacatlib.unacast.catalog.v3alpha import (
    ListRecordsStatisticsResponse as ListRecordsStatisticsResponseProto,
)

from unacatlib.query.record_list_plugin import RecordList
from unacatlib.query.field_definition_list_plugin import FieldDefinitionList
from unacatlib.query.record_statistics_list_plugin import (
    RecordStatisticsList,
    wrap_statistics,
)
from unacatlib.query.data_reference_list_plugin import (
    DataReferenceList,
    wrap_data_references,
    wrap_data_reference_fields,
)
from unacatlib.query.values_list_plugin import wrap_values_list
from unacatlib.unacast.v2.byo_external import MetricValuesOnPois, ReportStatus, MetricStatus
from unacatlib.unacast.v2.metric import MetricVersion, MetricValue

class ListDataReferencesResponse(ListDataReferencesResponseProto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wrap_data_references(self)

    # Type hints for IDE support
    data_references: DataReferenceList


class DataReference(DataReferenceProto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wrap_data_reference_fields(self)

    # Type hints for IDE support
    fields: FieldDefinitionList


class GetDataReferenceResponse(GetDataReferenceResponseProto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wrap_data_reference_fields(self.data_reference)

    # Type hints for IDE support
    data_reference: DataReference


class ListRecordsStatisticsResponse(ListRecordsStatisticsResponseProto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wrap_statistics(self)

    # Type hints for IDE support
    statistics: RecordStatisticsList


class PaginatedListRecordsResponse:
    """
    A wrapper around ListRecordsResponse that only exposes the desired attributes
    and methods while hiding pagination details.
    """

    __slots__ = ("_response", "records", "field_definitions", "total_size")

    def __init__(
        self,
        records: List[Record],
        field_definitions: List[FieldDefinition],
        total_size: int,
    ):
        # Create the wrapped response
        self._response = ListRecordsResponse(
            records=records, field_definitions=field_definitions, next_page_token=""
        )
        # Wrap collections in their respective list types
        self.field_definitions = FieldDefinitionList(self._response.field_definitions)
        self.total_size = total_size
        self.records = RecordList(self._response.records, self.field_definitions)

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        d = self._response.to_dict()
        if "next_page_token" in d:
            del d["next_page_token"]
        return d

    def __dir__(self) -> List[str]:
        """Control which attributes are visible"""
        return ["records", "field_definitions", "to_dict", "total_size"]

    # Type hints for IDE support
    records: RecordList
    field_definitions: FieldDefinitionList


class PaginatedSearchFieldValuesResponse:
    """
    A wrapper around SearchFieldValuesResponse that only exposes the desired attributes
    and methods while hiding pagination details.
    """

    __slots__ = ("_response", "values", "field_definition", "total_size")

    def __init__(
        self,
        values: List[str],
        field_definition: FieldDefinition,
        total_size: int,
    ):
        self._response = SearchFieldValuesResponse(
            values=values, field_definition=field_definition, next_page_token=""
        )
        self.field_definition = FieldDefinitionList([field_definition])
        self.total_size = total_size
        self.values = wrap_values_list(values)

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        d = self._response.to_dict()
        if "next_page_token" in d:
            del d["next_page_token"]
        return d

    def __dir__(self) -> List[str]:
        """Control which attributes are visible"""
        return ["values", "field_definition", "to_dict", "total_size"]

    # Type hints for IDE support
    field_definition: FieldDefinitionList


class PaginatedReadUSReportResponse:
    """
    Aggregated result for reading a BYO report's metric values across all pages.

    - **values**: Flat list of all `MetricValue` items from every page.
    - **schema**: The `MetricVersion` describing the returned data columns.
    - **report_status**: Overall `ReportStatus` of the report job.
    - **metric_status**: Per-metric `MetricStatus` describing production status.
    - **metric_status_reason**: Human-readable reason when a metric is delayed/failed.

    Provides convenience methods for converting to a serializable dictionary while
    removing pagination-specific fields.
    """

    __slots__ = ("values", "schema", "report_status", "metric_status", "metric_status_reason", "_first_response")

    def __init__(
        self,
        values: List[MetricValue],
        schema: MetricVersion,
        report_status: ReportStatus,
        metric_status: MetricStatus,
        metric_status_reason: str,
        first_response: Optional[MetricValuesOnPois] = None,
    ):
        self.values = values
        self.schema = schema
        self.report_status = report_status
        # Store the first response to delegate method calls
        self._first_response = first_response
        self.metric_status = metric_status
        self.metric_status_reason = metric_status_reason

    # Attribute type hints for IDEs
    values: List[MetricValue]
    schema: MetricVersion
    report_status: ReportStatus
    metric_status: MetricStatus
    metric_status_reason: str

    def to_pydict(self) -> dict:
        """Convert to a dictionary, merging all pages and dropping pagination tokens."""
        # Create a synthetic response that looks like the original gRPC response
        # but with all the accumulated values
        if self._first_response:
            # Use the first response as a template and override the values
            result = self._first_response.to_dict()
            # Convert the accumulated values to dict format
            result['values'] = [value.to_dict() if hasattr(value, 'to_dict') else value for value in self.values]
            # Remove pagination token since this is the complete result
            if 'next_page_token' in result:
                del result['next_page_token']
            return result
        else:
            # Fallback if no first response is available
            return {
                'values': [value.to_dict() if hasattr(value, 'to_dict') else value for value in self.values],
                'schema': self.schema.to_dict() if hasattr(self.schema, 'to_dict') else self.schema,
                'report_status': self.report_status,
                'metric_status': self.metric_status,
                'metric_status_reason': self.metric_status_reason,
            }

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return self.to_pydict()
