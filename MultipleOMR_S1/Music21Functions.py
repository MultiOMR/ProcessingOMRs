'''
Created on 02/06/2014

@author: Victor Padilla
@project: Multiple OMR Lancaster University


Functions to manipulate sequences of music in Music21
'''
import os
from music21 import stream
from music21 import spanner
from Music21OMR import correctors
from music21 import note
from music21 import meter
from music21 import beam
class Music21Functions:

    def getStringNotesFromBar(self,mybar):
        '''
        return the string of pitches of a measure given a bar
        '''
        strOut=""
        for thisNote in mybar.notes:
            if(thisNote.isNote):
                strOut+=thisNote.pitch.name
            elif(thisNote.isChord):
                strOut+=thisNote[0].pitch.name
            else:
                print("unknown")
          
        return str
    
    def getStringBar(self,Multiple_OMR,barNumber):
        '''
        return the string of pitches of the same measure in a Multiple OMR slice
        '''
        i=0        
        strBar=["","",""]
        for OMR in Multiple_OMR:
            mybar=OMR.parts[0].measure(barNumber)
            strBar[i]=self.getStringNotesFromBar(mybar)
            i+=1
        return strBar
    
    def getSingleStringBar(self,OMR,barNumber):
        '''
        return the string of pitches of a measure given the score in Music21 Format and bar number
        '''
        strBar=""
        try:
            mybar=OMR.parts[0].measure(barNumber)
            strBar=self.getStringNotesFromBar(mybar)
        except:
            print ("Error bar:"+str(barNumber))
        return strBar
     
    def getWholeNoteString(self,OMR):
        strOut=""
        for i in range(len(OMR.parts[0])):
            strOut+=self.getSingleStringBar(OMR,i+1)
            strOut+="|"
        return strOut
    
    def getDuration(self,bar):
        duration=0
        try:
            for event in bar:
                try:
                    if(event.isNote):
                        duration+=event.duration.quarterLength
                    if(event.isRest):
                        duration+=event.duration.quarterLength
                except:
                    a=0 
        except:
            a=0
        return str(duration)
    
    def getWholeDurations(self,OMR):
        strOut=""
        for i in range(len(OMR.parts[0])):
            bar=OMR.parts[0].measure(i+1)
            strOut+=self.getDuration(bar)
            strOut+="|"
        return strOut
    
    def getHashArrayFromPart(self,part):
        '''
        get Hash string of a Part (music21)
        '''
        hashArray=[]
        lengthArray=len(part.measureOffsetMap())
        for i in range(lengthArray):
#             measure=part.measure(i+1)
            measure=part.getElementsByClass(stream.Measure)[i]
            hashMeasure=self.getHashFromMeasure(measure)
            hashArray.append(hashMeasure)
        return hashArray
    
    def getHashFromMeasure(self,measure):
        '''
        get Hash string of a measure. Library correctors.py of Michael Scott Cuthbert. Project OMR
        '''
        mh=correctors.MeasureHash(measure).getHashString()
        return mh
    def getSlurs(self,part):
        slurs=part.flat.getElementsByClass(spanner.Spanner)
        return slurs
        
    def reconstructScore(self,part,hashPart): 
        partReconstructed=stream.Part()
        barNumber=1
        for i in range(len(hashPart)): 
            if hashPart[i]!="*":
                m=part.getElementsByClass(stream.Measure)[barNumber-1]
                partReconstructed.append(m)
                barNumber+=1
            else:
                m=stream.Measure()
                partReconstructed.append(m)
        slurs=self.getSlurs(part)   
        partReconstructed.append(slurs)  
        myStream=self.reorderMeasures(partReconstructed)  
        return myStream
    
    def reorderMeasures(self,omr):
        slurs=self.getSlurs(omr) 
        s=stream.Part()
        barNumber=1
        for measure in omr.getElementsByClass(stream.Measure):
            measure.number=barNumber
            s.append(measure)
            barNumber+=1
        s.append(slurs)
        return s              
            

        
    def recombineBars(self,bar1,bar2):
        '''
        Not implemented yet
        '''
        s=stream.Stream()
        
        for element in bar1:
                s.append(element)
        for element in bar2:
                s.append(element)
        s=s.notesAndRests
        return s
    
    def correctIncorrectMeasuresArray(self,omr,incorrectMeasures):
        measures=omr.parts[0].getElementsByClass(stream.Measure)
        if 0 in incorrectMeasures:
            incorrectMeasures.remove(0)#Anacrusis
            
        for barNumber in incorrectMeasures:
            if barNumber<len(measures)-1:
                measure=measures[barNumber]
                measureNext=measures[barNumber+1]
                duration=self.getDuration(measure)
                
                if(float(duration)<=0):
                    incorrectMeasures.remove(barNumber)
                    self.correctIncorrectMeasuresArray(omr,incorrectMeasures)
                    
                if(measureNext!=None):
                    durationNext=self.getDuration(measureNext)
                    if(float(duration)+float(durationNext)==4):
                        try:
                            incorrectMeasures.remove(barNumber)
                            incorrectMeasures.remove(barNumber+1)
                        except:
