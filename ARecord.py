import binascii
import socket
from copy import copy, deepcopy
import CSV


def sendMessage(message, address, port):
    message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    sock.connect(server_address)
    try:
        sock.send(bytes.fromhex(message))
        data, _ = sock.recvfrom(4096)
        return binascii.hexlify(data).decode("utf-8")
    except socket.timeout as e:
        sock.close()
    finally:
        sock.close()


def buildMessage(address, havingRecursion):
    ID = 43690  # 16-bit identifier (0-65535)
    QR = 0  # 1bit
    OPCODE = 0  # 4bit
    AA = 0  # 1bit
    TC = 0  # 1bit
    RD = 1  # 1bit
    if not havingRecursion:
        RD = 0  # 1bit
    RA = 0  # 1bit
    Z = 0  # 3bit
    RCode = 0  # 4bit

    query_params = str(QR)
    query_params += str(OPCODE).zfill(4)
    query_params += str(AA) + str(TC) + str(RD) + str(RA)
    query_params += str(Z).zfill(3)
    query_params += str(RCode).zfill(4)
    query_params = "{:04x}".format(int(query_params, 2))
    QDCOUNT = 1  # 16bit
    ANCOUNT = 0  # 16bit
    NSCOUNT = 0  # 16bit
    ARCOUNT = 0  # 16bit

    message = ""
    message += "{:04x}".format(ID)
    message += query_params
    message += "{:04x}".format(int(str(QDCOUNT), 2))
    message += "{:04x}".format(int(str(ANCOUNT), 2))
    message += "{:04x}".format(int(str(NSCOUNT), 2))
    message += "{:04x}".format(int(str(ARCOUNT), 2))

    addr_parts = address.split(".")
    for part in addr_parts:
        addr_len = "{:02x}".format(len(part))
        addr_part = binascii.hexlify(part.encode())
        message += addr_len
        message += addr_part.decode()

    message += "00"
    QTYPE = "{:04x}".format(1)
    message += QTYPE
    QCLASS = 1
    message += "{:04x}".format(QCLASS)
    return message


def decodeMessage(message):
    res = []
    ANCOUNT = message[12:16]
    NSCOUNT = message[16:20]
    ARCOUNT = message[20:24]
    question_parts = parseParts(message, 24, [])
    QTYPE_STARTS = 24 + (len("".join(question_parts))) + (len(question_parts) * 2) + 2
    QCLASS_STARTS = QTYPE_STARTS + 4
    ANSWER_SECTION_STARTS = QCLASS_STARTS + 4

    answer = []
    ns = []
    ar = []
    now = int(0)
    NUM_ANSWERS = int(ANCOUNT, 16) + int(NSCOUNT, 16) + int(ARCOUNT, 16)
    if NUM_ANSWERS > 0:
        for ANSWER_COUNT in range(NUM_ANSWERS):
            if ANSWER_COUNT == int(ANCOUNT, 16):
                now = int(1)
            if ANSWER_COUNT == int(ANCOUNT, 16) + int(NSCOUNT, 16):
                now = int(2)
            if ANSWER_SECTION_STARTS < len(message):
                ATYPE = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]
                RDLENGTH = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                RDDATA = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)]
                IPString = ""
                if ATYPE == "0001":
                    for i in range(RDLENGTH):
                        thisPartStart = 2 * i
                        temp = RDDATA[thisPartStart:thisPartStart + 2]
                        if IPString == "":
                            IPString = IPString + (str(int(temp, 16)))
                        else:
                            IPString = IPString + "." + (str(int(temp, 16)))
                    if now == 0:
                        answer.append(copy(IPString))
                    if now == 1:
                        ns.append(copy(IPString))
                    if now == 2:
                        ar.append(copy(IPString))
                ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)
    res.append(answer)
    res.append(ns)
    res.append(ar)
    return res


def parseParts(message, start, parts):
    part_start = start + 2
    part_len = message[start:part_start]

    if len(part_len) == 0:
        return parts

    part_end = part_start + (int(part_len, 16) * 2)
    parts.append(message[part_start:part_end])

    if message[part_end:part_end + 2] == "00" or part_end > len(message):
        return parts
    else:
        return parseParts(message, part_end, parts)


