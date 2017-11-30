import requests


def create_url(file_server_ip, file_server_port_number, end_point=''):
    return "http://{0}:{1}/{2}".format(file_server_ip, file_server_port_number, end_point)


def find_file_location_if_exists(file_name):
    print "finding location of {}".format(file_name)
    request_to_server = {'file_name': str(file_name)}
    response = requests.get('http://127.0.0.1:5000', params=request_to_server)
    file_server_details = response.json()['file_server_details']
    file_id = file_name + str(response.json()['file_id'])
    file_server_id = response.json()['file_server_id']
    print response.json()

    return file_server_details, file_id, file_server_id


def cast_file_id_to_file_name(file_id):
    return str(file_id) + '.txt'
