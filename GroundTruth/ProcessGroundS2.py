

'''
Created on 13/06/2014

@author: victor
'''

from MultipleOMR.PipelineAlignment import PipelineAlignment


class ProcessGroundS2:
    
    
    def getSimilarity(self,omr_files):
        pa=PipelineAlignment()
        omr_symbolsAlign=pa.align(omr_files)
        count=0
        symbolsLength=0
        Errors=[]
        arrErrors=[]
        for i in range(len(omr_symbolsAlign[0])):
            
            sGround=omr_symbolsAlign[0][i]
            sOMR=omr_symbolsAlign[1][i]
            if isinstance(sGround,list):
                sGroundSimple=sGround[0]
            else:
                sGroundSimple=sGround
            if isinstance(sOMR,list):
                sOMRSimple=sOMR[0]
            else:
                sOMRSimple=sOMR
                
            if(self.isGraceNote(sGround) or self.isGraceNote(sOMR)):
                continue    
            if(self.isKeySignature(sGroundSimple) or self.isKeySignature(sOMRSimple)):
                continue        
            if (sGroundSimple==sOMRSimple):
                if isinstance(sOMR,list)!=True:
                    count+=1
                else:
                    if sGround[0]==sOMR[0]: #and sGround[1]==sOMR[1]:#not counting ties
                        count+=1
                    else:
                        Errors.append([sGround,sOMR,i])
                        arrErrors.append(i)
                        
                    
            else:
                Errors.append([sGround,sOMR,i])
                arrErrors.append(i)
                
            symbolsLength+=1
        result=(float(count)/symbolsLength)*100
        scoreWithErrors=pa.convertM21(omr_symbolsAlign[1], arrErrors,omr_symbolsAlign[0])

        return result,Errors,scoreWithErrors
    
    def isGraceNote(self,s):
        if isinstance(s,list):
            if s[0].find('N:')!=-1: 
                duration=s[1]
                if float(duration)==0:
                    return True
           
        return False
    def isKeySignature(self,s):
        if s.find('KS:')!=-1: 
                return True
        return False
               

