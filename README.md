# CS4400 - Distributed File Server #

### Breandan Kerin - B.A.I Computer Engineering, Trinity College Dublin - 14310166 ###

This project was completed as part of my module, CS4400 - Internet Applications in Trinity College Dublin (_TCD_).
The source code can be viewed [Here](https://bitbucket.org/Breandan96/cs4400distributedfileserver)
The aim of this project is to implement a Distributed File Server, modelled as either an NFS; _Network File System_, or AFS; _Andrew File System_
style server. The system also has to have some other features implemented, a minimum of four had to be chosen from the following list:

*    *_Distributed Transparent File Access - Either AFS or NFS_*
*    Security Service
*    _Directory Service_
*    Replication
*    _Caching_
*    Transactions
*    _Lock Service_

The features implemented in this project are highlighted above as the italicised values, and the emboldened value is compulsory
for the project.

### Launching the System ###
This application can be run either on Windows or Linux; It has not yet been tested on Mac OS, Operating systems. In this project,
several shell scripts are provided. These scripts can be used to run the system through a Command Line Interface; _CLI_,such as terminal
on Linux. To run these scripts, the permissions need to be granted in order to execute the scripts. The permissions can be granted as follows:
_chmod 755 <script name>_. The list below is the list of required commands to give permissions:
* chmod 755 install_requirements.sh
* chmod 755 launch_directory_server.sh
* chmod 755 launch_file_server.sh
* chmod 755 launch_locking_server.sh
* chmod 755 launch_client.sh

To launch the system, first give the permissions as shown abpve, then in order to run the python scripts, a commands similiar
to the following is used, *./<script name>*
The list below shows the order in which to run each of the scripts.
* ./install_requirements.sh
    * This script must be run first. It will install all of the required dependencies in order for the service to run, installing
    all requirements from the *requirements.txt* file.
* ./launch_directory_server.sh
    * This script will run the directory server script. It is run on the URL "http://127.0.0.1:46666"
* ./launch_locking_server.sh
    * this script runs the locking server.This and the file server scripts can be run interchangeably. This script runs the locking
    server on the URL "http://127.0.0.1:46667".
* ./launch_file_server.sh <number_of_servers_to_spawn>
    * this script runs up a series of file serves. For this file, the number of file serves to spawn must be specified in the
    <number_of_servers_to_spawn>. Here, the first file server will be hosted on port "46668",  and every subsequent file server spawned
    will be hosted on the incremented value of the previous; ie 46668, 46669 etc etc.
    hence the URL for the servers will similar to "http://127.0.0.1:46668"
* ./launch_client.sh
    * This script will spawn up a single client. To spawn multiple clients, this script will need to be run multiple times. This is
    because each client will be required to input values for file names etc while in use, and would simply cause confusion if they were
    all run on the same window.

### Additional Notes on this project ###
* Originally, I had implemented this project using Sockets; instead of Flask and restful-flask, for my means of communications between
  each of my services I was running; ie between a client and a file server etc. It was only when I had implemented the file server and
  client and had nearly finished work on the directory server, did I come to terms and realise the error of my ways and I began implementing
  this with flask and flaskrest-ful. Changing to rest was a great idea, as it simplified my approach significantly and I no longer needed
  to worry about implementing sockets and handling them and threads between multiple services.
* The commit where I scraped the socket and threads approach can be found
[Here](https://bitbucket.org/Breandan96/cs4400distributedfileserver/commits/805aa84afbe567bdebfe1bca356f20b246f3eae5)

### Languages, Dependencies etc ###
The list of dependencies and requirements are highlighted below. This project uses the Python 2.7 project interpreter.
The list of requirements are contained within _requirements.txt_ file. This list are then downloaded and installed using the
_pip install --user -r requirements.txt_ command in the *install_requirements.sh* file.
* Flask
* flask-restful 
* requests
In order to work effectively with this project, a basic understanding of JSON would be beneficial due to the data being stored and
transferred between the classes are in JSON format, since it is the default data transfer method in Flask.
* a good working knowledge of JSON is also advantageous


## Distributed Transparent File Access ##
This system was modelled after the NFS system. the system can support multiple clients and multiple servers.For this, a
client was written up that made use of a client API, which had the 'brains' of the clients abstracted from the client.
A file server was also implemented as a RESTful server that could be written to and read from by a client. 

### Client and Client Library ###
The file being run here is the client.py. It acts as an interface to the clientApi.py file. Here, the client is able to
make decisions for files stored locally and on a file server. Using the CliantApi, the client is able to:
*	read from the file server, write to the file server, 
*	Create a file that is stored locally and is also pushed to the server containing the data "First Time file is
 opened.... Edit me!".

### File Server ### 
The file servers are implemented as a flat-file style system, where the files are stored in the file server without any
deeper directories used. The file server directories are named using the file servers 'file_server_id' appended to 'Server
'; ie, 'Server0/' etcThe file servers directory is created when the file server starts up, and is prescribed a
file_server_id by the directory server.

All files stored on a file server follow a simple name & numerical naming system such as 0.txt -

The server accepts get() and post() requests from all clients that are connected and know the servers IP and port
number. It can be reached at any available host address and port specified by the user, which are provided as sys.argv[0] and sys.argv[1].
For the client to communicate with the file server, it must first communicate with the directory server, which will be discussed below.

*    A client that wishes to read a remote copy of a file from a file server will need to send a get() request. The client must provide
JSON parameters:
*        'file_id': file_id
*        'file_server_id': file_server_id
*    A client wishing to write to a remote copy of a file will send a post() request. The client must provide JSON parameters:
*        'file_id': file_id
*        'data': data

NOTE: There is no versioning in that any files written to on the server is overwritten
The file servers are hosted on ports 5001, 5002 etc etc, which are passed in as environment variables at run time.

### Directory Server ###
The directory server must be started of first, as the file server and locking server need to register themselves with it.
the directory server is located at the default address: 'http://127.0.0.1:5000'.  The Directory Server acts as a management server
for the entire distributed file system. The Directory server maintains a record of the mappings of the client names and file mappings.
The Directory server takes in a request by a client, and checks whether the file the client has requested exists on the file server
If the file exists, the directory server returns the ip and port number of the file server to the client, where the client can
make communications with the file server. The same works for a write operation also, but if the file doesnt exist on a file server,
the round robin protocol is used to assign the file to a file server, that has the least files stored on it.

The directory server also performs the following:
* acts a registration system as mentinoed above for the file server and lock server
* performs a load balancing on the file servers by means of Round-Robin. The directory server will forward the file onto
the least loaded file server

### Caching ###
Each client has its own cache implemented as a caching object. The cache is implemented using Least Recently Used policy,
where each file is stored with a time-date stamp, and the file that was accessed least recently is evicted.
Everytime a file is read from a file server, it is added to the cache, with its time date stamp.
The cache can store currently 3 files simply for the point of illustration, to increase the number of files that the cache
can store, simply increase the size of MAX_SIZE_OF_CACHE.



