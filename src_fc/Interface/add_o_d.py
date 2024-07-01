import sys


def main():
    args = sys.argv
    fin = open("../data/InputFiles/" + args[1], 'r')
    fout = open("../data/InputFiles/" + args[1][:-4] + "_" + args[2] + ".swf", 'w')
    lines = fin.readlines()
    fin.close()
    ls = ""
    o_d = ""
    header = ""

    for line in lines:
        # print(line)
        if line[0] == ';':
            header += line
        else:
            new_line = ' '.join(line.split()) + " 0" + '\n'
            # new_line = ' '.join([str(cnt)] + new_line.split(' ')[1:]) + '\n'
            ls += new_line
            # ls += line

    for submit in range(566129 + 3600, 63582293, 3600):
        # 64node
        # o_d += ("1 " + str(submit - 1800) + " 85075 42 64 0.25 -1 64 1200 -1 5 34 7 13712 3 -1 -1 -1" + " 1" + "\n")
        # o_d += ("1 " + str(submit) +        " 85075 42 64 0.25 -1 64 1200 -1 5 34 7 13712 3 -1 -1 -1" + " -1" + "\n")
        # 32node
        # o_d += ("1 " + str(submit - 1800) + " 85075 42 32 0.25 -1 32 1200 -1 5 34 7 13712 3 -1 -1 -1" + " 1" + "\n")
        # o_d += ("1 " + str(submit) +        " 85075 42 32 0.25 -1 32 1200 -1 5 34 7 13712 3 -1 -1 -1" + " -1" + "\n")
        # 16node
        o_d += ("1 " + str(submit - 1800) + " 85075 42 16 0.25 -1 16 1200 -1 5 34 7 13712 3 -1 -1 -1" + " 1" + "\n")
        o_d += ("1 " + str(submit) +        " 85075 42 16 0.25 -1 16 1200 -1 5 34 7 13712 3 -1 -1 -1" + " -1" + "\n")

    # print(o_d)    

    ls += o_d
    ls = sorted(ls.splitlines(), key=lambda line: int(line.split()[1]))
    # print(ls)

    for line in ls:
        new_line = ' '.join(line.split()) + '\n'
        header += new_line
    
    fout.write(header)
    fout.close()

if __name__ == "__main__":
    main()
