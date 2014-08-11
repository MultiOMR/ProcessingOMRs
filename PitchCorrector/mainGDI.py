'''
Created on 09/06/2014

@author: victor
'''
import os
import wx

from music21 import converter
from ProcessPitchCorrector import ProcessPitchCorrector
from MultipleOMR.Music21Functions import Music21Functions



class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400,400))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar() 

        filemenu= wx.Menu()
        utilsmenu=wx.Menu()

        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open and Process"," Process the MusicXML files in the folder")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") 
        menuBar.Append(utilsmenu,"&Utils") 
        self.SetMenuBar(menuBar)  

        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Show(True)

    def OnAbout(self,e):
        dlg = wx.MessageDialog( self, "Pitch corrector", "Pitch corrector", wx.OK)
        dlg.ShowModal() 
        dlg.Destroy()

    def OnExit(self,e):
        self.Close(True)  
    
    def trace(self,txt):
        self.control.SetValue(self.control.GetValue()+"\n"+txt)
    def OnViewMusicXimple(self,e):
        self.filename = ''
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard="",
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()

            for path in paths:
                xml = converter.parse(path)
                xml.show()

        
        dlg.Destroy()

    def getFiles(self,path):
        omr_files=[]
        dir_content = os.listdir(path)
        for myfile in dir_content:
                directory = os.path.join(path,myfile)
                if  myfile.find("result.")==-1 and myfile!="ground.xml" and myfile!="pitchCorrected.xml" :
                    omr_files.append(os.path.abspath(directory))
        return omr_files
    def getResult(self,path):
        dir_content = os.listdir(path)
        for myfile in dir_content:
                directory = os.path.join(path,myfile)
                if myfile =="result.S1.xml":
                    return os.path.abspath(directory)
    def runPitchCorrector(self,dirname):
        path = dirname
        omr_files=self.getFiles(path)
        omr_result=self.getResult(path)
        
        filesArray=[]
        filesArray.append(omr_result)
        for files in omr_files:
            filesArray.append(files)
            
        ppc=ProcessPitchCorrector()
        omrResult=[]
        omrResult.append(omr_result)
        hashArrayResult=ppc.getHashFromOMRs(omrResult)
        hashArrayOMRs=ppc.getHashFromOMRs(omr_files)
        
        resultHashWithExtraRest,omrsWithExtraRest=ppc.alignHashResultWithOMR(hashArrayResult[0], hashArrayOMRs)
        resultHashWithExtraRest,omrsHashWithExtraRest=ppc.alignHashResultWithOMR(resultHashWithExtraRest, hashArrayOMRs)
        
        hashArrays=[]
        hashArrays.append(resultHashWithExtraRest)
        for hash in omrsHashWithExtraRest:
            hashArrays.append(hash)
        
        print filesArray
        OMRs=ppc.convertFilesToMusic21(filesArray)  
        omrJoinedParts=ppc.reconstructScores(OMRs,hashArrays)
        omrJoinedParts.show()
        resultPitchCorrected=ppc.votePitch(omrJoinedParts)
        resultPitchCorrected.show()
    
        resultPitchCorrected.write("musicxml", path+'/pitchCorrected.xml')

    def OnOpen(self,e):
        dirname = ''
        dlg = wx.DirDialog(None, "Choose a directory","",wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetPath()
            self.runPitchCorrector(dirname)
            
        dlg.Destroy()

app = wx.App(False)
frame = MainWindow(None, "Correct Pitch")
app.MainLoop()