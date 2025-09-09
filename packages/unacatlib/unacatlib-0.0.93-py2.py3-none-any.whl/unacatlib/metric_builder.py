
from .layer import Layer
from .dimension import Dimension
from .metric import Metric
from syncer import sync

from unacatlib.unacast.operator.v1 import CreateLayerRequest, CreateMetricRequest
from unacatlib.unacast.maps.v1 import LayerSpec, Layer as v1_Layer, AddressComponent as v1_AddressComponent, ComponentKind
from unacatlib.unacast.metric.v1 import Metric as v1_Metric, Cadence, MetricSpec, DimensionSpec, ValueSpec, VersionSpec, DimensionCompleteness, GroupMemberSpec
from unacatlib.unacast.unatype import AvailabilityKind

class MetricBuilder(object):

    def __init__(self, catalog: 'Catalog', given_id: str):
        self._catalog = catalog
        self._metric_operator_service = catalog._client.metric_operator_service

        self._given_id = given_id
        self._display_name = ""
        self._description = ""
        self._layer = None
        self._related_layer = None
        self._value: ValueSpec = None
        self._version_spec: VersionSpec = None
        self._supporting_values = []
        self._cadence = Cadence.CADENCE_UNSPECIFIED
        self._processing_cadence = Cadence.CADENCE_UNSPECIFIED
        self._dimensions = []
        self._availability = AvailabilityKind.DELIVERY_ONLY
        self._rolling_observation_window = False
        self._group_memberships: GroupMemberSpec = []

    def with_display_name(self, display_name: str):
      self._display_name = display_name
      return self

    def with_description(self, description: str):
      self._description = description
      return self

    def with_cadence(self, cadence: Cadence):
      self._cadence = cadence
      return self

    def with_processing_cadence(self, cadence: Cadence):
        self._processing_cadence = cadence
        return self

    def with_availability(self, availability: AvailabilityKind):
      self._availability = availability
      return self

    def with_layer(self, layer: Layer):
      self._layer = layer
      return self

    def with_related_layer(self, layer: Layer):
      self._related_layer = layer
      return self

    def with_value(self, value: ValueSpec):
      value.supporting_value = False
      self._value = value
      return self

    def with_version_spec(self, version_spec: VersionSpec):
      self._version_spec = version_spec
      return self

    def with_supporting_value(self, value: ValueSpec):
      value.supporting_value = True
      self._supporting_values.append(value)
      return self

    def with_dimension(self, dimension: Dimension, default_value: str = "", dimension_completeness: DimensionCompleteness = DimensionCompleteness.STRICT ):
      self._dimensions.append(DimensionSpec(
        dimension_id=dimension.id,
        default_value=default_value,
        dimension_completeness= dimension_completeness,
      ))
      return self

    def with_rolling_observation_window(self, rolling_observation_window: bool):
      self._rolling_observation_window=rolling_observation_window
      return self

    def with_group_membership(self, key: str, value: str):
        self._group_memberships.append(GroupMemberSpec(
            key=key,
            value=value
        ))
        return self

    def create(self) -> Metric:
      values = self._supporting_values
      values.append(self._value)

      res: v1_Metric = sync(
            self._metric_operator_service.create_metric(CreateMetricRequest(
              catalog_id=self._catalog.id,
              given_id=self._given_id,
              name=self._display_name,
              description=self._description,
              version_spec=self._version_spec,
              availability=self._availability,
              spec=MetricSpec(
                layer_id=self._layer.id,
                related_layer_id=self._related_layer.id if self._related_layer else None,
                dimensions=self._dimensions,
                values=values,
                cadence=self._cadence,
                rolling_observation_window=self._rolling_observation_window,
                processing_cadence=self._processing_cadence,
                group_memberships=self._group_memberships
              )
            ))
      )
      return Metric(self._catalog, res)

