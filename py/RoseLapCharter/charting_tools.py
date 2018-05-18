import os

def makeLabel(d):
    data = list(d.values())
    label = []

    for i in range(len(data[0])):
        label.append(str([v[i] for v in data])[1:-1])

    return (str([k for k in list(d.keys())])[1:-1], label)

def makeGraphFolder(foldername):
	os.makedirs("../../graph/" + foldername)

def writeHTML(H, filename):
    with open("../../graph/" + filename, "w") as chart:
        chart.write(H.htmlcontent)