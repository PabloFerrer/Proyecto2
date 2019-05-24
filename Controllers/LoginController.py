from Views import AdminMenu as AM, LoginMenu as MM
from Controllers import ClassifyController as CWC, AdminController as AC
from main import Main as m
from Model import DB_Driver as DB
import hashlib, uuid


class LoginController:

    def __init__(self, view):
        self.view = view

    def user_access(self, username, password):

        valid, role = self.__validate(username,password)

        if valid != True:
            return

        if valid and role == 0:
            self.view.running = False
            classifier = CWC.ClassifyWebController()
            self.view.close()

        elif valid and role == 1:

            self.view.running = False
            adminMenu = AC.AdminController()
            self.view.close()


    def __validate(self, username,password):

        db = DB.DB_Driver()
        db_hash, db_role = db.getUser(username)
        db.closeConnection()

        if db_hash == 0 and db_role == 0:
            print("Validation failed: No user found")
            self.view.label_errors.setVisible(True)
            return False, 0

        hashed_password = hashlib.sha512(password.encode('utf8')).hexdigest()

        if not hashed_password == db_hash:
            print("Validation failed: Password incorrect")
            self.view.label_errors.setVisible(True)
            return False, 0
        else:
            return True, db_role








