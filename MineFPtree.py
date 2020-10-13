import pandas as pd
'''
Load data
'''
def loadSimpDat():
    simpDat = [['I1','I2','I5'],['I2','I4'],['I2','I3'],['I1','I2','I4'],['I1','I3'],['I2','I3'],['I1','I3'],['I1','I2','I3','I5'],['I1','I2','I3']]
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
                    C1[ii]=ii.values()
                except:
                    C1[ii]=1
            else:
                C1[ii]+=1
    C1={key:value for key, value in C1.items() if value/len(trans)>=min_support}#include min_support
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
    for itemset in trans:
        #order the itemset according to the header table
        if len(itemset)>0:
            if len(itemset)>1:
                SortedItems=sorted(list(itemset),key=lambda x:headertable[x][0],reverse=True)
            else:
                SortedItems=sorted(itemset,key=lambda x:headertable[x][0],reverse=True)
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

        # Conditional Pattern Base
        CPB = findPrefixPath(baseitem, headertable[baseitem][1])
        if len(CPB)!=0:
            print(pd.DataFrame({'Item':[str(baseitem) for i in range(len(CPB))],'Prefix':[(i) for i in CPB]}))

        CPBC1=GenC1(CPB,min_support)
        if len(CPBC1)!=0:
            print(CPBC1)
            print('-'*30)
        CondFPTree, Condheadertable = Build_tree(list(CPB.keys()),CPBC1,1)
        if Condheadertable is not None:
            #myCondTree.disp(1)
            mineTree(CondFPTree, Condheadertable, min_support, newFreqSet, freqItemList)


if __name__=='__main__':
    min_support=0.6
    simpDat=loadSimpDat()
    C1=GenC1(simpDat,min_support)
    myTree,myHeader=Build_tree(simpDat,C1)
else:
    freqItemList,preFix=[],set([])
    mineTree(myTree, myHeader, min_support, preFix, freqItemList)
