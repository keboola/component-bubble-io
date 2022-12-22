import json
from datetime import timedelta
from dateutil import parser

from kbc.client_base import HttpClientBase

from . import exceptions


class Client(HttpClientBase):
    MAX_RETRIES = 10
    MAX_LIMIT = 100
    MODIFIED_DATE = "Modified Date"

    def __init__(self, base_url, api_token):
        HttpClientBase.__init__(self, base_url=base_url, max_retries=self.MAX_RETRIES, backoff_factor=0.3,
                                status_forcelist=(429, 503, 500, 502, 504))

        # set auth header
        self._auth_header = {"Authorization": 'Bearer ' + api_token,
                             "Content-Type": "application/json"}

    def get_paged_result_pages(self, endpoint, since_date, to_date, cursor=0):

        def calc_params():
            params = {
                "cursor": None,  # will be assigned prior to a request
                "limit": self.MAX_LIMIT,
                "sort_field": self.MODIFIED_DATE
            }
            const = []
            if since_date:
                const.append({"key": "Modified Date",
                              "constraint_type": "greater than",
                              "value": since_date.isoformat(timespec='milliseconds')
                              })
            if to_date:
                const.append({"key": "Modified Date",
                              "constraint_type": "less than",
                              "value": to_date.isoformat(timespec='milliseconds')
                              })
            if const:
                params["constraints"] = json.dumps(const)
            return params

        next_url = self.base_url + endpoint
        query_params = calc_params()

        while True:
            query_params['cursor'] = cursor
            resp = self.get_raw(next_url, params=query_params)
            req_response = self._parse_response(resp, endpoint)
            remaining = req_response['response']['remaining']
            results = req_response['response']['results']
            if results:
                yield results
            if not remaining:
                break
            if results:
                last_date = results[-1][self.MODIFIED_DATE]
            if len(results) < self.MAX_LIMIT:
                last = parser.parse(last_date)
                since_date = last - timedelta(milliseconds=1)
                cursor = 0
                query_params = calc_params()
            else:
                cursor += self.MAX_LIMIT

    def _parse_response(self, response, endpoint):
        status_code = response.status_code
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.text
        if status_code in (200, 201, 202):
            return r
        elif status_code == 204:
            return None
        elif status_code == 400:
            raise exceptions.BadRequest(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 401:
            raise exceptions.Unauthorized(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 403:
            raise exceptions.Forbidden(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 404:
            raise exceptions.NotFound(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 405:
            raise exceptions.MethodNotAllowed(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 406:
            raise exceptions.NotAcceptable(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 409:
            raise exceptions.Conflict(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 410:
            raise exceptions.Gone(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 411:
            raise exceptions.LengthRequired(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 412:
            raise exceptions.PreconditionFailed(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 413:
            raise exceptions.RequestEntityTooLarge(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 415:
            raise exceptions.UnsupportedMediaType(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 416:
            raise exceptions.RequestedRangeNotSatisfiable(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 422:
            raise exceptions.UnprocessableEntity(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 429:
            raise exceptions.TooManyRequests(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 500:
            raise exceptions.InternalServerError(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 501:
            raise exceptions.NotImplemented(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 503:
            raise exceptions.ServiceUnavailable(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 504:
            raise exceptions.GatewayTimeout(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 507:
            raise exceptions.InsufficientStorage(f'Calling endpoint {endpoint} failed', r)
        elif status_code == 509:
            raise exceptions.BandwidthLimitExceeded(f'Calling endpoint {endpoint} failed', r)
        else:
            raise exceptions.UnknownError(f'Calling endpoint {endpoint} failed', r)
