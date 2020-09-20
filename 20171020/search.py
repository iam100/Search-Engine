import nltk
import sys 
import re
import os
from Stemmer import Stemmer
from nltk.corpus import stopwords
from collections import defaultdict as ddic
import time
import math

stemmer = Stemmer('english')
stop_words = set(stopwords.words('english'))

class searchClass():
    def __init__(self):
        self.query_fname = sys.argv[1]
        self.outfile = open("./query_op.txt",'w')
        self.titleOffset = []
        self.offset = []
        self.vocabFile = open("./inverted_index/vocabulary.txt",'r')
        self.titleFile = open("./inverted_index/title.txt",'r')
        self.keys = ['t:','b:','i:','c:','r:','l:']
        self.queryType = 0
        self.num_query = 0
        self.nResults = 0

    def load_files(self):
        print("Loading Files")
        with open(self.query_fname,'r') as f:
            self.queries = f.readlines()
        
        with open("./inverted_index/titleOffset.txt",'r') as f:
            for line in f:
                self.titleOffset.append(int(line.strip()))
        with open("./inverted_index/offset.txt",'r') as f:
            for line in f.readlines():
                try:
                    self.offset.append(int(line.strip()))
                except:
                    pass
        with open("./inverted_index/fileNumbers.txt",'r') as f:
            var = f.read()
            var = var.strip()
            self.nFiles = int(var)
    def fieldQuery(self,query):
        text = re.findall(r'[b|i|t|c|r|l]:([^:]*)(?!\S)',query)
        fields = re.findall(r'[b|i|t|c|r|l]:',query)
        fields = [re.sub(r':',r'',field) for field in fields]
        text = [i.lower() for i in text]


        docDict = ddic(dict)
        docFreq = ddic()

        for i in range(len(fields)):
            words = text[i].split(' ')
            for w in words:
                if w in stop_words:
                    continue
                w = stemmer.stemWord(w)
                docs, _ = self.binarySearch(w,self.offset,self.vocabFile)
                if len(docs) > 0:
                    fileNo = docs[0]
                    filename = "./inverted_index/"+fields[i]+str(fileNo)+".txt"
                    with open(filename,'r') as fieldFile:
                        rList, df  = self.find_documents(filename,fileNo,fields[i],w,fieldFile)
                        docDict[w][fields[i]] = rList
                        docFreq[w] = df
        return docDict, docFreq
    
    def normalQuery(self,query):
        docDict = ddic(dict)
        docFreq = ddic()

        query = query.encode("ascii",errors="ignore").decode()
        query = query.split()

        query = [w for w in query if w not in stop_words]
        query = stemmer.stemWords(query)

        for word in query:
            docs, _ = self.binarySearch(word,self.offset,self.vocabFile)
            if len(docs) > 0:
                fileNo = docs[0]
                docFreq[word] = docs[1]
                for field in self.keys:
                    fname = "./inverted_index/"+field+fileNo+".txt"
                    with open(fname,'r') as f:
                        arr = self.find_documents(fname,fileNo,field,word,f)
                         
                        docDict[word][field] = arr[0]
        return docDict, docFreq

        

    def find_documents(self,fname,fileno,field,word,filefield):
        fieldOffset = []
        freq = []
        field_off_fname = "./inverted_index/offset_"+field+fileno+".txt"

        with open(field_off_fname,'r') as f:
            lines = f.readlines()
            for line in lines:
                x = line.strip()
                off,count = x.split()
                freq.append(int(count))
                fieldOffset.append(int(off))
        arr = self.binarySearch(word, fieldOffset,filefield)
        return arr[0],freq[arr[1]]


    def binarySearch(self,word,offset,f,datatype = 'string'):
        low = 0
        high = len(offset)
        while high > low:
            mid = int((low+high)/2)
            # print(offset[mid])
            # print(offset
            # )
            f.seek(offset[mid])
            pointer = f.readline()
            pointer = pointer.strip()
            pointer = pointer.split()
            comp_word  = word
            comp_point = pointer[0]
            if (datatype == 'int'):
                comp_word = int(comp_word)
                comp_point = int(comp_point)
            if comp_point == comp_word:
                return pointer[1:],mid
            elif comp_word > comp_point:
                low = mid + 1
            else:
                high = mid
        return [],-1
    
    def ranking(self,results,docFreq):
        docs = ddic(float)
        queryID = {}

        scores = {'t':0.25,'b':0.25,'i':0.20,'c':0.10,'r':0.05,'l':0.05}
        float_n = float(self.nFiles) 
        # float_doc

        for key in docFreq:
            float_doc = float(docFreq[key])
            queryID[key] = math.log((float_n - float_doc + 0.5)/(float_doc+0.5))
            docFreq[key] = math.log(float_n/float_doc)
        
        for word in results:
            pList = results[word]
            for field in pList:
                if len(field) <= 0:
                    pass
                else:
                    pos = pList[field]
                    factor = scores[field]
                    for i in range(0,len(pos),2):
                        x = factor * (1+math.log(float(pos[i+1]))) * docFreq[word]
                        x = float(x)
                        docs[pos[i]] = docs[pos[i]] + x
        return docs

    def querying(self):
        for query in self.queries:
            self.queryType = 0
            start = time.time()
            self.num_query  = self.num_query + 1
            query = query.strip()
            query = query.lower()
            self.nResults, query = query.split(",")
            query = query.strip()

            self.nResults = int(self.nResults)

            for word in self.keys:
                if word in query:
                    self.queryType = 1
                    break
            if self.queryType:
                results,docFreq = self.fieldQuery(query)
                results = self.ranking(results,docFreq)
            else:
                results,docFreq = self.normalQuery(query)
                results = self.ranking(results,docFreq)
            
            if len(results) > 0:
                results = sorted(results,key=results.get, reverse=True)
                results = results[:self.nResults]
                for key in results:
                    title, _ = self.binarySearch(key,self.titleOffset,self.titleFile,'int')
                    # print(title)
                    print(','.join([key] + [" ".join(title)]),file=self.outfile)
            
            end = time.time()
            print(str(end-start)+", "+str((end-start)/self.nResults)+"\n",file=self.outfile)
        self.outfile.close()

if __name__ == '__main__':
    search = searchClass()
    search.load_files()
    search.querying()