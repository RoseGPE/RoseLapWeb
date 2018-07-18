import config
import os

def makeLabel(d):
    data = list(d.values())
    label = []

    for i in range(len(data[0])):
        label.append(str([v[i] for v in data])[1:-1])

    return (str([k for k in list(d.keys())])[1:-1], label)

def generateTimeseries(times):
    return [time[1] for time in times]

def makeGraphFolder(foldername):
    dname = "C:\wamp\www\RoseLap\graph\\" + foldername
    try:
        os.makedirs(dname)
    except Exception:
        pass
    return dname

def getHead():
    styles = '<link rel="stylesheet" type="text/css" href="../../css/col-bootstrap.min.css">'
    with open(config.file_dir + "/display/head.php", "r") as head:
        with open(config.file_dir + "/display/nav.php", "r") as nav:
            return head.read() + styles + nav.read()

def writeHTML(H, filename):
    with open("C:\wamp\www\RoseLap\graph\\" + filename, "w") as chart:
        html_head = '''
        '''

        html_foot = '''
        '''

        html = H.htmlcontent
        chart.write(html_head)
        chart.write(html)
        chart.write(html_foot)