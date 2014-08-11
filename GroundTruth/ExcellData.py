
import xlsxwriter

class ExcellData:
    def saveData(self,data,files,percentages):
        path=self.getPath(files[0])
        wb=xlsxwriter.Workbook(path+'/Result/result.xlsx')
        ws=wb.add_worksheet()
        c=0
        ws.write(0, 0,str(files[0]))
        
        for col in data:
            ws.write(1, c,str(percentages[c]))
            r=2
            fArray=files[c+1].split('\\')
            ws.write(r, c,str(fArray[-1]))
            
            for row in col:
                r+=1
                ws.write(r, c,str(row))
            c+=1   
        wb.close()
    def saveGlobalData(self,data,dir):
        wb=xlsxwriter.Workbook(dir+'/resultGeneral.xlsx')
        ws=wb.add_worksheet()
        c=0
        
        for col in data:
            r=1
            for row in col:
                r+=1
                ws.write(c, r,float(row))
            c+=1   
        wb.close()
    def getPath(self,f):
        fArray=f.split('\\')
        path=''
        for i in range(len(fArray)-2):
            path+=fArray[i]+"/"
        return path
    def saveArray(self,path,data):
        wb=xlsxwriter.Workbook(path+'alignS2.xlsx')
        ws=wb.add_worksheet()
        c=0

        for col in data:
            r=1
            for row in col:
                r+=1
                ws.write(r, c,str(row))
            c+=1   
        wb.close()