import csv
import os


def read(add):
    fields = []
    rows = []
    filename = add + "csv"
    with open(filename, 'r') as csvFile:
        reader = csv.reader(csvFile)
        fields = next(reader)
        for row in reader:
            rows.append(row)

    return rows


def write(add, rows):
    fields = ["Host", "IP 1", "IP 2"]
    filename = add + "ans.csv"
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as csvFile:
        writer = csv.writer(csvFile,  lineterminator='\n',)
        writer.writerow(fields)
        for i in rows:
            writer.writerow(i)
