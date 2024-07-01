import sys

# read in result file
rstfile = open("../data/Results/" + sys.argv[1] + '.rst', 'r')
# read in trace file
tracefile = open("../data/InputFiles/" + sys.argv[1][:len(sys.argv[1])-8] + '.swf', 'r')
rst = rstfile.readlines()
trace = tracefile.readlines()
log = []
o_d = []

# read in ID and on-demand property
for line in trace:
    if(line[0] != ";"):
        element = []
        element.append(int(line.split(' ')[0]))
        element.append(int(line.split(' ')[18]))
        o_d.append(element)

# read in result and combine with on-demand property
for line in rst:
    element = []
    # print("Line{}: {}".format(count, line.strip()))
    element.append(int(line.split(';')[0])) # ID
    element.append(int(line.split(';')[1])) # CPU
    element.append(float(line.split(';')[2])) # req time
    element.append(float(line.split(';')[3])) # run time
    element.append(float(line.split(';')[4])) # wait time
    element.append(float(line.split(';')[5])) # submit time
    element.append(float(line.split(';')[6])) # start time
    element.append(float(line.split(';')[7])) # finish time
    for o_d_item in o_d:
        if o_d_item[0] == int(line.split(';')[0]):
            element.append(o_d_item[1]) # on-demand property
            break
    log.append(element)

# calculate average wait time
sum = 0.0
for i in range(len(log)):
    sum +=log[i][4]

print("average wait time      : ", round(sum/len(log), 2))

# calculate rigid job average wait time
sum = 0.0
rigid_number = 0 
for i in range(len(log)):
    if log[i][8] == 0:
        rigid_number += 1
        sum +=log[i][4]
print("rigid average wait time: ", round(sum/rigid_number, 2))

# calculate on-demand job average wait time
sum = 0.0
o_d_number = 0 
for i in range(len(log)):
    if log[i][8] == -1:
        o_d_number += 1
        sum +=log[i][4]
print("o_d average wait time  : ", round(sum/o_d_number, 2))

# calculate bounded slowdown
b_slowdown = 0.0
for i in range (len(log)):
    b_slowdown += max(((log[i][3] + log[i][4]) / max(log[i][4], 10)), 1)
print("average BSLD           : ", round(b_slowdown/len(log), 2))

# calculate rigid job bounded slowdown
b_slowdown = 0.0
rigid_number = 0 
for i in range (len(log)):
    if log[i][8] == 0:
        rigid_number += 1 
        b_slowdown += max(((log[i][3] + log[i][4]) / max(log[i][4], 10)), 1)
print("rigid BSLD             : ", round(b_slowdown/rigid_number, 2))

# calculate on-demand job bounded slowdown
b_slowdown = 0.0
o_d_number = 0 
for i in range (len(log)):
    if log[i][8] == -1:
        o_d_number += 1 
        b_slowdown += max(((log[i][3] + log[i][4]) / max(log[i][4], 10)), 1)
print("o_d BSLD               : ", round(b_slowdown/o_d_number, 2))

# get finish time
print("all job finish time    : ", log[len(log) - 1][7])

# calculate on-demand job quick response rate
o_d_number = 0 
instant_response_number = 0 
quick_response_number = 0 
for i in range (len(log)):
    if log[i][8] == -1:
        # print(log[i][0])
        o_d_number += 1
        if log[i][4] == 0: # hyper parameter in schedule agent
            # print(log[i][0])
            instant_response_number += 1
        if log[i][4] <= 1800: # hyper parameter in schedule agent
            # print(log[i][0])
            quick_response_number += 1
print(o_d_number, quick_response_number, instant_response_number)