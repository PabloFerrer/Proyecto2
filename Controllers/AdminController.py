from Views import TrainMenu as TM, TrainWebMenu as TWM , AdminUsers as AU
from Controllers import TrainController as TC, TrainWebController as TWC
from Model import DB_Driver as DD

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
        driver.getUser()
        driver.closeConnection()
        
        
    def insertUser(self,user,password):
        driver =  DD.DB_Driver()
        driver.registerUser(user,password)
        driver.closeConnection()
        
        