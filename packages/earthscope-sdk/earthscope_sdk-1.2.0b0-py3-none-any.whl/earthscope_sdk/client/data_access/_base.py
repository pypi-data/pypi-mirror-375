import datetime as dt
from typing import TYPE_CHECKING, Union

from earthscope_sdk.client.data_access._arrow._common import load_table_with_extra
from earthscope_sdk.common.service import SdkService
from earthscope_sdk.util._time import to_utc_dt

if TYPE_CHECKING:
    from pyarrow import Table


class DataAccessBaseService(SdkService):
    """
    L1 data access service functionality
    """

    async def _get_gnss_observations(
        self,
        *,
        session_edid: str,
        start_datetime: dt.datetime,
        end_datetime: dt.datetime,
        system: Union[str, list[str]] = [],
        satellite: Union[str, list[str]] = [],
        obs_code: Union[str, list[str]] = [],
        field: Union[str, list[str]] = [],
    ) -> "Table":
        """
        Retrieve GNSS observations.

        This method retrieves GNSS observations for a given session.

        Args:
            session_edid: The session EDID to retrieve observations for.
            start_datetime: The start datetime to retrieve positions for.
            end_datetime: The end datetime to retrieve positions for.
            system: The system(s) to retrieve observations for.
            satellite: The satellite(s) to retrieve observations for.
            obs_code: The observation code(s) to retrieve observations for.
            field: The field(s) to retrieve observations for.

        Returns:
            A pyarrow table containing the GNSS observations.
        """

        # lazy import

        headers = {
            "accept": "application/vnd.apache.arrow.stream",
        }

        params = {
            "session_id": session_edid,
            "start_datetime": to_utc_dt(start_datetime).isoformat(),
            "end_datetime": to_utc_dt(end_datetime).isoformat(),
        }

        if system:
            params["system"] = system

        if satellite:
            params["satellite"] = satellite

        if obs_code:
            params["obs_code"] = obs_code

        if field:
            params["field"] = field

        req = self.ctx.httpx_client.build_request(
            method="GET",
            url=f"{self.resources.api_url}beta/data-products/gnss/observations",
            headers=headers,
            params=params,
            timeout=30,
        )

        resp = await self._send_with_retries(req)

        return await self.ctx.run_in_executor(
            load_table_with_extra,
            resp.content,
            # Add edid column to the table returned by the API
            edid=session_edid,
        )
