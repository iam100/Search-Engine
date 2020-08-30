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


# In[4]:


def writeFile(pageno, imap, fileno, titleoffset):

    global titleID
    global inverted_index_dir
    global invertedindex_stat
    global tokens_total

    inv_ind_total = 0

    stats = []
    for k in sorted(imap):
        initial = k + ' '
        fi = imap[k]
        inv_ind_total += len(fi)
        initial += ' '.join(fi)
        stats.append(initial)
    fname = os.path.join(inverted_index_dir, 'index.txt')
    with open(fname, 'w') as f:
        f.write('\n'.join(stats))
    inv_ind_total -= len(imap)

    fname = invertedindex_stat
    with open(fname, 'w') as f:
        f.write(str(tokens_total)+'\n')
        f.write(str(inv_ind_total))


# In[5]:


def cleanupText(stats):
    global stop_words
    global stemmer
    global tokens_total

    stats = stats.encode("ascii", errors="ignore").decode()
    stats = re.sub(r'http[^\ ]*\ ', r' ', stats)
    stats = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', stats)
    stats = re.sub(
        r'\`|\~|\!|\@|\#|\"|\'|\$|\%|\^|\&|\*|\(|\)|\-|\_|\=|\+|\\|\||\]|\[|\}|\{|\;|\:|\/|\?|\.|\>|\,|\<|\'|\n|\||\|\/"', r' ', stats)
    stats = stats.split()
    tokens_total += len(stats)
    stats = [i for i in stats if not i in stop_words]
    stats = stemmer.stemWords(stats)
    return stats


# In[6]:


class Index():
    def __init__(self, refs, extlink, cat, body, info, title):
        self.title = title
        self.refs = refs
        self.extlink = extlink
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

    def IndexMapping(self, total, refs, extlink, cat, body, info, title, pageno, iMap):

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
            if re.search(r'ref', l):
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
                x = re.sub('\{\{infobox(.*)', r'\1', l)
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
#         print(data)
        if len(cleaned_text) == 1:
            cleaned_text = text.split('== references== ')
        if len(cleaned_text) == 1:
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
            self.pageNo += 1
            reg = RegexExp()
            refs, extlink, cat, body, info, title = reg.textHandling(
                self.ID, self.text, self.title)
            indexer = Index(refs, extlink, cat, body, info, title)
            self.iMap, self.pageNo = indexer.InitIndex(self.pageNo, self.iMap)

            global fileNo, pageNo, iMap, offset, titleID
            titleID[self.pageNo] = self.title.strip().encode(
                "ascii", errors="ignore").decode()

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
            self.title += content
        elif self.CurrentData == 'text':
            self.text += content
        elif self.CurrentData == 'id' and self.flag == 0:
            self.ID = content
            self.flag = 1


# In[9]:




# In[10]:

if __name__ == '__main__':
    wiki_dump = sys.argv[1]
    global inverted_index_dir, invertedindex_stat

    inverted_index_dir = sys.argv[2]
    invertedindex_stat = sys.argv[3]

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = XMLHandler()
    parser.setContentHandler(handler)
    parser.parse(wiki_dump)

    

    writeFile(pageNo, iMap, fileNo, offset)