#                             print "error correctIncorrectmeasures bar:"+str(barNumber)
                            a=1
                        self.correctIncorrectMeasuresArray(omr,incorrectMeasures)
        return incorrectMeasures
    
    
    def filterExtraMeasures(self,omr):
        sco=stream.Score()
        s=stream.Part()
#         if isinstance(omr,stream.Stream):
#             score=stream.Score()
#             score.append(omr)
#             omr=score
#             omr.show('text')
        slurs=self.getSlurs(omr.parts[0])
        for measure in omr.parts[0].getElementsByClass(stream.Measure):
            if measure.duration.quarterLength>0:
                s.append(measure)
        s.append(slurs)
        sco.append(s)
        return sco
    def filterExtraMeasuresWithoutParts(self,omr):
        sco=stream.Score()
        s=stream.Part()

        for measure in omr.getElementsByClass(stream.Measure):
            if measure.duration.quarterLength>0:
                s.append(measure)
        sco.append(s)
        return sco
    
    
    def getIncorrectMeasureIndices(self,omr):
        arrChunks= self.getTransitions(omr)
        measures=omr.parts[0].getElementsByClass(stream.Measure)
        indexBar=0
        FlagErrors=[]
        barFrom=0
        barTo=0
        for chunk in arrChunks:
            indexC=arrChunks.index(chunk)
            chunkBefore=arrChunks[indexC-1]
            if(indexC==0):
                barFrom=0
            else:
                barFrom+=chunkBefore[1]  
            barTo=chunk[1]+barFrom       
            chunkMeasures=measures[barFrom:barTo]
            quarterChunk=round(chunk[0]/2)
            for measure in chunkMeasures:              
                if measure.duration.quarterLength!=quarterChunk:
                    FlagErrors.append(indexBar)
                indexBar+=1
        return FlagErrors
    
    def filterTransitions(self,arrMeasureIndex):
        arrMeasureIndex2=[]
        arrMeasureIndex.insert(0,0)
        arrMeasureIndex.append(-1) 
        for mes in arrMeasureIndex:
            indexM=arrMeasureIndex.index(mes)
            if indexM>0:
                bars=arrMeasureIndex[indexM]-arrMeasureIndex[indexM-1]
                if (bars>9):
                    arrMeasureIndex2.append(mes)
        arrMeasureIndex2.insert(0,0)
        arrMeasureIndex2.append(-1) 
        return arrMeasureIndex2
   
    def getTransitions(self,omr):
        MeasuresLength=[]
        arrMeasureIndex_before=self.getTransitionBar(omr)
        
        arrMeasureIndex=self.filterTransitions(arrMeasureIndex_before)
        for i in range(len(arrMeasureIndex)-1):
            arrMeasureslength= self.getAverageQuavers(omr,arrMeasureIndex[i],arrMeasureIndex[i+1],False)
            MeasuresLength.append(arrMeasureslength)

        return MeasuresLength
        
    def getTransitionBar(self,omr):
        arrOut=[]
        measures=omr.parts[0].getElementsByClass(stream.Measure)
        barsNumber=len(measures)
        for barIndex in range(5,barsNumber):
            averageBefore=self.getAverageQuavers(omr,barIndex-4,barIndex,isUntilTS=False)
            averageAfter=self.getAverageQuavers(omr,barIndex,barIndex+2,isUntilTS=False)
            if(abs(averageBefore[0]-averageAfter[0])>1.5):
                if(measures[barIndex].duration.quarterLength<averageBefore[0]*2):#rest bars or missing bars
                    arrOut.append(barIndex)
        return arrOut
        
    def getAverageQuavers(self,myStream,measureIndex,measureIndexEnd,isUntilTS):
        quavers=0
        barNumbers=0
        averageQuavers=0
        measures=myStream.parts[0].getElementsByClass(stream.Measure)
        for bar in measures[measureIndex:measureIndexEnd]:
            duration=bar.duration.quarterLength*2
            barNumbers+=1
            if(duration>0 and duration<10):
                quavers+=duration
                if isUntilTS:
                    if (len(bar.getElementsByClass(meter.TimeSignature))>0):
                        break
        if barNumbers>0:   
            averageQuavers=quavers/barNumbers
        return averageQuavers,barNumbers
    
