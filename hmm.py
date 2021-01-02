# -*- coding: utf-8 -*-

import json
import sys
import re

# state_M = 4
# word_N = 0
A_dic = {}
B_dic = {}
Count_dic = {}
Pi_dic = {}
word_set = set()
state_list = ['B', 'I', 'E', 'S']
line_num = -1

INPUT_DATA = "trainCorpus.txt_utf8"
PROB_START = "HMM\prob_start.py"  # 初始状态概率
PROB_EMIT = "HMM\prob_emit.py"  # 发射概率
PROB_TRANS = "HMM\prob_trans.py"  # 转移概率


def init():  # 初始化字典
    for state in state_list:
        A_dic[state] = {}
        for state1 in state_list:
            A_dic[state][state1] = 0.0
    for state in state_list:
        Pi_dic[state] = 0.0
        B_dic[state] = {}
        Count_dic[state] = 0


def getList(input_str):  # 输入词语，输出状态
    outpout_str = []
    if len(input_str) == 1:
        outpout_str.append('S')
    elif len(input_str) == 2:
        outpout_str = ['B', 'E']
    else:
        M_num = len(input_str) - 2
        M_list = ['M'] * M_num
        outpout_str.append('B')
        outpout_str.extend(M_list)  # 把M_list中的'M'分别添加进去
        outpout_str.append('E')
    return outpout_str


def Output():  # 输出模型的三个参数：初始概率+转移概率+发射概率
    start_fp = open(PROB_START, 'w', encoding='UTF-8')
    emit_fp = open(PROB_EMIT, 'w', encoding='UTF-8')
    trans_fp = open(PROB_TRANS, 'w', encoding='UTF-8')
    print ("len(word_set) = %s " % (len(word_set)))

    for key in Pi_dic:  # 状态的初始概率
        Pi_dic[key] = Pi_dic[key] * 1.0 / line_num
    # print (start_fp, )
    Pi_jsObj = json.dumps(Pi_dic)
    start_fp.write(Pi_jsObj)

    for key in A_dic:  # 状态转移概率
        for key1 in A_dic[key]:
            A_dic[key][key1] = A_dic[key][key1] / Count_dic[key]
    # print (trans_fp, A_dic)
    A_jsObj = json.dumps(A_dic)
    trans_fp.write(A_jsObj)


    for key in B_dic:  # 发射概率(状态->词语的条件概率)
        for word in B_dic[key]:
            B_dic[key][word] = B_dic[key][word] / Count_dic[key]
    # print (emit_fp, B_dic)
    B_jsObj = json.dumps(B_dic)
    emit_fp.write(B_jsObj)

    start_fp.close()
    emit_fp.close()
    trans_fp.close()


def train():
    ifp = open(INPUT_DATA, encoding='UTF-8')
    init()
    global word_set  # 初始是set()
    global line_num  # 初始是-1
    for line in ifp:
        line_num += 1
        if line_num % 10000 == 0:
            print(line_num)
        line = line.strip()
        # print("line:", line)
        if not line: continue
        # line = line.decode("utf-8", "ignore")  # 设置为ignore，会忽略非法字符

        word_list = []
        for i in range(len(line)):
            if line[i] == " ": continue
            word_list.append(line[i])
        word_set = word_set | set(word_list)  # 训练预料库中所有字的集合

        lineArr = line.split(" ")
        line_state = []
        for item in lineArr:
            # print("getList:", getList(item))
            line_state.extend(getList(item))  # 一句话对应一行连续的状态
        print("line:", line)
        print("linestate:", line_state)
        if len(word_list) != len(line_state):
            print (sys.stderr, "[line_num = %d][line = %s]" % (line_num, line.endoce("utf-8", 'ignore')))
        else:
            for i in range(len(line_state)):
                if i == 0:
                    Pi_dic[line_state[0]] += 1  # Pi_dic记录句子第一个字的状态，用于计算初始状态概率
                    Count_dic[line_state[0]] += 1  # 记录每一个状态的出现次数
                else:
                    A_dic[line_state[i - 1]][line_state[i]] += 1  # 用于计算转移概率
                    Count_dic[line_state[i]] += 1
                    if not word_list[i] in B_dic[line_state[i]]:
                        B_dic[line_state[i]][word_list[i]] = 0.0
                    else:
                        B_dic[line_state[i]][word_list[i]] += 1  # 用于计算发射概率
        # print("word_set:" ,word_set)
        # print("word_list:",word_list)
        # print("word_state:",state_list)
    Output()
    ifp.close()
