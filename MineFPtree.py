import pandas as pd
import itertools
'''
Load data
'''
def loadSimpDat():
    simpDat = [['I1','I2','I5'],['I2','I4'],['I2','I3'],['I1','I2','I4'],['I1','I3'],['I2','I3'],['I1','I3'],['I1','I2','I3','I5'],['I1','I2','I3']]
    '''simpDat=[]
    with open('Example_data.txt', 'r') as f:
        for line in f.readlines():
            L=line.split(',')
            L[-1]=L[-1].replace('\n','')
            simpDat.append(L)'''
    return simpDat

#tree node
class TreeNode:
    def __init__(self, item, count, parentNode):
        self.item=item
        self.count=count
        self.nodelink=None
        self.parent=parentNode
        self.children={}
    def inc_count(self,num):
        self.count+=num

'''
Generate Headertable and remove item does not meet minimum support
|item|counts|Nodelink
'''
def GenC1(trans,min_support,total):
    C1={}
    for i in trans:
        for ii in set(i):
            if ii not in C1:
                try:
                    C1[ii]=trans[i]
                except:
                    C1[ii]=1
            else:
                try:
                    C1[ii]+=trans[i]
                except:
                    C1[ii]+=1
    C1={key:value for key, value in C1.items() if value>=min_support*total}#include min_support
    #print('C1',C1)
    return {i:[k,None] for i,k in sorted(C1.items(),key=lambda x:x[1],reverse=True)}

def link_same_items(curr,targetNode):
    while curr.nodelink is not None:
        curr=curr.nodelink
    curr.nodelink=targetNode


'''
Build Tree
'''
def link_same_items(curr,targetNode):
    while curr.nodelink is not None:
        curr=curr.nodelink
    curr.nodelink=targetNode

def updateTree_Table(SortedItems,FPTree,headertable,count):
    if SortedItems[0] in FPTree.children:
        FPTree.children[SortedItems[0]].inc_count(count)
    else:
        FPTree.children[SortedItems[0]]=TreeNode(SortedItems[0],count,FPTree)
        if headertable[SortedItems[0]][1]==None:
            headertable[SortedItems[0]][1]=FPTree.children[SortedItems[0]]
        else:
            link_same_items(headertable[SortedItems[0]][1], FPTree.children[SortedItems[0]])
    if len(SortedItems)>1:
        updateTree_Table(SortedItems[1:],FPTree.children[SortedItems[0]],headertable,count)

def Build_tree(trans,headertable,count=1):
    recTree=TreeNode('Null',1,None)
    for iii,itemset in enumerate(trans):
        #order the itemset according to the header table
        itemset=[i for i in itemset if i in headertable]
        if len(itemset)>0:
            SortedItems=sorted(list(itemset),key=lambda x:headertable[x][0],reverse=True)
            try:
                updateTree_Table(SortedItems,recTree,headertable,count[iii])
            except:
                updateTree_Table(SortedItems,recTree,headertable,count)
    return recTree,headertable

'''
Mine Tree
'''
def ascendTree(leafNode,PrefixPath):
    if leafNode.parent is not None:
        PrefixPath.append(leafNode.item)
        ascendTree(leafNode.parent, PrefixPath)

def findPrefixPath(baseitem,TreeNode):
    CPB={}
    while TreeNode is not None:
        PrefixPath=[]
        ascendTree(TreeNode,PrefixPath)
        if len(PrefixPath)>1:
            CPB[frozenset(PrefixPath[1:])]=TreeNode.count
        TreeNode=TreeNode.nodelink
    return CPB

def mineTree(inTree, headertable, min_support, preFix, freqItemList,total):
    reverse_headertable = [v for v,_ in sorted(headertable.items(), key=lambda x: x[1][0])]
    for baseitem in reverse_headertable:
        newFreqSet = preFix.copy()
        newFreqSet.add(baseitem)
        freqItemList.append(newFreqSet)
        #print('newFreqSet:',newFreqSet)
        #print('Freqitemls:',freqItemList)

        # Conditional Pattern Base
        CPB = findPrefixPath(baseitem, headertable[baseitem][1])
        #if len(CPB)!=0:
            #print(pd.DataFrame({'Item':[str(baseitem) for i in range(len(CPB))],'Prefix':[(i) for i in CPB],'count':[(i) for i in CPB.values()]}))
        CPBC1=GenC1(CPB,min_support,total)
        #if len(CPBC1)!=0:
            #print(CPBC1)
            #print('-'*30)
        CondFPTree, Condheadertable = Build_tree(list(CPB.keys()),CPBC1,list(CPB.values()))
        if Condheadertable is not None:
            #myCondTree.disp(1)
            mineTree(CondFPTree, Condheadertable, min_support, newFreqSet, freqItemList,total)


