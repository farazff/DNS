import csv
import os
from copy import deepcopy


def readHostNames(add):
    fields = []
    rows = []
    filename = add + ".csv"
    with open(filename, 'r') as csvFile:
        reader = csv.reader(csvFile)
        fields = next(reader)
        for row in reader:
            rows.append(row)

    return rows


def writeIPs(add, rows):
    fields = ["Host", "IP 1", "IP 2"]
    filename = add + "ans.csv"
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n', )
        writer.writerow(fields)
        for i in rows:
            writer.writerow(i)


def readCountFile():
    fields = []
    rows = []
    filename = "countFile.csv"
    with open(filename, 'r') as csvFile:
        reader = csv.reader(csvFile)
        fields = next(reader)
        for row in reader:
            rows.append(row)

    return rows


def writeCountFile(rows):
    fields = ["cached", "Host", "NUM", "IP1", "IP2", "IP3"]
    filename = "countFile.csv"
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n', )
        writer.writerow(fields)
        for i in rows:
            writer.writerow(i)


def addToCache(oneRow):
    fields = []
    rows = []
    filename = "cache.csv"
    with open(filename, 'r') as csvFile:
        reader = csv.reader(csvFile)
        fields = next(reader)
        for row in reader:
            rows.append(row)
    rows.append(deepcopy(oneRow))
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n', )
        writer.writerow(fields)
        for i in rows:
            writer.writerow(i)
