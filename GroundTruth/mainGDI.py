'''
Created on 09/06/2014

@author: victor
'''
import os
import wx
from ProcessGroundS2 import ProcessGroundS2
from music21 import converter
from ExcellData import ExcellData


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
        
        menuViewMusicXimple = utilsmenu.Append(wx.ID_ANY, "&View MusicXiMpLe"," View MusicXiMpLe")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") 
#         menuBar.Append(utilsmenu,"&Utils") 
        self.SetMenuBar(menuBar)  

        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnViewMusicXimple, menuViewMusicXimple)

        self.Show(True)
    def getPath(self,f):
        fArray=f.split('\\')
        path=''
        for i in range(len(fArray)-2):
            path+=fArray[i]+"/"
        return path

    def OnAbout(self,e):
        dlg = wx.MessageDialog( self, "Ground Truth Processing", "Ground Truth Processing", wx.OK)
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
                if myfile=="ground.xml":
                    omr_files.append(os.path.abspath(directory))
        for myfile in dir_content:
                directory = os.path.join(path,myfile)
                if myfile!="ground.xml":
                    omr_files.append(os.path.abspath(directory))
        return omr_files
    def SubDirPath (self,d):
        return filter(os.path.isdir, [os.path.join(d,f) for f in os.listdir(d)])  
    def OnOpen(self,e):
        dlg = wx.DirDialog(None, "Choose a directory","",wx.DD_DEFAULT_STYLE)
        
        if dlg.ShowModal() == wx.ID_OK:
            dirGeneral = dlg.GetPath()
            subdirname=self.SubDirPath(dirGeneral)
            percentagesArray=[]
            for dirname in subdirname:
                d=dirname+"/XML/"
                files=self.getFiles(d)
                print files
                pg=ProcessGroundS2()
                ErrorsMatrix=[]
                percentages=[]
                for i in range(len(files)-1):
                    myFiles=[]
                    myFiles.append(files[0])
                    myFiles.append(files[i+1])
                    print " "
                    print "*********************"
                    percentage,errors,scoreWithErrors= pg.getSimilarity(myFiles)
                    ErrorsMatrix.append(errors)
                    percentages.append(percentage)
                    path=self.getPath(files[0])
                    if not os.path.exists(path+"/Result"):
                        os.makedirs(path+"/Result")
                    scoreWithErrors.write("musicxml", path+"/Result/"+os.path.basename(files[i+1]))
                ed=ExcellData()
                ed.saveData(ErrorsMatrix,files,percentages)  
                percentagesArray.append(percentages)  
                print "----------- END ------------"
            ed=ExcellData()
            ed.saveGlobalData(percentagesArray,dirGeneral)  
        dlg.Destroy()

app = wx.App(False)
frame = MainWindow(None, "Ground Truth")
app.MainLoop()