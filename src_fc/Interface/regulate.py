import sys


def main():
    args = sys.argv
    fileName = args[1]
    #newFileName = "".join(fileName.split(".")[:-1]) + "_regulate.swf"
    fin = open("../data/InputFiles/" + args[1], 'r')
    fout = open("../data/InputFiles/" + args[2], 'w')
    lines = fin.readlines()
    fin.close()
    ls = ""
    cnt = 0
    for line in lines:
        if line[0] == ';':
            ls += line
        else:
            new_line = ' '.join(line.split())
            new_line = ' '.join([str(cnt)] + new_line.split(' ')[1:]) + '\n'
            ls += new_line
            cnt += 1
    fout.write(ls)
    fout.close()

if __name__ == "__main__":
    main()
