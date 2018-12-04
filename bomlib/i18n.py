
import os
import yaml    

def LangLoadStr(prefs):
    
    script_dir = os.path.dirname(__file__)
    lang_filename = os.path.join(script_dir, "../languages/"+prefs.language+".yaml")
    messsages = {}
    
    with open(lang_filename,"r") as lang_file:
        elements = yaml.load(lang_file)
        messages = {k: unicode(v).encode("utf-8") for k,v in elements["_MESSAGES"].iteritems()}
        columns = {k: unicode(v).encode("utf-8") for k,v in elements["_COLUMNS"].iteritems()}
        
    return (messages,columns)
