#!/usr/bin/env python
# coding: utf-8

# In[1]:
from Stemmer import Stemmer
from collections import defaultdict as ddic
from nltk.corpus import stopwords
import xml.sax
import re
import os
import sys
import nltk
import heapq
import threading
from tqdm import tqdm
import glob

nltk.download('stopwords')
nltk.download('punkt')


# In[2]:


titleID = {}
fileNo = 0
pageNo = 0
iMap = ddic(list)
offset = 0
tokens_total = 0

stop_words = set(stopwords.words('english'))
stemmer = Stemmer('english')


# In[3]:


# filename = '../enwiki-20200801-pages-articles-multistream1.xml-p1p30303'
# sergey = '../Sergey_brin.xml'
class writeFinalIndex():
    def __init__(self, data, finalCount, offsetSize):
        self.data = data
        self.finalCount = finalCount
        self.offsetSize = offsetSize

        self.distinctWords = []
        self.offset = []
        keys = ['t', 'b', 'i', 'l', 'c', 'r']
        self.keys = keys
        self.maindict = {'t':ddic(dict),'b':ddic(dict),'i':ddic(dict),'l':ddic(dict),'c':ddic(dict),'r':ddic(dict)}

        self.datadict = {'t':[],'b':[],'i':[],'l':[],'c':[],'r':[]}

        self.offsetdict = {'t':[],'b':[],'i':[],'l':[],'c':[],'r':[]}

        self.prevdict = {'t':0,'b':0,'i':0,'l':0,'c':0,'r':0}

    def findOffset(self):
        for key in sorted(self.data.keys()):
            docs = self.data[key]
            temp = []
            len_docs = len(docs)
            for i in range(0, len_docs):
                posting = docs[i]
                exp = str(r'.*D([0-9]*).*')
                docID = re.sub(exp, r'\1', posting)
                exp = str(r'.*t([0-9]*).*')
                temp = re.sub(exp, r'\1', posting)
                if temp != posting:
                    # print('t')
                    self.maindict['t'][key][docID] = float(temp)

                temp = re.sub(r'.*b([0-9]*).*', r'\1', posting)
                if temp != posting:
                    # print('b')
                    self.maindict['b'][key][docID] = float(temp)

                temp = re.sub(r'.*i([0-9]*).*', r'\1', posting)
                if temp != posting:
                    # print('i')
                    self.maindict['i'][key][docID] = float(temp)

                temp = re.sub(r'.*c([0-9]*).*', r'\1', posting)
                if temp != posting:
                    # print('c')
                    self.maindict['c'][key][docID] = float(temp)

                temp = re.sub(r'.*l([0-9]*).*', r'\1', posting)
                if temp != posting:
                    # print('l')
                    self.maindict['l'][key][docID] = float(temp)

                temp = re.sub(r'.*r([0-9]*).*', r'\1', posting)
                if temp != posting:
                    # print('r')
                    self.maindict['r'][key][docID] = float(temp)
            string = key + ' ' + str(self.finalCount) + ' ' + str(len(docs))
            self.distinctWords.append(string)
            self.offset.append(str(self.offsetSize))
            self.offsetSize += len(string) + 1

    def appendData(self):
        for key in tqdm(sorted(self.data.keys())):
            for inkey in self.keys:
                if key in self.maindict[inkey]:
                    # print(key)
                    string = key + ' '
                    docs = self.maindict[inkey][key]
                    docs = sorted(docs, key=docs.get, reverse=True)
                    for doc in docs:
                        string +=  doc + ' ' + str(self.maindict[inkey][key][doc]) + ' '
                    self.offsetdict[inkey].append(
                        str(self.prevdict[inkey]) + ' ' + str(len(docs)))
                    self.prevdict[inkey] += len(string) + 1
                    self.datadict[inkey].append(string)

    def writeAll(self):
        for inkey in self.keys:
            # print(self.datadict[inkey])
            fname = './inverted_index/' + inkey + str(self.finalCount) + '.txt'
            with open(fname, 'w') as f:
                f.write('\n'.join(self.datadict[inkey]))

        for inkey in self.keys:
            fname = './inverted_index/offset_' + inkey + str(self.finalCount) + '.txt'
            with open(fname, 'w') as f:
                f.write('\n'.join(self.offsetdict[inkey]))

        with open('./inverted_index/vocabulary.txt', 'a') as f:
            f.write('\n'.join(self.distinctWords))
            f.write('\n')

        with open('./inverted_index/offset.txt', 'a') as f:
            f.write('\n'.join(self.offset))
            f.write('\n')

    def returnFinal(self):
        print(self.finalCount)
        return (self.finalCount+1, self.offsetSize)


