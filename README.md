# CS4400 - Distributed File Server #

### Breandan Kerin - B.A.I, Computer Engineering, Trinity College Dublin - 14310166 ###

This project was completed as part of my module, CS4400 - Internet Applications in Trinity College Dublin (TCD). 
The aim of this project was to implement a Distributed file server, as either an NFS or AFS style server. It also had
to have other features implemented, a minimum of four had to be chosen from the following list:

*    <b>Distributed Transparent File Access - Aither AFS or NFS </b>
*    Security Service
*    <b>Directory Service</b>
*    Replication
*    <b>Caching</b>
*    Transactions
*    <b>Lock Service</b>

<i> Points highlighted above were the features implemented in this project.</i>

### Languages, Dependancies etc ###
* Python 2.7. 
* Flask
* flask-restful 
* requests
* a good working knowledge of JSON is also advantageous


## Distributed Transparent File Access ##
This system was modelled after the NFS system. the system can support multiple clients and multiple servers.For this, a client was written up that made use of a client API, which had the 'brains' of the clients abstracted from the client.
A file server was also implemented as a RESTful server that could be written to and read from by a client. 

### Client and Client Library ###
The file being run here is the client.py. It acts as an interface to the clientApi.py file. Here, the client is able to make decisionsfor files stored locally and on a file server. Using the CLiantApi, the client is able to:
*	read from the file server, write to the file server, 
*	Create a file that is stored locally and is also pushed to the server containing the data <i>"First Time file is opened.... Edit me!"</i>.

### File Server ### 
The file servers are implemented as a flat-file style system, where the files are stored in the file server without any deeper directories used. The file server directories are named using the file servers 'file_server_id' appened to 'Server'; ie, 'Server0/' etc
The file servers directory is created when the file server starts up, and is perscribed a file_server_id by the directory server. 

All files stored on a file server follow a simple name & numerical naming system such as hi0.txt - TODO - I want to change this to go back to my original implementation of just numerical values.

The server accepts get() and post() requests from all clients that are connected and know the servers IP and port number. It can be reached at any available host address and port specified by the user, which are provided as sys.argv[0] and sys.argv[1].
For the client to communicate with the file server, it must first communicate with the directory server, which will be discussed below.

*    A client that wishes to read a remote copy of a file from a file server will need to send a get() request. The client must provide JSON parameters:
*        'file_id': file_id
*        'file_server_id': server_id
*    A client wishing to write to a remote copy of a file will send a post() request. The client must provide JSON parameters:
*        'file_id': file_id
*        'file_contents': file_contents

<b>NOTE: There is no versioning in that any files written to on the server is overwritten </b>
The file servers are hosted on ports 5001 +

### Directory Server ###
The directory server must be started of first, as the file server and locking server need to register themselves with it. the directory server is located at the default address: 'http://127.0.0.1:5000'.  The Directory Server acts as a management server 
for the entire distributed file system. The Directory server maintains a record of the mappings of the client names and file mappings. 

The directory server also performs the following:
* acts a registration system as mentinoed above for the file server and lock server
* performs a load balancing on the file servers by means of Round-Robin. The directory server will forward the file onto the least loaded file server

### Caching ###
Each client has its own cache implemented as a caching object. The cache is implemented using Least Recently Used policy, where each file is stored with a time-date stamp, and the file that was accessed least recently is evicted. 
Everytime a file is read from a file server, it is added to the cache, with its time date stamp. 


### What is this repository for? ###



### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact