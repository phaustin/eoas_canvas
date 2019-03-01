import numpy as np

def calcboundaries(score):
   """  
    90-100     A+ exceptional
    85-90     A exceptional
    80-84     A- exceptional
    76-79     B+ competent
    72-75     B competent
    68-71     B- competent
    64-67     C+ adequate
    60-63     C adequate
    55-59     C- adequate
    50-54     D adequate
    00-49     F* inadequate
   """
   bounds={'a+':90,'a':85,'a-':80,'b+':76,'b':72,'b-':68,'c+':64,'c':60,'c-':55,'d':50}
   letters=['a+','a','a-','b+','b','b-','c+','c','c-','d']
   print("boundaries for a score of %d" % score)
   for letter in letters:
       thescore=bounds[letter]/100.*score
       minus=score - thescore
       print("%-5s: %5.2f  %5.2f" % (letter,bounds[letter]/100.*score,minus))

def assignGrade(score):
   score=np.round(score/100.,decimals=2)*100.
   print("theScore: ",score)
   invertBound={90:'a',85:'a-',80:'b+',76:'b',72:'b-',68:'c+',64:'c',60:'c-',55:'d',50:'f'}
   if score > 100:
      raise Exception('score > 100: score is %6.2f' % score)
   if score >= 90:
      return 'a+'
   theGrades=invertBound.keys()
   theGrades.sort()
   for grade in theGrades:
      if grade > score:
         return invertBound[grade]
   raise Exception("shouldn't reach here: score is %6.2f" % score)

def markLimits(markTotal):
   bounds={'a+':90,'a':85,'a-':80,'b+':76,'b':72,'b-':68,'c+':64,'c':60,'c-':55,'d':50}
   inverted_bounds = dict([[v,k] for k,v in bounds.items()])         
   theKeys=inverted_bounds.keys()
   theKeys.sort()
   charGrade=[]
   for key in theKeys:
      charGrade.append(inverted_bounds[key])
   theKeys=np.array(theKeys)
   charGrade=np.array(charGrade)
   numGrade=np.array(theKeys)
   problemGrade=np.round(numGrade/100.*markTotal,decimals=1)
   numberMinus=problemGrade - markTotal
   problemGrade=['%4.1f' % item for item in problemGrade]
   numberMinus=['%4.1f' % item for item in numberMinus]
   problemGrade=np.array(problemGrade)
   numberMinus=np.array(numberMinus)
   theOut=np.rec.fromarrays([charGrade,numGrade,problemGrade,numberMinus],names=['letter','value','problem','minus'])
   return theOut

if __name__=="__main__":
    score=17
    out=markLimits(score)
    for item in out:
       print(item)
