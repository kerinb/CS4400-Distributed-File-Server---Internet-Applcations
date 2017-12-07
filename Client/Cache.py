import os

import itertools

"""
I want the cache to store a file and its version, and i need to determine a key for it. 
how do I determine a key? 
"""


class Cache:
    client_id = 0
    client_cache_dir = ""
    MAX_SIZE_OF_CACHE = 10  # Number of files in cache
    cache_entries = []  # array of json tuples -> cache_entries[key] = [{'file': file, 'version': version}]
    number_of_cache_entries = 0

    def __init__(self, client_id):
        print "in init bruv..."
        # Initialise cache to size 10 with None populated
        self.client_id = client_id
        self.client_cache_dir = "Cache{}/".format(client_id)
        if not os.path.exists(self.client_cache_dir):
            os.mkdir(self.client_cache_dir)
        self.cache_entries = dict(itertools.izip(xrange(self.MAX_SIZE_OF_CACHE), itertools.repeat(None)))

    def initialise_cache(self, client_cache_path, client_id):
        print "initialising cache"
        if not os.path.exists(client_cache_path):
            print "path to client cache does not exists... creating it"
            os.mkdir(client_cache_path)
            self.client_id = client_id
            self.client_cache_dir = client_cache_path
        else:
            print "clients cache already exists"

    def add_cache_entry(self, cache_file_name, version, updated_data):
        print "adding data to cache"

        if cache_file_name not in self.cache_entries:
            print "file is not in cache -add it"
            key = self.number_of_cache_entries + 1
            if len(self.cache_entries) is self.MAX_SIZE_OF_CACHE:
                print "cache is full - must use LRU function"
                key = self.remove_file_LRU_policy()
            print "add file to cache here..."
            self.cache_entries[key] = {'file': cache_file_name, 'version': version}
            self.number_of_cache_entries += 1
            self.update_data_in_cache(cache_file_name, updated_data)
            return

        # file is in cache
        key = self.get_key_to_file(cache_file_name)

        if version > self.cache_entries[key].json['version']:
            print "updating data in the cache"
            print "version is not up to date - need to up date cache"
            self.cache_entries[key] = {'file': cache_file_name, 'version': version}
            print "updated file in cache"
            return
        print "file is up to date - dont need to do anything..."

    def update_data_in_cache(self, cache_file_name, updated_data):
        pass

    def remove_file_LRU_policy(self):
        print "removing a file via LRU"
        # find the last accessed value - i think this may be max not min!
        key = max(self.cache_entries.values())
        del self.cache_entries[key]
        self.number_of_cache_entries -= 1
        print "removed file from cache"
        return key

    def empty_out_the_cache(self):
        print "emptying out the cache"
        self.cache_entries = {}

    def get_cache_entry(self, cache_file_name):
        print "getting entry from cache"
        key = self.get_key_to_file(cache_file_name)
        return self.data_from_cache(key)

    def get_key_to_file(self, cache_file_name):
        for i in range(self.number_of_cache_entries):
            if self.cache_entries[i].json['file'] is cache_file_name:
                return i
        return None

    def get_version_of_file(self, cache_file_name):
        for i in range(self.number_of_cache_entries):
            if self.cache_entries[i].json['file'] is cache_file_name:
                return self.cache_entries[i].json['version']
        return None

    def data_from_cache(self, key):
        f = open(self.cache_entries[key].json('file'), 'r')
        data = f.read()
        return {'file': self.cache_entries[key].json('file'), 'version': self.cache_entries[key].json('version'),
                'data': data}


if __name__ == "__main__":
    pass
