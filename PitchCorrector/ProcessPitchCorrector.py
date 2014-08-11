'''
Created on 09/06/2014

@author: victor
'''

from music21 import converter

from Music21OMR import correctors
from music21 import stream
from music21 import note
from music21 import bar
from music21 import key
from MultipleOMR_S1.AlignmentArrays import AlignmentArrays
from MultipleOMR_S1.Music21Functions import Music21Functions


class ProcessPitchCorrector:
    myAlignment=AlignmentArrays()
    m21F=Music21Functions()   

    def convertFilesToMusic21(self,omrFiles):
        OMRs=[]
        for f in omrFiles:  
            OMRs.append(converter.parse(f))
        return OMRs
    def getHashFromOMRs(self,omrFiles):
        hashArrayOMRs=[]
        OMRs=self.convertFilesToMusic21(omrFiles)
        for omr in OMRs:
            hashArrayOMRs.append(self.m21F.getHashArrayFromPart(omr.parts[0]))
        return  hashArrayOMRs   
       
    def alignHashResultWithOMR(self,hashArrayResult,hashArrayOMRs):
        hashOrdered=[]
        hashOrderedOMR=[]
        hashOrdered.append(hashArrayResult)
        for hashArrayOMR in hashArrayOMRs:
            hashOrdered,s=self.myAlignment.needleman_wunsch(hashOrdered[0], hashArrayOMR)
            hashOrderedOMR.append(hashOrdered[1])
        
        return hashOrdered[0],hashOrderedOMR
        
    def reconstructScores(self,OMRs,hashParts):
        m21F=Music21Functions()
        s=stream.Stream()
        for i in range(len(hashParts)):
            rec=m21F.reconstructScore(OMRs[i].parts[0], hashParts[i])
            s.append(rec)
            

        return s
            
    
    def votePitch(self,omrJoinedParts):
        
        s=stream.Stream()
        measures=omrJoinedParts[0].getElementsByClass(stream.Measure)
#         myKey=omrJoinedParts[0].getKeySignatures()
        s=stream.Stream()
#         s.append(myKey)
        for indexBar in range(len(measures)):
            myBar=measures[indexBar].notesAndRests
            m=stream.Measure()
            m.append(measures[indexBar])
            m=m.flat
            m.removeByClass('GeneralNote')
            for indexNote in range(len(myBar)):
                myNote=myBar[indexNote]
                newNote=self.getVoteNote(omrJoinedParts,myNote,indexBar,indexNote)
                m.append(newNote)
            s.append(m)
        m21F=Music21Functions()
        sOutFiltered=m21F.filterExtraMeasuresWithoutParts(s)
        return sOutFiltered     
        
    def getNote(self,omrJoinedParts,indexPart,indexBar,indexNote): 
        try:
            bar=omrJoinedParts[indexPart].getElementsByClass(stream.Measure)[indexBar]
            notes=bar.notesAndRests
            n=notes[indexNote] 
            return n
        except:
            return None
         
     
    def getVoteNote(self,omrJoinedParts,myNote,indexBar,indexNote):
        percentageScore=[]
        numOMR=len(omrJoinedParts)-1
        for i in range(numOMR):
            score=0
            for j in range(numOMR):
                nVote=self.getNote(omrJoinedParts,i+1,indexBar,indexNote)
                nCompare=self.getNote(omrJoinedParts,j+1,indexBar,indexNote)
                if nVote==nCompare:
                    score=score+1.0
            percentageScore.append(score/numOMR)
        indexMax=percentageScore.index(max(percentageScore))
        valueMax=max(percentageScore)
        noteVoted=self.getNote(omrJoinedParts,indexMax+1,indexBar,indexNote)
        noteDefault=self.getNote(omrJoinedParts,0,indexBar,indexNote)
#         print noteDefault,noteVoted,valueMax

        if noteVoted==None:
            return noteDefault
        if noteVoted.quarterLength!=noteDefault.quarterLength:
            return noteDefault
        if valueMax>=0.5:
            return noteVoted
        
        return noteDefault
