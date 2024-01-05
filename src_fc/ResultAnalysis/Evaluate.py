import sys

# read in result file
file = open("../data/Results/" + sys.argv[1] + '.rst', 'r')
rst = file.readlines()
log = []
count = 0
for line in rst:
    count += 1
    element = []
    # print("Line{}: {}".format(count, line.strip()))
    element.append(int(line.split(';')[0]))
    element.append(int(line.split(';')[1]))
    element.append(float(line.split(';')[2]))
    element.append(float(line.split(';')[3]))
    element.append(float(line.split(';')[4]))
    element.append(float(line.split(';')[5]))
    element.append(float(line.split(';')[6]))
    element.append(float(line.split(';')[7]))
    log.append(element)

# calculate average wait time
sum = 0.0
for i in range(len(log)):
    sum +=log[i][5]

print("average wait time   : ", sum/len(log))

# calculate bounded slowdown
b_slowdown = 0.0
for i in range (len(log)):
    b_slowdown += max(((log[i][5] + log[i][4]) / max(log[i][4], 10)), 1)

print("average slow down(b): ", b_slowdown/len(log))

# get finish time
print("all job finish time : ", log[len(log) - 1][7])