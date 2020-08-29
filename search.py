import nltk
import sys 
import re
import os
from Stemmer import Stemmer
from nltk.corpus import stopwords
from textHandling import cleanupText

stemmer = Stemmer('english')
stop_words = set(stopwords.words('english'))

def binarySearch(L, target):
    start = 0
    end = len(L) - 1

    while start <= end:
        middle = int((start + end)/ 2)
        midpoint = L[middle]
        if midpoint > target:
            end = middle - 1
        elif midpoint < target:
            start = middle + 1
        else:
            return middle
    return -1

def field_query(query,words,indices):
    global stemmer
    global stop_words

    text = re.findall(r'[b|i|t|c|r|l]:([^:]*)(?!\S)',query)
    fields = re.findall(r'[b|i|t|c|r|l]:',query)
    fields = [re.sub(r':',r'',field) for field in fields]

    text = [i.lower() for i in text]

    full_fields = {'t':'title','b':'body','l':'links','r':'references','i':'infobox','c':'category'}


    for i,field in enumerate(fields):
        searchTerm = text[i].split(' ')
        print(full_fields[field])

        if len(searchTerm) == 1:
            print(searchTerm[0],end='\t')
            if searchTerm[0] in stop_words:
                continue
            searchTerm = stemmer.stemWord(searchTerm[0])
            if len(searchTerm) == 0:
                continue

            index = binarySearch(words,searchTerm)
            if index == -1:
                continue
            x = indices[index][0]
            for tokens in x.split(' '): 
                if field == 'b':
                    # print(tokens)
                    y = re.findall('b',tokens)
                    if y:
                        print(tokens,end=' ')
                elif field == 'i':
                    # print(tokens)
                    y = re.findall('i',tokens)
                    if y:
                        print(tokens,end=' ')
                elif field == 't':
                    # print(tokens)
                    y = re.findall('t',tokens)
                    if y:
                        print(tokens,end=' ')
                elif field == 'c':
                    # print(tokens)
                    y = re.findall('c',tokens)
                    if y:
                        print(tokens,end=' ')
                elif field == 'r':
                    # print(tokens)
                    y = re.findall('r',tokens)
                    if y:
                        print(tokens,end=' ')
                elif field == 'l':
                    # print(tokens)
                    y = re.findall('l',tokens)
                    if y:
                        print(tokens,end=' ')
        elif len(searchTerm) > 1:
            terms = cleanupText(' '.join(searchTerm))
            for searchTerm in terms:
                index = binarySearch(words,searchTerm)
                if index == -1:
                    continue
                print(searchTerm,end='\t')
                x = indices[index][0]
                for tokens in x.split(' '): 
                    if field == 'b':
                        # print(tokens)
                        y = re.findall('b',tokens)
                        if y:
                            print(tokens,end=' ')
                    elif field == 'i':
                        # print(tokens)
                        y = re.findall('i',tokens)
                        if y:
                            print(tokens,end=' ')
                    elif field == 't':
                        # print(tokens)
                        y = re.findall('t',tokens)
                        if y:
                            print(tokens,end=' ')
                    elif field == 'c':
                        # print(tokens)
                        y = re.findall('c',tokens)
                        if y:
                            print(tokens,end=' ')
                    elif field == 'r':
                        # print(tokens)
                        y = re.findall('r',tokens)
                        if y:
                            print(tokens,end=' ')
                    elif field == 'l':
                        # print(tokens)
                        y = re.findall('l',tokens)
                        if y:
                            print(tokens,end=' ')
                print('\n')



def plain_query(query,words,indices):
    global stop_words
    global stemmer

    searchTerm = query.split(' ')
    if len(searchTerm) == 0:
        print('No Query Given')
    elif len(searchTerm) == 1:
        if searchTerm[0] in stop_words:
            return
        searchTerm[0] = searchTerm[0].lower()
        searchTerm = stemmer.stemWord(searchTerm[0])
        if len(searchTerm) == 0:
            return
        index = binarySearch(words,searchTerm)
        print(searchTerm,end='\t')
        x = indices[index][0]
        print(x)
    elif len(searchTerm) > 1:
        terms = cleanupText(' '.join(searchTerm))
        for searchTerm in terms:
            index = binarySearch(words,searchTerm)
            if index == -1:
                continue
            print(searchTerm,end='\t')
            x = indices[index][0]
            print(x)





def main():
    query = sys.argv[2]
    words = []
    indices = []
    print("Loading Files")
    with open(os.path.join(sys.argv[1],'index0.txt'),'r') as file:
        for line in file:
            try:
                words.append(line.split(None,1)[0])
                indices.append(line.split(None,1)[1:])
            except IndexError:
                pass
    print('Querying Started')
    print('\n\n\n')
    if re.match('[b|i|t|c|r|l]:',query):
        field_query(query,words,indices)
    else:
        plain_query(query,words,indices)

if __name__ == '__main__':
    main()    