def indexMerge(filecount):
    data = ddic(list)
    words = {}
    files = {}
    top = {}
    flag = [0] * filecount
    finalcount = 0
    offsetSize = 0
    heap = []
    zero = 0

    for i in range(filecount):
        filename = 'inverted_index/index' + str(i) + '.txt'
        files[i] = open(filename, 'r')
        flag[i] = True
        top[i] = files[i].readline()
        top[i] = top[i].strip()
        words[i] = top[i].split()

        if words[i][zero] not in heap:
            heapq.heappush(heap, words[i][zero])
    count = zero
    while(any(flag) == 1):
        temp = heapq.heappop(heap)
        count += 1
        # print(count)

        if(count % 100000 == zero):
            oldFilecount = finalcount
            finalIndexClass = writeFinalIndex(data, finalcount, offsetSize)
            finalIndexClass.findOffset()
            finalIndexClass.appendData()
            finalIndexClass.writeAll()
            finalcount, offsetSize = finalIndexClass.returnFinal()

            if oldFilecount != finalcount:
                data = ddic(list)

        for i in range(0, filecount):
            if flag[i] == 1:
                if words[i][zero] == temp:
                    data[temp].extend(words[i][1:])
                    top[i] = files[i].readline()
                    top[i] = top[i].strip()
                    if top[i] == '':
                        flag[i] = zero
                        files[i].close()
                    else:
                        words[i] = top[i].split()
                        if words[i][zero] not in heap:
                            heapq.heappush(heap, words[i][zero])
    finalIndexClass = writeFinalIndex(data, finalcount, offsetSize)
    finalIndexClass.findOffset()
    finalIndexClass.appendData()
    finalIndexClass.writeAll()
    finalcount, offsetSize = finalIndexClass.returnFinal()

