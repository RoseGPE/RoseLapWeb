import os

def makeLabel(d):
    data = list(d.values())
    label = []

    for i in range(len(data[0])):
        label.append(str([v[i] for v in data])[1:-1])

    return (str([k for k in list(d.keys())])[1:-1], label)

def makeGraphFolder(foldername):
	os.makedirs("C:\wamp\www\RoseLap\graph\\" + foldername)

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