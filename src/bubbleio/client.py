from kbc.client_base import HttpClientBase

from bubbleio import exceptions


class Client(HttpClientBase):
    MAX_RETRIES = 10
    MAX_LIMIT = 100

    def __init__(self, base_url, api_token):
        HttpClientBase.__init__(self, base_url=base_url, max_retries=self.MAX_RETRIES, backoff_factor=0.3,
                                status_forcelist=(429, 503, 500, 502, 504))

        # set auth header
        self._auth_header = {"Authorization": 'Bearer ' + api_token,
                             "Content-Type": "application/json"}

    def get_paged_result_pages(self, endpoint, parameters, cursor=0):

        has_more = True
        next_url = self.base_url + endpoint
        paging_params = {"cursor": cursor,
                         "limit": self.MAX_LIMIT}
        query_params = {**parameters, **paging_params}
        while has_more:
            query_params['cursor'] = cursor
            resp = self.get_raw(next_url, params=query_params)
            req_response = self._parse_response(resp, endpoint)

            if req_response['response']['remaining'] != 0:
                has_more = True
                cursor += self.MAX_LIMIT
            else:
                has_more = False

            yield req_response['response']['results']

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
