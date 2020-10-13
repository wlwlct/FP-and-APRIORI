import pandas as pd

'''
Get Seed and repeat
'''
# Generate seed C1
def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
    C1.sort()
    return [frozenset(i) for i in C1]


#Scan through datasets, remove the ones below min support
def scanD(D, Ck, minSupport):
    # Generate counts for the C
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                if can not in ssCnt:
                    ssCnt[can] = 1
                else:
                    ssCnt[can] += 1
    print('Cn with count:',pd.DataFrame.from_dict(ssCnt,orient='index'))
    # Check weather meet minimum support or not, remove the ones below
    numItems = float(len(D))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key]/numItems
        print('support',support,'min_support',minSupport,'Bool',support >= minSupport)
        if support >= minSupport:
            retList.insert(0, key)
            supportData[key] = support
    print('supportData:',pd.DataFrame.from_dict(supportData,orient='index'))
    print('-'*30)
    return retList, supportData


#Generate Ck according to Lk
def aprioriGen(Lk, k):
    #print('AprioriGen',Lk)
    #print('AprioriGen',k)
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk):
            L1 = list(Lk[i])[: k-2]
            L2 = list(Lk[j])[: k-2]
            L1.sort()
            L2.sort()
            #If the all elements exept the last are same, merge two elements
            if L1 == L2:
                retList.append(Lk[i] | Lk[j])
    return retList


def apriori(dataSet, minSupport=0.5):
    #Generate C1 
    C1 = createC1(dataSet)
    D=list(map(set,dataSet))
    L1, supportData = scanD(D, C1, minSupport)

    #print('supportData',pd.DataFrame(supportData.values(),supportData.keys()))
    #print('L1',(L1))
    #print('------Seed------'*5,'\n')

    #repeatively generate L and C
    L = [L1]
    k = 2 #help to put values in L
    while (len(L[k-2]) > 0):
        #print('L_',k-2,L[k-2])
        Ck = aprioriGen(L[k-2], k) 
        #print(pd.DataFrame({'Ck':Ck}))
        Lk, supK = scanD(D, Ck, minSupport) 
        supportData.update(supK)
        #print('*'*10)
        if len(Lk) == 0:
            break
        # all the Lk generated along the way are put into L.
        L.append(Lk)
        k += 1
    return L, supportData


if __name__ == "__main__":
    dataSet = [['I1','I2','I5'],['I2','I4'],['I2','I3'],['I1','I2','I4'],['I1','I3'],['I2','I3'],['I1','I3'],['I1','I2','I3','I5'],['I1','I2','I3']]
    LI, S = apriori(dataSet, minSupport=1.9/9)