def mytrain(PATH1, PaTH2):
    global word_set  # 初始是set()
    global line_num  # 初始是-1
    file = open(PATH1, encoding='UTF-8')
    file2 = open(PaTH2, encoding='UTF-8')
    init()
    lastState='Q'
    for line in file:
        line_num += 1
        line = line.strip()
        print(line)
        # print(line)
        lineArr = line.split(" ")
        if(len(lineArr)==2):
            word_set.add(lineArr[0])
            if lastState == "Q":
                Pi_dic[lineArr[1]] += 1  # Pi_dic记录句子第一个字的状态，用于计算初始状态概率
                Count_dic[lineArr[1]] += 1  # 记录每一个状态的出现次数
            else:
                A_dic[lastState][lineArr[1]] += 1  # 用于计算转移概率
                Count_dic[lineArr[1]] += 1
                if not lineArr[0] in B_dic[lineArr[1]]:
                    B_dic[lineArr[1]][lineArr[0]] = 0.0
                else:
                    B_dic[lineArr[1]][lineArr[0]] += 1  # 用于计算发射概率
            lastState = lineArr[1]
    lastState = 'Q'
    for line in file2:
        line_num += 1
        line = line.strip()
        print(line)
        # print(line)
        lineArr = line.split(" ")
        if(len(lineArr)==2):
            word_set.add(lineArr[0])
            if lastState == "Q":
                Pi_dic[lineArr[1]] += 1  # Pi_dic记录句子第一个字的状态，用于计算初始状态概率
                Count_dic[lineArr[1]] += 1  # 记录每一个状态的出现次数
            else:
                A_dic[lastState][lineArr[1]] += 1  # 用于计算转移概率
                Count_dic[lineArr[1]] += 1
                if not lineArr[0] in B_dic[lineArr[1]]:
                    B_dic[lineArr[1]][lineArr[0]] = 0.0
                else:
                    B_dic[lineArr[1]][lineArr[0]] += 1  # 用于计算发射概率
            lastState = lineArr[1]
    Output()
    file.close()



def load_model(f_name):
    ifp = open(f_name, 'rb')
    return eval(ifp.read())  # eval参数是一个字符串, 可以把这个字符串当成表达式来求值,



def viterbi(obs, states, start_p, trans_p, emit_p):  # 维特比算法
    V = [{}]
    path = {}
    for y in states:  # 初始值
        V[0][y] = start_p[y] * emit_p[y].get(obs[0])  # 在位置0，以y状态为末尾的状态序列的最大概率
        path[y] = [y]
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}
        for y in states:  # 从y0 -> y状态的递归
            list = []
            for y0 in states:
                if V[t - 1].get(y0, 0) >= 0:
                    list.append((V[t - 1][y0] * trans_p[y0].get(y) * emit_p[y].get(obs[t]), y0))
            if len(list)>0:
                (prob, state) = max(list)
                # print("state:", state)
                V[t][y] = prob
                newpath[y] = path[state] + [y]
            # else:
            #     V[t][y] = 0
            #     newpath[y] = path[y] + [y]
        path = newpath  # 记录状态序列
    # print(V)
    list2 = [(V[len(obs) - 1].get(y, 0), y) for y in states]
    (prob, state) = max([(V[len(obs) - 1].get(y, 0), y) for y in states])  # 在最后一个位置，以y状态为末尾的状态序列的最大概率
    # print(path)
    # print(state)
    return  path.get(state, 0)  # 返回概率和状态序列



def cut(sentence):
    prob_start = load_model("HMM\prob_start.py")
    prob_trans = load_model("HMM\prob_trans.py")
    prob_emit = load_model("HMM\prob_emit.py")
    prob, pos_list = viterbi(sentence, ('B', 'I', 'E', 'S'), prob_start, prob_trans, prob_emit)
    return (prob, pos_list)

def predict(sentence):
    prob_start = load_model("HMM\prob_start.py")
    prob_trans = load_model("HMM\prob_trans.py")
    prob_emit = load_model("HMM\prob_emit.py")
    states = ('B', 'I', 'E', 'S')
    wordset = set()
    for y in states:  # 初始值
        for x in sentence:
            if x not in prob_emit[y].keys():
                wordset.add(x)
    res = ""
    split = ""

    if(len(wordset)>0):
        for x in wordset:
            split+=x
        split="["+split+"]"
        sentences = re.split(split, sentence)
        for mycentence in sentences:
            print(mycentence)
            if len(mycentence)>0:
                reslist = viterbi(mycentence, ('B', 'I', 'E', 'S'), prob_start, prob_trans, prob_emit)
                for l in reslist:
                    res+=l
            res+="S"
        res=res[0:len(res)-1]
    else:
        reslist = viterbi(sentence, ('B', 'I', 'E', 'S'), prob_start, prob_trans, prob_emit)
        for l in reslist:
            res += l
    return res

if __name__ == "__main__":
    # train()
    # test_str = u"新华网驻东京记者报道"
    # prob, pos_list = cut(test_str)
    # print (test_str)
    # print (pos_list)

    # fileName = ""
    # file = open(fileName, encoding='UTF-8')
    # for line in file:
    #     line =line.strip()
    #     # print(line)
    #     lineArr = line.split(" ")
    #     print(len(lineArr))

    mytrain("dataset/dataset1/train.utf8", "dataset/dataset2/train.utf8")
    # "东省泸沽湖"
    # print(predict("空间数据库给对方看见"))
    print(predict("空间数据库给对方看见啥尽快赶到还是发给东省泸沽湖"))
    # a ="[]"
    # print(re.split(a, '空间数据库给对方看见啥尽快赶到还是发给东省泸沽湖'))