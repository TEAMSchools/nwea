import requests
import re
import csv
import io

BASE_URL = 'https://api.mapnwea.org'
HTTP_ERROR = requests.exceptions.HTTPError

class DataExport:
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

class Client:
    def __init__(self, username, password):
        self.base_url = BASE_URL
        self.username = username

        self.session = requests.Session()
        self.session.auth = (username, password)

    def send_request(self, method, path, files=None):
        request_url = f'{self.base_url}/{path}'
        try:
            response = self.session.request(method, request_url, files=files)
            response.raise_for_status()
            return response
        except HTTP_ERROR as e:
            print(e, '\n' + response.text)

    def data_export(self):
        path = 'services/reporting/dex'

        response = self.send_request('GET', path)

        if response.ok:
            print('Server response: ' + str(response.status_code) + ' | ' + response.reason)

            response_headers = response.headers['Content-Disposition']
            re_matches = re.findall('filename="(.+)"', response_headers)
            filename = re_matches[0]

            data_export = DataExport(filename=filename, data=response.content)
            return data_export

    def combined_update(self, file_path):
        path = 'services/rostering/submit/complete/update'
        file = {'file': open(file_path, 'rb')}

        response = self.send_request('POST', path, file)

        if response.ok:
            print('Server response: ' + str(response.status_code) + ' | ' + response.text)
            return response.status_code

    def additional_users(self, file_path):
        path = 'services/rostering/submit/others'
        file = {'file': open(file_path, 'rb')}

        response = self.send_request('POST', path, file)

        if response.ok:
            print('Server response: ' + str(response.status_code) + ' | ' + response.text)
            return response.status_code

    def import_status(self):
        path = 'services/rostering/status'

        response = self.send_request('GET', path)

        if response.ok:
            print('Server response: ' + str(response.status_code) + ' | ' + response.text)
            return response.text

    def import_errors(self):
        path = 'services/rostering/errors'

        response = self.send_request('GET', path)

        if response.ok:
            if response.text == 'OK_NO_ERRORS':
                print('Server response: ' + str(response.status_code) + ' | ' + response.text)
                return {}
            else:
                errors_dictreader = csv.DictReader(io.StringIO(response.text))
                errors_list = [e for e in map(dict, errors_dictreader)]
                return errors_list