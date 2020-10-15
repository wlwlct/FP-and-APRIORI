import pandas as pd
import itertools
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
    #print('Cn with count:',pd.DataFrame.from_dict(ssCnt,orient='index'))
    # Check weather meet minimum support or not, remove the ones below
    numItems = float(len(D))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key]#/numItems
        #print('support',support,'min_support',minSupport,'Bool',support >= minSupport)
        if support >= minSupport*numItems:
            retList.insert(0, key)
            supportData[key] = support
    #print('supportData:',pd.DataFrame.from_dict(supportData,orient='index'))
    #print('-'*30)
    return retList, supportData

def notRedundant(mergedlist,Lkm1,km1,l1,l2):
    sub_mergedlist=[set(i) for i in itertools.combinations(mergedlist,km1) if set(i) not in [l1,l2]]
    for i in sub_mergedlist:
        if i not in Lkm1:
            return False
    return True


#Generate Ck according to Lk
def aprioriGen(Lk, k):
    #print('AprioriGen Lk',Lk)
    #print('AprioriGen k',k)
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
                mergedlist=Lk[i] | Lk[j]
                #print('---------',mergedlist,k-1)
                if notRedundant(mergedlist,Lk,k-1,Lk[i],Lk[j]):
                    retList.append(mergedlist)
                #else:
                #    print('----Remove-----',mergedlist,k-1)
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
        #print(pd.DataFrame(supK.values(),supK.keys()))
        supportData.update(supK)
        #print('*'*10)
        if len(Lk) == 0:
            break
        # all the Lk generated along the way are put into L.
        L.append(Lk)
        k += 1
    return L, supportData


'''
Mine Association Rule
'''
def calcConf(freqSet, H, supportData, brl, minConf=0.7):
    prunedH = []
    for conseq in H:
        conf = supportData[freqSet]/supportData[freqSet-conseq]
        #print('freqSet:',freqSet)
        #print('conseq:',conseq)
        #print('freqSet-conseq',freqSet-conseq)
        #print('conf:',conf)
        if conf >= minConf:
            #print(freqSet-conseq, '-->', conseq, 'conf:', conf)
            brl.append((freqSet,freqSet-conseq, conseq,supportData[freqSet-conseq],supportData[freqSet]))
            prunedH.append(conseq)
    return prunedH

def rulesFromConseq(freqSet, H, supportData, brl, minConf=0.7):
    m = len(H[0])
    #print('*'*10*m,'H[0]',H[0])
    #print('H:',H)
    if (len(freqSet) >(m+1)):
        H = calcConf(freqSet, H, supportData, brl, minConf)
        Hmp1 = aprioriGen(H, m+1)
        #print('*'*20*m,Hmp1)
        Hmp1 = calcConf(freqSet, Hmp1, supportData, brl, minConf)
        #print('Hmp1=', Hmp1)
        #print('len(Hmp1)=', len(Hmp1), 'len(freqSet)=', len(freqSet))
        if (len(Hmp1) >= 1):
            rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)

# Generate Association rules
def generateRules(L, supportData, minConf=0.7):
    bigRuleList = []
    for i in range(1, len(L)):
        for freqSet in L[i]:#wont calculate with frequent item=1
            H1 = [frozenset([item]) for item in freqSet]
            #print('H1',H1)
            if (i > 1):#if only has two items, no need to split the relation
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
            #print('-'*30)
    return bigRuleList

def printrules(rules,total):
    C=['Frequent itemset','From','To','Confident number','Support Number']
    Ruletable=pd.DataFrame(rules)
    Ruletable.columns=C
    Ruletable['Confidence']=Ruletable['Support Number']/Ruletable['Confident number']
    Ruletable['Support']=Ruletable['Support Number']/total
    Ruletable['Lift']=Ruletable['Confidence']/Ruletable['Support']
    return Ruletable

def printsupport(S):
    S_table=pd.DataFrame.from_dict(S,orient='index').reset_index()
    S_table.columns=['itemset','support']
    S_table
    return S_table

if __name__ == "__main__":
    dataSet = [['I1','I2','I5'],['I2','I4'],['I2','I3'],['I1','I2','I4'],['I1','I3'],['I2','I3'],['I1','I3'],['I1','I2','I3','I5'],['I1','I2','I3']]
    LI, S = apriori(dataSet, minSupport=1.9/9)
    rules = generateRules(LI, S, minConf=0)
    printrules(rules,len(dataSet))
