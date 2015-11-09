import os
import ConfigParser


class ConfigHandler(object):
    def __init__(self, filename):
        self._filename = filename
        self._parser = ConfigParser.SafeConfigParser()

        try:
            self._parser.read(self._filename)
        except IOError:
            print "Cannot read " + self._filename
    
    def get(self, section, key):
        return self._parser.get(section, key)
    
    def set(self, section, key, value):
        self._parser.set(section, key, value)
    
    def save(self):
        with open(self._filename, 'w+b') as out:
            self._parser.write(out)