import requests


def create_url(file_server_ip, file_server_port_number):
    return "http://{0}:{1}".format(file_server_ip, file_server_port_number)


def find_file_location_if_exists(file_name):
    request_to_server = {'file_name': file_name}
    response = requests.get('http://127.0.0.1:5000', params=request_to_server)
    file_server_id = response.json()['file_server_id']
    file_id = response.json()['file_id']

    return file_server_id, file_id

