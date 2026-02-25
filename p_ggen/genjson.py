#see: https://stackoverflow.com/questions/6886283/how-i-can-i-lazily-read-multiple-json-values-from-a-file-stream-in-python/7795029#7795029
#json reads until the end of file. If more data is found it raises exception
#that "Extra data" was found. Then we use the data contained in the exception
#object to see where the json ends.
#If "Extra data" was found, then another error has happened, and the exception
#should be re-raised.

import re, json
_matcher = re.compile(r'Extra data: line \d+ column \d+ .*\(char (\d+).*\)')

def getjson(fr):
    "Get a json object from the current position of file, to the end of the json."
    start_pos = fr.tell()
    try:
        obj = json.load(fr)
        return obj            #json object was ok - No extra data - end of file.
    except ValueError as ee:
        e = ee    #save exception object to another variable, as ee is temporary

    if 'Extra data: line' not in e.args[0]: raise  #reraise exception if no "extra data" was found, ..
                                                   #..as this is another problem
    end_pos = int(_matcher.match(e.args[0]).groups()[0])    #Find json end position
    fr.seek(start_pos)     #Restore position
    json_str = fr.read(end_pos)
    obj = json.loads(json_str)
    return obj
