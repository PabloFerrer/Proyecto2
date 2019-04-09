from Views import TrainMenu as TM, TrainWebMenu as TWM , AdminUsers as AU
from Controllers import TrainController as TC, TrainWebController as TWC
from Model import DB_Driver as DD
from PyQt5.QtWidgets import QWidget,QTableWidget,QGridLayout,QTableWidgetItem,QFileDialog, QLabel

class AdminController:

    def __init__(self, view):
        self.view = view


    def openTrainer(self):
        ctrl = TC.TrainController()
        ventanaEntrenamiento = TM.TrainMenu(ctrl)
        ctrl.asignarVentana(ventanaEntrenamiento)
        ventanaEntrenamiento.show()

    def openWebScrapper(self):
        ventanaEntrenamientoWeb = TWM.TrainWebMenu()
        ventanaEntrenamientoWeb.show()
        
        
    def openGestor(self):
        ventanaGestionUsuarios = AU.AdminUsers()
        ventanaGestionUsuarios.show()
        
    def getUser(self):
        driver =  DD.DB_Driver()
        result = driver.getUserList()
        print(result)
        
        for i in result:
            
            rowPosition = self.view.tableWidget.rowCount()
            self.view.tableWidget.insertRow(rowPosition)
    
            self.view.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(i[0]))
    
            
    
        driver.closeConnection()
        return result
   
        
        
        
    def insertUser(self,user,password):
        driver =  DD.DB_Driver()
        driver.registerUser(user,password)
        result = driver.getUserList()
        self.view.tableWidget.setRowCount(0)
        
        for i in result:
            
            rowPosition = self.view.tableWidget.rowCount()
            self.view.tableWidget.insertRow(rowPosition)
    
            self.view.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(i[0]))
        
        
        driver.closeConnection()
        
        