#**************************************************
    def getPossibleBeamsErrors(self,omr):   
        arrErrors=[] 
        measures=omr.parts[0].getElementsByClass(stream.Measure)
        barsNumber=len(measures)
        for i in range(barsNumber):
            notes=measures[i].getElementsByClass(note.Note)
            count=0
            state=0
            for n in notes:
                if n.duration.quarterLength==0.25:
                    bs=n.beams.getNumbers() 
                    if(len(bs)>0):
                        b=n.beams.getByNumber(bs[0])          
                        if b.type=='start':
                            count=1
                            state=1
                        if b.type=='continue':
                            if(state==1 or state==2):
                                count+=1
                                state=2
                        if b.type=='stop':
                            if(state==1 or state==2):
                                count+=1
                                if count==3:
                                    arrErrors.append(i)
        arrErrors=list(set(arrErrors))
        return arrErrors

    def getPossibleLastNoteErrors(self,omr):   
        arrErrors=[] 
        measures=omr.parts[0].getElementsByClass(stream.Measure)
        barsNumber=len(measures)
        for i in range(barsNumber):
            notes=measures[i].getElementsByClass(note.GeneralNote)
            if(len(notes)>0):
                lastNote=notes[len(notes)-1]
                if lastNote.duration.quarterLength<=0.25:
                    if(lastNote.isRest):
                        arrErrors.append(i)
                    else:
                        bs=lastNote.beams.getNumbers() 
                        
                        if(len(bs)==0):
                            if(len(notes)>2):
                                noteBefore=notes[len(notes)-2]
                                if noteBefore.duration.quarterLength+lastNote.duration.quarterLength!=1:
                                    arrErrors.append(i)
               
            
        return arrErrors
    
    
    
    
    
    
    
    
    
    
    
    def writeAlignmentMAFFT(self,sequences):
        '''
        multi-alignment of strings using mafft.bat
        http://mafft.cbrc.jp/alignment/software/
        input file:     input.txt
        output file:    output.txt
        '''
        f=open("input.txt","w")
        for seq in sequences:
            f.write(">\n")
            f.write(seq+"\n")
        f.close()
        os.system("mafft.bat --localpair --text --out output.txt input.txt")
        fOut=open("output.txt","r")
        fOut2=open("outputLine.txt","w")
        for line in fOut:
            line=line.strip("\n")
            if(line==">"):
                fOut2.write("\n")
            else:
                fOut2.write(line) 
                
        fOut.close()
        fOut2.close()
             
                
        
        
        
            