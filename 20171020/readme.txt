There are two files one for indexing and one for searching.

The indexer.py does not take any arguments as it was not mentioned in the Phase 2 doc. 
It will work on xml files stored in the IRE directory. IRE directory should be in the same directory as indexer.py. There should exist an empty directory named inverted_index to successfully run the program in the same directory as indexer.py

stats.txt was created manually.

The number of files in which index is stored is dynamic and changes as the number of token increases.

2 files keep track of titles and it's offset and one file keeps track of the overall vocabulary. All tokens are are sorted in files which are responsible for field querying.
