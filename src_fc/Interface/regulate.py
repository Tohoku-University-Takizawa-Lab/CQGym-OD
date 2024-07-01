import sys


def main():
    args = sys.argv
    fileName = args[1]
    newFileName = "".join(fileName.split(".")[:-1]) + "_regulate.swf"
    fin = open("../data/InputFiles/" + args[1], 'r')
    fout = open("../data/InputFiles/" + newFileName, 'w')
    lines = fin.readlines()
    fin.close()
    ls = ""
    cnt = 1
    for line in lines:
        if line[0] == ';':
            ls += line
            continue
        elif (int(line.split()[0])<=0): # job id
            continue
        elif (int(line.split()[1])<0): # job submit
            continue
        elif (int(line.split()[3])<=0): # job run
            continue  
        elif (int(line.split()[8])<=0): # job reqTime
            continue
        elif (int(line.split()[7])<=0): # job reqProc
            continue
        else:
            new_line = ' '.join(line.split())
            new_line = ' '.join([str(cnt)] + new_line.split(' ')[1:]) + '\n'
            ls += new_line
            cnt += 1
    # print(ls)
    lss = ""
    ids = []
    cnt = 0
    lines = ls.splitlines()
    for line in lines: 
        if line[0] != ';' and line.split(" ")[18] == "-1": # for on demand task
            ids.append(line.split(" ")[0]) # save their id
    # print(ids)
    for line in lines:
        if line[0] == ';':
            lss += line + "\n"
        else:
            # print(line.split(" ")[18])
            if(line.split(" ")[18] == '1'): # for on demand task notice 
                new_line = ' '.join(line.split(' ')[:-1] + [str(int(ids[cnt]))] ) + '\n' # set their corresponding on demand id to o_d property.
                cnt += 1
            else:
                new_line = ' '.join(line.split()) + '\n'
            lss += new_line
    # print(lss)    

    fout.write(lss)
    fout.close()

if __name__ == "__main__":
    main()