def main():
    while True:
        fileQuestion = input("Do you want to read from file? [y/n] ")
        if fileQuestion == "n" or fileQuestion == "y":
            break

    # read from file
    if fileQuestion == "y":
        fileName = input("Enter your File name: ")
        hosts = CSV.readHostNames(fileName)
        while True:
            IPQuestion = input("Do you want to use 8.8.8.8 as DNS server? [y/n] ")
            if IPQuestion == "n" or IPQuestion == "y":
                break
        IP = "8.8.8.8"
        if IPQuestion == 'n':
            IP = input("Enter your preferred IP for DNS server: ")
        sendAndReceiveForFile(hosts, IP, fileName)

    # read from input
    if fileQuestion == "n":
        url = input("Enter URL: ")
        check = CSV.checkInCache(url)
        if check is not None:
            print("Answer: ")
            for i in check:
                print(i)
            exit(0)
        while True:
            IPQuestion = input("Do you want to use 8.8.8.8 as DNS server? [y/n] ")
            if IPQuestion == "n" or IPQuestion == "y":
                break
        IP = "8.8.8.8"
        if IPQuestion == 'n':
            IP = input("Enter your preferred IP for DNS server: ")

        while True:
            recursion = input("Do you want to have recursion? [y/n] ")
            if recursion == "n" or recursion == "y":
                break
        havingRecursion = True
        if recursion == "n":
            havingRecursion = False
        sendAndReceiveForInput(url, IP, havingRecursion)

    updateCache()


def updateCache():
    count = deepcopy(CSV.readCountFile())
    for t in count:
        if t[2] == '3' and t[0] == '0':
            t[0] = '1'
            tempList = []
            for i in range(len(t)):
                if i != 0 and i != 2:
                    tempList.append(deepcopy(t[i]))
            CSV.addToCache(deepcopy(tempList))
    CSV.writeCountFile(count)


def sendAndReceiveForFile(hosts, IP, fileName):
    answers = []
    for i in hosts:
        ans1 = [i[0]]
        check = CSV.checkInCache(i[0])
        if check is not None:
            for j in check:
                ans1.append(deepcopy(j))
            answers.append(deepcopy(ans1))
            continue
        message = buildMessage(i[0], True)
        response = sendMessage(message, IP, 53)
        if response is None:
            print("Couldn't find i[0]")
            continue
        res = decodeMessage(response)
        listTemp = []
        if len(res[0]) != 0:
            for j in res[0]:
                ans1.append(deepcopy(j))
                listTemp.append(deepcopy(j))
        updateCountFile(i[0], deepcopy(listTemp))
        answers.append(deepcopy(ans1))
    CSV.writeIPs(fileName, answers)


fringe = []


def sendAndReceiveForInput(url, IP, havingRecursion):
    message = buildMessage(url, havingRecursion)
    response = sendMessage(message, IP, 53)
    res = None
    if response is not None:
        res = decodeMessage(response)

    if res is not None and len(res[0]) != 0:
        tempList = []
        print("Answer: ")
        for i in res[0]:
            print(i)
            tempList.append(deepcopy(i))
        updateCountFile(url, deepcopy(tempList))
        return

    else:
        if res is not None and len(res[2]) != 0:
            # print("AR: ")
            for i in res[2]:
                fringe.append(i)
        if len(fringe) == 0:
            print("please try again :(")
            exit(0)

        temp = fringe.pop(0)
        sendAndReceiveForInput(url, temp, havingRecursion)


def updateCountFile(url, answer):
    count = deepcopy(CSV.readCountFile())
    found = int(0)
    for t in count:
        if t[1] == url:
            t[2] = int(t[2]) + 1
            found = int(1)
            break
    if count is None:
        count = []
    if found == int(0):
        tempList = [0, url, 1]
        for i in answer:
            tempList.append(i)
        count.append(tempList)
    CSV.writeCountFile(count)


if __name__ == "__main__":
    main()
