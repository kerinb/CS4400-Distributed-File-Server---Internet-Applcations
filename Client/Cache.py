import os
import datetime

"""
I want the cache to store a file and its version, and i need to determine a key for it. 
how do I determine a key? 
"""


def find_LRU_key(cache_entries):
    min_key = 0
    for i in range(1, len(cache_entries)):
        if cache_entries[i]['version'] < min:
            min_key = i
    return min_key


class Cache:
    client_id = None
    client_cache_dir = ""
    MAX_SIZE_OF_CACHE = 3  # Number of files in cache
    cache_entries = []  # array of json tuples -> cache_entries[key] = [{'file': file, 'version': version}]

    def __init__(self, client_id):
        print "in init bruv..."
        # Initialise cache to size 10 with None populated
        self.client_id = client_id
        self.client_cache_dir = "Cache{}/".format(client_id)
        if not os.path.exists(self.client_cache_dir):
            os.mkdir(self.client_cache_dir)
        self.cache_entries = {}
        self.number_of_cache_entries = -1

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
                key = self.replace_file_LRU_policy()
            print "add file to cache here..."
            self.cache_entries[key] = {'file': cache_file_name, 'version': version}
            self.number_of_cache_entries += 1
            self.update_data_in_cache(cache_file_name, updated_data)

        # file is in cache
        key = self.get_key_to_file(cache_file_name)

        if version > self.cache_entries[key]['version']:
            print "updating data in the cache"
            print "version is not up to date - need to up date cache"
            self.cache_entries[key] = {'file': cache_file_name, 'version': version}
            print "updated file in cache"
            return
        print "file is up to date - dont need to do anything..."

    def update_data_in_cache(self, cache_file_name, updated_data):
        open_file = open(cache_file_name, 'w')
        open_file.write(updated_data)
        open_file.close()
        self.set_version_of_file(cache_file_name)

    def replace_file_LRU_policy(self):
        print "getting key to replace a file via LRU"
        # find the last accessed value - i think this may be max not min!
        key = find_LRU_key(self.cache_entries)
        dic = self.cache_entries[key]
        name = dic['file']
        dic.pop('version', 0)
        dic.pop('file', 0)
        file_to_delete_from_cache = 'Cache{}/{}.txt'.format(self.client_id, name)
        os.remove(file_to_delete_from_cache)
        return key

    def empty_out_the_cache(self):
        print "emptying out the cache"
        self.cache_entries = {}

    def get_cache_entry(self, cache_file_name):
        print "getting entry from cache"
        key = self.get_key_to_file(cache_file_name)
        if key is not None:
            return self.data_from_cache(key)
        else:
            return None

    def get_key_to_file(self, cache_file_name):
        if len(self.cache_entries) is 0:
            return -1
        for i in range(self.number_of_cache_entries):
            if self.cache_entries[i]['file'] is cache_file_name:
                return i
        return 0

    def get_version_of_file(self, cache_file_name):
        for i in range(self.number_of_cache_entries):
            if self.cache_entries[i]['file'] is cache_file_name:
                return self.cache_entries[i]['version'], self.cache_entries[i]['file'], cache_file_name
        return 0, 0, 0

    def data_from_cache(self, key):
        f = open(self.cache_entries[key]['file'], 'r')
        data = f.read()
        return {'file': self.cache_entries[key]['file'], 'version': self.cache_entries[key]['version'],
                'data': data}

    def set_version_of_file(self, cache_file_name):
        print str(self.cache_entries)
        for i in range(self.number_of_cache_entries):
            if self.cache_entries[i]['file'] is cache_file_name:
                # the new version is this time now!
                self.cache_entries[i]['version'] = str(datetime.datetime.now())


if __name__ == "__main__":
    pass
