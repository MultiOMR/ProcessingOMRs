'''
Created on 09/06/2014

@author: victor
'''
from AlignmentArrays import AlignmentArrays
from music21 import converter
from Music21Functions import Music21Functions
from Music21OMR import correctors
from music21 import stream
from music21 import meter

class ProcessOMR:
        
    def align(self,OMR):
        hashArray=[]
        myAlignment=AlignmentArrays()
        m21F=Music21Functions()
        
        print "...Obtaining Hash of measures..."
        for i in range(len(OMR)):
            hashArray.append(m21F.getHashArrayFromPart(OMR[i].parts[0]))
            print hashArray[i]
        
        
        hashOrdered,s=myAlignment.needleman_wunsch(hashArray[0], hashArray[1])
        
        print "...reconstruct the scores..."
        streams=[]
        for i in range(len(OMR)):
            partReconstruct=m21F.reconstructScore(OMR[i].parts[0], hashOrdered[i])
            sc=stream.Score()
            sc.append(partReconstruct)
            streams.append(sc)
        return streams
    
    def vote(self,OMR):
        incorrectMeasures=[]
        for omr in OMR:
            im=self.flagIncorrectMeasures(omr)[0]
            incorrectMeasures.append(im)
            
        print incorrectMeasures
        m21F=Music21Functions()
        if len(incorrectMeasures[0])<len(incorrectMeasures[1]):
            betterOMR=0
            worstOMR=1
        else:
            betterOMR=1
            worstOMR=0
        print "better="+str(betterOMR)
        
        
        sOutStream=stream.Score()
        sOut=stream.Part()

        for barNumber in range(len(OMR[betterOMR].parts[0].getElementsByClass(stream.Measure))):
            myBarBetter=OMR[betterOMR].parts[0].getElementsByClass(stream.Measure)[barNumber]
            myBarWorst=OMR[worstOMR].parts[0].getElementsByClass(stream.Measure)[barNumber]
            try:
                if (barNumber) in incorrectMeasures[betterOMR]:
                    sOut.append(myBarWorst)
                else:
                    sOut.append(myBarBetter)
            except:
                print "error vote bar:"+str(barNumber)
#         slurs=m21F.getSlurs(OMR[betterOMR].parts[0])
#         sOut.append(slurs)

        sOutStream.append(sOut)
        sOutFiltered=m21F.filterExtraMeasures(sOutStream)
    
        return sOutFiltered 
    def flagIncorrectMeasures(self,omr):
        m21F=Music21Functions()
        sc=correctors.ScoreCorrector(omr)
        part=sc.getSinglePart(0)
         
        im=[]
        arrErrors=[]
        im=part.getIncorrectMeasureIndices(runFast=False)
        
        im1= m21F.getIncorrectMeasureIndices(omr)
        
        im2= m21F.getPossibleBeamsErrors(omr)
        im3= m21F.getPossibleLastNoteErrors(omr)
       
         
        arrErrors.append(im)
        arrErrors.append(im1)
        arrErrors.append(im2)
        arrErrors.append(im3)
         
        if(len(im)>15):
            if(len(im1)<len(im)):
                im=im1
        imSum=list(set(im)|set(im2)|set(im3))
        imSum=sorted(imSum)
        imOK=m21F.correctIncorrectMeasuresArray(omr,imSum)  
        
        return imOK,arrErrors
      
        
    def order(self,omr_files):
        OMR=[]
        OMR_out=[]
        IM=[]
        lenIM=[]
        
        for f in omr_files:
            OMR.append(converter.parse(f))
        for omr in OMR:
            im=self.flagIncorrectMeasures(omr)[0]
            IM.append(im)
            lenIM.append(len(im))

        for i in range(len(OMR)):
            indexBetter=lenIM.index( min(lenIM))
            OMR_out.append(OMR[indexBetter])
            print indexBetter
            OMR.pop(indexBetter)
            lenIM.pop(indexBetter)

        return OMR_out
            
        