'''
Generate Support Number
'''
def calSuppData(FPtree,headerTable, freqItemList):
    suppData = {}
    for Item in freqItemList:
        base={}
        #print('*'*10)
        #print(Item)
        #print('*'*10)
        # Search from smallest to largest
        Item = sorted(Item, key=lambda x:headerTable[x][0])
        for ii in range(len(Item)):
            prebase = findPrefixPath(Item[ii], headerTable[Item[ii]][1])
            #print('Item:',Item[ii],'Base Before:', prebase)

            prebase={frozenset(set(each_base).union({Item[ii]})):value for each_base,value in prebase.items()}
            if Item[ii] in FPtree.children.keys():
                prebase[Item[ii]]=FPtree.children[Item[ii]].count+prebase.get(Item[ii],0)
            #print('Base After:', prebase)
            #print('Item:',Item[ii],'preBase:', prebase)
            base.update(prebase)
            #print('Base:',base)

        #print('-----Start to count:')
        support = 0
        for B in base:
            #print('Item:',frozenset(Item))
            #print('B:',B,base[B])
            if not isinstance(B,str):
                set_B=set(B)
            else:
                set_B={B}
            if frozenset(Item).issubset(set_B):
                support += base[B]
            #print('Support:',support)
        #print('-'*40)

        suppData[frozenset(Item)] = support
    return suppData


'''
Generate Confidence
'''
def calconf(FPtree,headerTable,freqItemList,Support,min_conf):
    allrules=[]
    for itemset in freqItemList:
        S=Support[frozenset(itemset)]
        check_leng=len(itemset)-1
        if check_leng==0:
            pass
            #allrules.append((itemset,itemset,'nan',headerTable[list(itemset)[0]][0],S,'nan'))
            #print(itemset,':',headerTable[list(itemset)[0]][0])
            #print(itemset,'--->','Nothing','Confidence:',headerTable[list(itemset)[0]][0],'Support:',S)
        for i in range(check_leng):
            n=i+1
            Test=[set(i) for i in itertools.combinations(itemset,n)]
            Rest=[itemset-i for i in Test]
            #print('Test:',Test)
            #print('Rest:',Rest)
            try:
                Confidence=calSuppData(FPtree,headerTable,Test)
                supportB=calSuppData(FPtree,headerTable,Rest)
                #print('Condidence:',Confidence)
                Confidence_value=[Confidence[frozenset(i)] for i in Test]
                supportB_value=[supportB[frozenset(i)] for i in Rest]
                #print('Confidence_value:',Confidence_value)
                for rule in range(len(Test)):
                    if Confidence_value[rule]*(min_conf)<=S:
                        allrules.append((itemset,Test[rule],Rest[rule],Confidence_value[rule],S,supportB_value[rule]))
                        #print(Test[rule],'--->',Rest[rule],'Confidence:',Confidence_value[rule],'Support:',S)
            except:
                raise
            #print('-'*50)
    return allrules
    
def FP(simpDat,min_support,total):
    C1=GenC1(simpDat,min_support,total)
    myTree,myHeader=Build_tree(simpDat,C1)
    freqItemList,preFix=[],set([])
    mineTree(myTree, myHeader, min_support, preFix, freqItemList,total)
    Support=calSuppData(myTree,myHeader,freqItemList)#{Frozenset:count}
    return freqItemList,Support, myTree,myHeader

def printsupport(S):
    S_table=pd.DataFrame.from_dict(S,orient='index').reset_index()
    S_table.columns=['itemset','support']
    S_table
    return S_table

def printrules(rules,total):
    C=['Frequent Itemset(AUB)','From(A)','To(B)','Confident Number(num of A)','Support Number(num of AUB)','Support Number(num of B)']
    Ruletable=pd.DataFrame(rules)
    Ruletable.columns=C
    Ruletable['Confidence']=Ruletable['Support Number(num of AUB)']/Ruletable['Confident Number(num of A)']
    Ruletable['Support']=Ruletable['Support Number(num of AUB)']/total
    Ruletable['Lift']=(Ruletable['Support Number(num of AUB)']/total)/(Ruletable['Support Number(num of B)']/total)/(Ruletable['Confident Number(num of A)']/total)
    return Ruletable

if __name__=='__main__':
    simpDat=loadSimpDat()
    min_support=1.9/9 #*len(simpDat)
    freqItemList,Support,myTree,myHeader=FP(simpDat,min_support,len(simpDat))

    print('Dataset', simpDat)
    print('frequent list:',freqItemList)
    print(printsupport(Support))
    min_conf=0.5
    Conf=calconf(myTree,myHeader,freqItemList,Support,min_conf)
    print(printrules(Conf,len(simpDat)))