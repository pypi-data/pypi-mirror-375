import base64
import json
from typing_extensions import deprecated
import requests

from openapi_client import Configuration, AllocationApi, DownHoleEquipmentApi, ESPApi, GasLiftValveApi, \
    MicroStringApi, NetworkApi, NetworkCompressorApi, NetworkCompressorConstraintApi, NetworkWellApi, NetworkWellConstraintApi, NetworkPipeApi, \
    TimeseriesConfigurationApi, SuckerRodPumpApi, NetworkSourceForecastApi, NetworkSourceApi, \
    NetworkScrewCompressorCurveApi, NetworkPipeConstraintApi, NetworkJointConstraintApi, TimeseriesHistoryApi, \
    WellEventApi, WellTestApi
from openapi_client.api.daily_production_api import DailyProductionApi
from openapi_client.api.well_api import WellApi
from openapi_client.api.wellbore_api import WellboreApi
from openapi_client.api.formation_api import FormationApi
from openapi_client.api.deviation_survey_api import DeviationSurveyApi
from openapi_client.api.tubing_api import *
from openapi_client.api.casing_api import CasingApi


class XectaApi:
    """
    This is a simple wrapper around the openapi generated client that adds some extra functionality for mtls auth
    as well as generating access tokens.
    """
    _configuration: Configuration = None

    def __init__(self, base_url: str, client_cert_file: str, client_key_file: str):
        """
        This will bootstrap the initial configuration before allowing the client to authenticate. Upon successful
        authentication a XectaApiClient instance will be returned
        :param base_url: The base url without any extra path parameters. example "https://testawsapi.onxecta.com"
        :param client_cert_file: The full path to the client certificate file for mtls.
        :param client_key_file: the full path to the client certificate key for mtls.
        """
        self._configuration = Configuration(host=base_url)
        # ISO 8601 format for python
        self._configuration.datetime_format = '%Y-%m-%dT%H:%M:%SZ'

        # Must initialize the configuration token to None initially or the client initialization will fail
        # with an error about missing access_token property.
        self._configuration.access_token = None

        # Initialize your mtls certificate and key that were provided by Xecta onboarding.
        # Note this should be the absolute path to your client certificate and key.
        self._configuration.cert_file = client_cert_file
        self._configuration.key_file = client_key_file


    class XectaApiClient:
        """
        This is an implementation of the api client that executes api functions. An instance of
        this class is returned from the xecta api authenticate function however this can be initialized
        manually if you already have a valid bearer token.
        """

        def __init__(self, configuration, bearer_token: str):
            self._configuration = configuration
            self.bearer_token = bearer_token
            self._configuration.access_token = bearer_token
            self.__api_client = ApiClient(self._configuration, header_name="Accept", header_value="application/json")
            # self.__api_client.default_headers['Accept'] = "application/json"

        def allocation_api(self) -> AllocationApi:
            return AllocationApi(self.__api_client)

        def casing_api(self) -> CasingApi:
            return CasingApi(self.__api_client)

        def daily_production_api(self) -> DailyProductionApi:
            return DailyProductionApi(self.__api_client)

        def deviation_survey_api(self) -> DeviationSurveyApi:
            return DeviationSurveyApi(self.__api_client)

        def down_hole_equipment_api(self) -> DownHoleEquipmentApi:
            return DownHoleEquipmentApi(self.__api_client)

        def esp_api(self) -> ESPApi:
            return ESPApi(self.__api_client)

        def formation_api(self) -> FormationApi:
            return FormationApi(self.__api_client)

        def gas_lift_valve_api(self) -> GasLiftValveApi:
            return GasLiftValveApi(self.__api_client)

        def micro_string_api(self) -> MicroStringApi:
            return MicroStringApi(self.__api_client)

        def network_api(self) -> NetworkApi:
            return NetworkApi(self.__api_client)

        def network_compressor_api(self) -> NetworkCompressorApi:
            return NetworkCompressorApi(self.__api_client)

        def network_compressor_constraint_api(self) -> NetworkCompressorConstraintApi:
            return NetworkCompressorConstraintApi(self.__api_client)

        def network_constraint_well_api(self) -> NetworkWellConstraintApi:
            return NetworkWellConstraintApi(self.__api_client)

        def network_joint_constraint_api(self) -> NetworkJointConstraintApi:
            return NetworkJointConstraintApi(self.__api_client)

        def network_pipe_api(self) -> NetworkPipeApi:
            return NetworkPipeApi(self.__api_client)

        def network_pipe_constraint_controller_api(self) -> NetworkPipeConstraintApi:
            return NetworkPipeConstraintApi(self.__api_client)

        def network_screw_compressor_curve_api(self) -> NetworkScrewCompressorCurveApi:
            return NetworkScrewCompressorCurveApi(self.__api_client)

        def network_source_api(self) -> NetworkSourceApi:
            return NetworkSourceApi(self.__api_client)

        def network_source_forecast_api(self) -> NetworkSourceForecastApi:
            return NetworkSourceForecastApi(self.__api_client)

        def network_well_api(self) -> NetworkWellApi:
            return NetworkWellApi(self.__api_client)

        def sucker_rod_pump_api(self) -> SuckerRodPumpApi:
            return SuckerRodPumpApi(self.__api_client)

        def time_series_configuration_api(self) -> TimeseriesConfigurationApi:
            return TimeseriesConfigurationApi(self.__api_client)

        def time_series_history_api(self) -> TimeseriesHistoryApi:
            return TimeseriesHistoryApi(self.__api_client)

        def tubing_api(self) -> TubingApi:
            return TubingApi(self.__api_client)

        def well_api(self) -> WellApi:
            return WellApi(self.__api_client)

        def well_events_api(self) -> WellEventApi:
            return WellEventApi(self.__api_client)

        def well_test_api(self) -> WellTestApi:
            return WellTestApi(self.__api_client)

        def wellbore_api(self) -> WellboreApi:
            return WellboreApi(self.__api_client)

        @deprecated("should use well_api")
        def well_header_api(self) -> WellApi:
            return WellApi(self.__api_client)

        @deprecated("should use formation_api")
        def wellbore_formation_api(self) -> FormationApi:
            return FormationApi(self.__api_client)

        @deprecated("should use tubing_api")
        def wellbore_tubing_api(self) -> TubingApi:
            return TubingApi(self.__api_client)

        @deprecated("should use casing_api")
        def wellbore_casing_api(self) -> CasingApi:
            return CasingApi(self.__api_client)

    def authenticate(self, api_key: str, api_secret: str, auth_url: str = "https://prod.authenticate.onxecta.com/oauth2/token") -> XectaApiClient:
        """
        This function will handle the authentication and upon successful authentication return a xecta api client
        implementation.

        Authentication URLS
        Production Environment: https://prod.authenticate.onxecta.com/oauth2/token
        Non Production Environment: https://nonprod.authenticate.onxecta.com/oauth2/token

        :param auth_url: The authentication url that was distributed by xecta during onboarding.
        :param api_key: The api key that was distributed by xecta during onboarding.
        :param api_secret: The api secret that was distributed by xecta during onboarding.
        :return: XectaApiClient implementation upon successful authentication.
        """
        encoded = f"{api_key}:{api_secret}".encode("utf-8")
        basic_auth = base64.b64encode(encoded).decode("utf-8")
        query_params = {"grant_type": "client_credentials"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_auth}"
        }

        client_response = requests.post(url=auth_url, headers=headers, params=query_params)
        response_data = client_response.json()
        return XectaApi.XectaApiClient(self._configuration, response_data['access_token'])
