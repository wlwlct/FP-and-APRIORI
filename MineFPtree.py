import pandas as pd
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
def GenC1(trans,min_support):
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
    C1={key:value for key, value in C1.items() if value>=min_support}#include min_support
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

def mineTree(inTree, headertable, min_support, preFix, freqItemList):
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
        CPBC1=GenC1(CPB,min_support)
        #if len(CPBC1)!=0:
            #print(CPBC1)
            #print('-'*30)
        CondFPTree, Condheadertable = Build_tree(list(CPB.keys()),CPBC1,list(CPB.values()))
        if Condheadertable is not None:
            #myCondTree.disp(1)
            mineTree(CondFPTree, Condheadertable, min_support, newFreqSet, freqItemList)


'''
Generate Support Number
'''
def calSuppData(FPtree,headerTable, freqItemList, total):
    suppData = {}
    for Item in freqItemList:
        print('*'*10)
        print(Item)
        print('*'*10)
        # Search from smallest to largest
        Item = sorted(Item, key=lambda x:headerTable[x][0])
        base = findPrefixPath(Item[0], headerTable[Item[0]][1])
        print('Item_0:',Item[0],'Base Before:', base)

        base={frozenset(set(each_base).union({Item[0]})):value for each_base,value in base.items()}
        if Item[0] in FPtree.children.keys():
            base[Item[0]]=FPtree.children[Item[0]].count+base.get(Item[0],0)
        print('Base After:', base)


        # 计算支持度
        support = 0
        for B in base:
            print('Item:',frozenset(Item))
            print('B:',B,base[B])
            if not isinstance(B,str):
                set_B=set(B)
            else:
                set_B={B}
            if frozenset(Item).issubset(set_B):
                support += base[B]
            print('Support:',support)
        print('-'*40)

        suppData[frozenset(Item)] = support#/float(total)
    return suppData

if __name__=='__main__':
    simpDat=loadSimpDat()
    min_support=1.9/9*len(simpDat)
    C1=GenC1(simpDat,min_support)
    myTree,myHeader=Build_tree(simpDat,C1)
    freqItemList,preFix=[],set([])
    mineTree(myTree, myHeader, min_support, preFix, freqItemList)

    Support=calSuppData(myTree,myHeader,freqItemList,len(simpDat))

