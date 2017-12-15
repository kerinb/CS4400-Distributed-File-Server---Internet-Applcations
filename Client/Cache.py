import os
import datetime


def find_LRU_key(cache_entries):
    min_key = 0
    for i in range(1, len(cache_entries)):
        if cache_entries[i]['version'] < min:
            min_key = i
    return min_key


class Cache:
    client_id = None
    client_cache_dir = ""
    MAX_SIZE_OF_CACHE = 3  # Number of files in cache  - This is actually three files, because we go from 0 - 2!
    cache_entries = {}  # array of json tuples -> cache_entries[key] = [{'file': file, 'version': version}]

    def __init__(self, client_id):
        print "in init bruv..."
        # Initialise cache to size 10 with None populated
        self.client_id = client_id
        self.client_cache_dir = "Cache{}/".format(client_id)
        if not os.path.exists(self.client_cache_dir):
            os.mkdir(self.client_cache_dir)
        self.cache_entries = {}
        self.number_of_cache_entries = 0

    def initialise_cache(self, client_cache_path, client_id):
        try:
            print "initialising cache"
            if not os.path.exists(client_cache_path):
                print "path to client cache does not exists... creating it"
                os.mkdir(client_cache_path)
                self.client_id = client_id
                self.client_cache_dir = client_cache_path
            else:
                print "clients cache already exists"
        except Exception as e:
            print "ERROR: occurred when initialising the cache with:\n{}".format(e.message)

    def add_cache_entry(self, cache_file_name, version, updated_data):
            if cache_file_name not in self.cache_entries:
                print cache_file_name
                key = self.number_of_cache_entries
                if len(self.cache_entries) is self.MAX_SIZE_OF_CACHE:
                    print "cache is full - must use LRU function"
                    key = self.replace_file_LRU_policy()
                self.cache_entries[key] = {'file': cache_file_name, 'version': version}
                print self.cache_entries[key]
                if self.number_of_cache_entries is not 3:
                    self.number_of_cache_entries += 1
                print str(self.number_of_cache_entries)
                self.update_data_in_cache(cache_file_name, updated_data)
                print "File has been added to the cache!"

            # file is in cache
            print "Gonne get key for file"
            key = self.get_key_to_file(cache_file_name)
            print "key: " + str(key)
            if version > self.cache_entries[key]['version']:
                print "updating data in the cache"
                print "version is not up to date - need to up date cache"
                self.cache_entries[key] = {'file': cache_file_name, 'version': version}
                print "updated file in cache"
                return
            print "file is up to date - dont need to do anything..."

    def update_data_in_cache(self, cache_file_name, updated_data):
        try:
            open_file = open(cache_file_name, 'w+')
            open_file.write(updated_data)
            open_file.close()
            self.set_version_of_file(cache_file_name)
        except Exception as e:
            print "ERROR: occurred when updating data in the cache\n{}".format(e.message)

    def replace_file_LRU_policy(self):
        try:
            print "getting key to replace a file via LRU"
            # find the last accessed value - i think this may be max not min!
            key = find_LRU_key(self.cache_entries)
            dic = self.cache_entries[key]
            name = dic['file']
            dic.pop('version', 0)
            dic.pop('file', 0)
            file_to_delete_from_cache = 'Cache{}/{}'.format(self.client_id, name)
            os.remove(file_to_delete_from_cache)
            return key
        except Exception as e:
            print "ERROR: occurred when replacing a file in the cache\n{}".format(e.message)

    def empty_out_the_cache(self):
        try:
            print "emptying out the cache"
            self.cache_entries = {}
        except Exception as e:
            print "ERROR occurred when clearing the cache\n{}".format(e.message)

    def get_cache_entry(self, cache_file_name):
        try:
            print "getting entry from cache"
            key = self.get_key_to_file(cache_file_name)
            if key is not None:
                return self.data_from_cache(key)
            else:
                return None
        except Exception as e:
            print "ERROR: occurred when getting an entry from the cache\n{}".format(e.message)

    def get_key_to_file(self, cache_file_name):
        try:
            print "getting key to the requested file..."
            leng = self.number_of_cache_entries
            for i in range(leng):
                if self.cache_entries[i]['file'] == cache_file_name:
                    # the new version is this time now!
                    return i
        except Exception as e:
            print "ERROR: file requested not in cache.\n{}".format(e.message)

    def get_version_of_file(self, cache_file_name):
            for i in range(self.number_of_cache_entries):
                if self.cache_entries[i]['file'] == cache_file_name:
                    print self.cache_entries[i]['version']
                    return self.cache_entries[i]['version']
            return 0

    def data_from_cache(self, key):
        try:
            f = open(self.cache_entries[key]['file'], 'r')
            data = f.read()
            return {'file': self.cache_entries[key]['file'], 'version': self.cache_entries[key]['version'],
                    'data': data}
        except Exception as e:
            print "ERROR: error occurred when retreiving data from cache\n{}".format(e.message)

    def set_version_of_file(self, cache_file_name):
        try:
            print "setting version of files"
            print "Size of cache: " + str(self.number_of_cache_entries)
            print str(self.cache_entries)
            for i in range(self.number_of_cache_entries):
                if self.cache_entries[i]['file'] == cache_file_name:
                    # the new version is this time now!
                    print self.cache_entries[i]['version']
                    self.cache_entries[i]['version'] = str(datetime.datetime.now())
                    print self.cache_entries[i]['version']
        except Exception as e:
            print "ERROR: occurred when setting version for file: {}\n{}".format(cache_file_name, e.message)


if __name__ == "__main__":
    pass
