from dataclasses import dataclass
import datetime
from enum import IntEnum
import time
from typing import Optional, TypedDict
from unacatlib.byo_external.report_job import ReportJob
from syncer import sync
import geojson

from grpclib.client import Channel
from unacatlib.unacast.v2.byo_external import ExternalByoServiceStub, ReadMetricFromReportRequest, CreateReportRequest, MetricReference, MetricValuesOnPois, ReportDetails, ReportStatus, \
PointOfInterest, MultiPolygon, Polygon, PolygonRing, Coordinate, Date
from unacatlib.query.proto_wrappers import PaginatedReadUSReportResponse


SERVER_ADDRESS = 'external-byo-poi-server-snr3asztcq-uk.a.run.app'
PORT = 443


class POIConverter(object):
    def to_pois(self, data_source: str) -> PointOfInterest:
        raise NotImplementedError("Subclasss should override this method")


class GeoJsonToPOIConverter(POIConverter):
	def to_pois(self, data_source: str) -> list[PointOfInterest]:
		"""
		Converts a geojson string into a list of PointOfInterest

		:param data_source: The geojson string
		:return: A list of PointOfInterest
		"""
		if not data_source:
			raise ValueError("no geo json for pois provided")

		try:
			pois = []
			features = geojson.loads(data_source)['features']
			for feature in features:
				feature_id = self.read_feature_id(feature)

				if not feature.get('geometry'):
					raise ValueError(f"a valid feature geometry is required, current feature {feature}")

				if not feature.geometry.type == 'Polygon':
					raise ValueError(f"expected geometry type of polygon got {feature.geometry.type}, current feature {feature}")

				polygonRing = PolygonRing(
					coordinates=list(
						map(
							lambda cord: Coordinate(lon=str(cord[0]), lat=str(cord[1])), feature.geometry.coordinates[0])
						)
					)
				point_of_interest = PointOfInterest(
					name=feature_id,
					polygon=MultiPolygon(
						polygons=[Polygon(rings=polygonRing)]
					)
				)
				pois.append(point_of_interest)
			return pois
		except KeyError as e:
			raise ValueError(f"`features` missing, in the provided poi geojson: {data_source}")

	def read_feature_id(self, feature: dict) -> str:
		"""Read the id from a geojson feature"""
		properties = feature.get('properties', None) or {}
		id = feature.get('id', None) or properties.get('id') or properties.get('name')
		if not id:
			raise ValueError(f'a valid id or name property is required, current feature {feature}')
		return id


class BYOApiClient(object):
	def __init__(self, billing_account, server_address=SERVER_ADDRESS, port=PORT, token="", additional_metadata: Optional[dict] = None):
		"""
		Create a client for the External BYO service.

		- **billing_account**: Billing account id (string like "cf95b8…").
		- **server_address**: Hostname of the BYO service. Defaults to the public endpoint.
		- **port**: Port for the service. If `server_address` ends with `run.app`, TLS is enabled and port forced to 443.
		- **token**: Bearer token used for authentication, e.g. `uc_…`.
		- **additional_metadata**: Extra gRPC metadata to include on all requests.
		"""
		if additional_metadata is None:
			additional_metadata = {}

		metadata = {**additional_metadata, "authorization": "Bearer " + token}

		ssl = False
		if server_address.endswith("run.app"):
			ssl = True
			port = 443

		self.channel = Channel(host=server_address, port=port, ssl=ssl)
		self.external_byo_service = ExternalByoServiceStub(
			self.channel, metadata=metadata)
		self.billing_account = billing_account
		self.poi_converter: POIConverter = GeoJsonToPOIConverter()

	def with_poi_converter(self, poi_converter: POIConverter):
		""" Associate a POI converter with the builder. This converter will be used to convert the POIs to the correct format. """

		self.poi_converter = poi_converter
		return self

	def read_us_report(self, report_id: str, metric_id: str, page_size: int = 10000) -> PaginatedReadUSReportResponse:
		"""
		Read a report's metric values in the US.

		- **report_id**: The id of the created report to read from.
		- **metric_id**: The metric to read (e.g., "traffic_trends_week").
		- **page_size**: Page size for each backend request. Larger sizes reduce roundtrips.

		Returns a `PaginatedReadUSReportResponse` with:
		- `values`: all metric values across pages
		- `schema`: metric version schema used for the values
		- `report_status`, `metric_status`, `metric_status_reason`: status information
		"""

		all_values = []
		page_token = ""
		first_response = None
		
		while True:
			response = sync(
				self.external_byo_service.read_metric_from_report(
					ReadMetricFromReportRequest(
						billing_account=self.billing_account,
						report_id=report_id,
						metric_reference=MetricReference(metric_id=metric_id),
						page_size=page_size,
						page_token=page_token,
					)
				)
			)
				
			# Store first response to use its structure later
			if first_response is None:
				first_response = response
				
			# Accumulate values from this page
			if response.values:
				all_values.extend(response.values)
				
			# Check if there are more pages
			if not response.next_page_token:
				break
				
			page_token = response.next_page_token
			
		return PaginatedReadUSReportResponse(
			values=all_values,
			schema=first_response.schema,
			report_status=first_response.report_status,
			metric_status=first_response.metric_status,
			metric_status_reason=first_response.metric_status_reason,
			first_response=first_response
		)

	def create_us_report(
		self,
		pois: str,
		metric_ids: str,
		start_date: datetime.date,
		end_date: datetime.date
	) -> ReportJob:
		"""
		Create a US report for the provided POIs and metrics.

		- **pois**: Input POIs in a format accepted by the configured `POIConverter`.
		  The default expects a GeoJSON string with Polygon features.
		- **metric_ids**: An iterable of metric ids to produce in the report.
		- **start_date**: Start date (inclusive) of the observation period.
		- **end_date**: End date (inclusive) of the observation period.

		Returns a `ReportJob` you can poll via `wait_for_completion()` or `refresh()`.
		"""
		if not self.poi_converter:
			raise NotImplementedError("no poi converter has been registered")

		r = sync(
			self.external_byo_service.create_report(
				CreateReportRequest(
					billing_account=self.billing_account,
					country_code="US",
					metric_reference=list(
						map(lambda metric_id: MetricReference(metric_id=metric_id), metric_ids)
					),
					pois=self.poi_converter.to_pois(pois),		# Verify the type of the returned pois.
					start_date=start_date and Date(
						year=start_date.year, month=start_date.month, day=start_date.day),
					end_date=end_date and Date(
						year=end_date.year, month=end_date.month, day=end_date.day)
				)
			)
		)
		return ReportJob(client=self, report_details=r)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.channel.close()

