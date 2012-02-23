#!/usr/bin/env python
import math
import re
import milk # http://packages.python.org/milk

#XXX look into a tree hash for storing unique user code

class Dataset(object):


   def __init__(self):
      self.allwords = dict()
      self.sortedwords = list()
      self.makefeatures = False
      self.documents = list()
      self.idf = dict()

   def add(self, string):
      tokens = map(lambda item: item.lower(), re.findall(r"\w+", string))
      for token in tokens:
         self.allwords[token] = self.allwords.setdefault(token, 0) + 1

   def computeidf(self):
      documentslen = len(self.documents)
      for key, value in self.allwords.iteritems():
         for vector in self.documents:
            if key in vector:
               self.idf[key] = self.idf.setdefault(key, 0) + 1
         self.idf[key] = math.log(documentslen / float(1 + self.idf.setdefault(key, 0))) #XXX fix this, shouldnt have to use default dict
      
   def featurevector(self, string):
      if self.makefeatures == False:
         self.sortedwords = self.allwords.keys()
         self.sortedwords.sort()
         self.computeidf()
         self.makefeatures = True
      tokens = map(lambda item: item.lower(), re.findall(r"\w+", string))
      features = list()
      for word in self.sortedwords:
         tf = tokens.count(word)
         features.append(tf * self.idf[word]) # tf*idf score
      return features

   def populate(self, arr):
      self.documents = arr[:]
      for row in arr:
         self.add(row)
      features = list()
      for row in arr:
         features.append(self.featurevector(row))
      return features

def main():
   """
   currently using kmeans to cluster the data, need to be able to find k as the data gathered will be dynamic
   maybe only calculate on batch time

   also, look into using EM instead of kmeans
   """
   filename = 'data'
   fd = open(filename, 'r')
   questions = [line.strip() for line in fd]
   fd.close()
   
   data = Dataset()
   features = data.populate(questions)
   k = 2
   cluster_ids, centroids = milk.kmeans(features, k) #using unigrams successfully classifies every question
   print cluster_ids
   while True:
      raw = raw_input('ask a question?')
      if raw == 'x' or raw == 'q': break
      if raw == '': continue
      f = data.featurevector(raw) #wont update the data used initially to find unigrams
      query = features + [f]
      cluster_ids, centroids = milk.kmeans(query, k + 1)
      print '***** did you mean ******'
      results = filter(lambda zipped: zipped[0] == cluster_ids[-1], zip(cluster_ids[:-1], questions))
      if len(results) == 0:
         print '** no similar questions have been asked **'
      for index, result in results[:5]:
         print result
      print '*************************'

if __name__ == '__main__':
   main()
