import os

def process_list():
    cmd = 'wmic process get description, processid'
    output = os.popen(cmd).read()
    
    processes = [[j for j in i.split('  ') if j!=''and j!=' '] for i in output.split('\n') if i != ''][1:]
    processes = [[i[0],eval(i[1])] for i in processes]
    return processes


def find_all(pname:str=None, pid:int=None):
    if pname:
        return [i for i in process_list() if i[0]==pname]
    elif pid:
        return [i for i in process_list() if i[1]==pid]


def find(pname:str=None, pid:int=None):
    results = find_all(pname, pid)
    if results != []:
        return results[0]

def refresh(pid):
    os.kill(pid, 9)

