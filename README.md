# CS4400 - Distributed File Server #

### Breandan Kerin - B.A.I, Computer Engineering, Trinity College Dublin - 14310166 ###

This project was completed as part of my module, CS4400 - Internet Applications in Trinity College Dublin (TCD). 
The aim of this project was to implement a Distributed file server, as either an NFS; Network File System, or AFS; Andrew File System
style server. It also had to have other features implemented, a minimum of four had to be chosen from the following list:

*    Distributed Transparent File Access - Either AFS or NFS
*    Security Service
*    Directory Service
*    Replication
*    Caching
*    Transactions
*    Lock Service

The features I have implemented are:
1. Distributed Transparent File Access - FS
2. Directory Service
3. Caching
4. Lock Service

### Languages, Dependencies etc ###
* Python 2.7. 
* Flask
* flask-restful 
* requests
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

*    A client that wishes to read a remote copy of a file from a file server will need to send a get() request. The client must provide JSON parameters:
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