def cleanupText(stats):
    global stop_words
    global stemmer
    global tokens_total

    stats = stats.encode("ascii", errors="ignore").decode()
    exp = str(r'http[^\ ]*\ ')
    stats = re.sub(exp, r' ', stats)
    exp = str(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;')
    stats = re.sub(exp, r' ', stats)
    stats = re.sub(
        r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\u2013|\n',
        r' ', stats)
    stats = stats.split()
    tokens_total += len(stats)
    stats = [i for i in stats if not i in stop_words]
    stats = stemmer.stemWords(stats)
    return stats


def writeFile(pageno, imap, fileno, titleoffset):

    global titleID
    global inverted_index_dir
    global invertedindex_stat
    global tokens_total

    inv_ind_total = 0
    prevoff = titleoffset

    stats = []
    for k in sorted(imap):
        initial = k + ' '
        fi = imap[k]
        inv_ind_total += len(fi)
        initial += ' '.join(fi)
        stats.append(initial)

    filename = 'index' + str(fileno) + '.txt'

    fname = os.path.join(inverted_index_dir, filename)
    with open(fname, 'w') as f:
        f.write('\n'.join(stats))
    inv_ind_total -= len(imap)

    fname = invertedindex_stat
    with open(fname, 'w') as f:
        f.write(str(tokens_total)+'\n')
        f.write(str(inv_ind_total))

    stats = []
    statOffset = []

    for k in sorted(titleID):
        initial = str(k) + ' ' + titleID[k].strip()
        stats.append(initial)
        statOffset.append(str(prevoff))
        prevoff += len(initial) + 1

    with open('./inverted_index/title.txt', 'a') as f:
        var = '\n'.join(stats)
        f.write(var)
        f.write('\n')

    with open('./inverted_index/titleOffset.txt', 'a') as f:
        var = '\n'.join(statOffset)
        f.write(var)
        f.write('\n')

    return prevoff


# In[5]:




# In[6]:


class Index():
    def __init__(self, refs, extlink, cat, body, info, title):
        self.title = title
        self.refs = refs
        self.extlink = extlink
        self.prevOff = 0
        self.nextOff = []
        self.cat = cat
        self.body = body
        self.info = info

    def MakingDicts(self):
        total = ddic(int)

        title = ddic(int)
        for i in range(len(self.title)):
            title[self.title[i]] += 1
            total[self.title[i]] += 1

        refs = ddic(int)
        for i in range(len(self.refs)):
            refs[self.refs[i]] += 1
            total[self.refs[i]] += 1

        extlink = ddic(int)
        for i in range(len(self.extlink)):
            extlink[self.extlink[i]] += 1
            total[self.extlink[i]] += 1

        cat = ddic(int)
        for i in range(len(self.cat)):
            cat[self.cat[i]] += 1
            total[self.cat[i]] += 1

        body = ddic(int)
        for i in range(len(self.body)):
            body[self.body[i]] += 1
            total[self.body[i]] += 1

        info = ddic(int)
        for i in range(len(self.info)):
            info[self.info[i]] += 1
            total[self.info[i]] += 1
        return (total, refs, extlink, cat, body, info, title)

    def IndexMapping(
            self, total, refs, extlink, cat, body, info, title, pageno, iMap):

        for word in total.keys():
            initial = 'D' + str(pageno)
            if refs[word] > 0:
                initial += 'r' + str(refs[word])
            if extlink[word] > 0:
                initial += 'l' + str(extlink[word])
            if cat[word] > 0:
                initial += 'c' + str(cat[word])
            if body[word] > 0:
                initial += 'b' + str(body[word])
            if info[word] > 0:
                initial += 'i' + str(info[word])
            if title[word] > 0:
                initial += 't' + str(title[word])

            iMap[word].append(initial)
        return iMap

    def InitIndex(self, pageno, iMap):

        (total, refs, extlink, cat, body, info, title) = self.MakingDicts()
        iMap = self.IndexMapping(total, refs, extlink,
                                 cat, body, info, title, pageno, iMap)

        return iMap, pageno


# In[7]:


class RegexExp():
    def __init__(self):
        pass

    def findUsefulText(self, info):
        stats = info.split('\n')
        refs = []
        extlinks = []
        cat = []
        for l in stats:
            if re.search(r'<ref', l):
                x = re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', l)
                refs.append(x)
            if re.search(r'\[\[category', l):
                x = re.sub(r'\[\[category:(.*)\]\]', r'\1', l)
                cat.append(x)
            if re.match(r'\*[\ ]*\[', l):
                extlinks.append(l)

        return (refs, extlinks, cat)

    def findUsefulInfo(self, info):
        stats = info.split('\n')
        i = []
        flag = 0

        for l in stats:
            if re.match(r'\{\{infobox', l):
                flag = 1
                x = re.sub(r'\{\{infobox(.*)', r'\1', l)
                i.append(x)
            elif flag == 1:
                if l == '}}':
                    flag = 0
                    continue
                i.append(l)
        empty = []
        stats = cleanupText(' '.join(i))
        return stats

    def textHandling(self, ID, text, title):
        text = text.lower()
        cleaned_text = text.split('==references==')
        one = 1
#         print(data)
        if len(cleaned_text) == one:
            cleaned_text = text.split('== references== ')
        if len(cleaned_text) == one:
            refs = []
            extlink = []
            cat = []
        else:
            useful = cleaned_text[1]
            (refs, extlink, cat) = self.findUsefulText(useful)
            refs = cleanupText(' '.join(refs))
            extlink = cleanupText(' '.join(extlink))
            cat = cleanupText(' '.join(cat))
        title = title.lower()
        title = cleanupText(title)
        useful = cleaned_text[0]
        info = self.findUsefulInfo(useful)
        stats = re.sub(r'\{\{.*\}\}', r' ', useful)
        body = cleanupText(stats)

        return (refs, extlink, cat, body, info, title)


# In[8]:


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.text = ""
        self.pageNo = 0
        self.iMap = ddic(list)
        self.fileNo = 0
        self.CurrentData = ''
        self.title = ''
        self.flag = 0
        self.ID = ''

    def startElement(self, tag, attributes):
        self.CurrentData = tag

    def endElement(self, tag):
        if self.CurrentData == 'title':
            pass
#             print(self.title)
        elif self.CurrentData == 'text':
            pass
#             print(self.text)

        if tag == 'page':
            reg = RegexExp()
            global fileNo, pageNo, iMap, offset, titleID
            refs, extlink, cat, body, info, title = reg.textHandling(
                self.ID, self.text, self.title)
            indexer = Index(refs, extlink, cat, body, info, title)
            self.iMap, self.pageNo = indexer.InitIndex(self.pageNo, self.iMap)
            titleID[self.pageNo] = self.title.strip().encode(
                "ascii", errors="ignore").decode()
            self.pageNo += 1
            if self.pageNo % 10000 == 0:
                offset = writeFile(self.pageNo, self.iMap, self.fileNo, offset)
                self.iMap = ddic(list)
                titleID = {}
                self.fileNo += 1

            global fileNo

            fileNo = self.fileNo
            pageNo = self.pageNo
            iMap = self.iMap

            self.CurrentData = ''
            self.title = ''
            self.ID = ''
            self.flag = 0
            self.text = ''

    def characters(self, content):
        if self.CurrentData == 'title':
            self.title = self.title + content
        elif self.CurrentData == 'text':
            self.text = self.text + content
        elif self.CurrentData == 'id' and self.flag == 0:
            self.ID = content
            self.flag = 1


# In[10]:

if __name__ == '__main__':
    wiki_dump = "IRE/"
    global inverted_index_dir, invertedindex_stat
    # global fileNo

    filenames = glob.glob(wiki_dump + '*')

    inverted_index_dir = "./inverted_index"
    invertedindex_stat = "inverted_index_stat"

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = XMLHandler()
    parser.setContentHandler(handler)
    for fname in filenames:
        parser.parse(fname)

    with open("./inverted_index/fileNumbers.txt","w") as f:
        f.write(str(handler.pageNo))
    writeFile(pageNo, iMap, fileNo, offset)
    fileNo += 1
    indexMerge(fileNo)
