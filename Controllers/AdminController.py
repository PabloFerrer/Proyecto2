import sys
import os
import glob
import csv
import pickle
import itertools

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFileDialog, QLabel, QApplication

from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

import matplotlib.pyplot as plt

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from PyQt5.QtWidgets import QTableWidgetItem

from Utilities.Scrappers import MetacriticScrapper as MS, SteamScrapper as SS, YelpScrapper as YS, AmazonScrapper as AS
from Views import AlgorithmDialog, AdminMenu as AM, TrainOutputWindow as TOW
from Model import User as US, Model as MD


class AdminController:

    def __init__(self):
        self.view = AM.AdminMenu(self)
        self.loadUsers()
        self.view.show()

        self.linkList = []
        self.pathList = []
        self.starList = []
        self.contentList = []
        self.starList2 = []
        self.contentList2 = []
        self.categoryList = []
        self.addedList = []
        self.labels = []
        self.algorithm = ''
        self.algorithm_name = ''
        self.stopword = ''
        self.route = ''
        self.link = ''
        self.subdirectories = []

        self.n_estimators = 1000
        self.random_state = 0
        self.max_depth = None
        self.verbose = 0
        self.oob_score = False

        self.var_smoothing = 1e-09

        self.shrinking = False
        self.max_iter = -1



    # def getUser(self):
    #     result = US.User().getUserList()
    #
    #     for i in result:
    #
    #         rowPosition = self.view.userTable.rowCount()
    #         self.view.userTable.insertRow(rowPosition)
    #         item = QTableWidgetItem(i[0])
    #         item.setFlags(QtCore.Qt.ItemIsEnabled)
    #         self.view.userTable.setItem(rowPosition, 0, item)
    #
    #     return result


    def loadUsers(self):
        result = US.User().getUserList()
        listaUsers = []

        for i in result:
            listaUsers.append(i[0])
        self.view.comboBox.addItems(listaUsers)

        for i in result:
            rowPosition = self.view.userTable.rowCount()
            self.view.userTable.insertRow(rowPosition)
            item = QTableWidgetItem(i[0])
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.view.userTable.setItem(rowPosition, 0, item)

    def insertUser(self,user,password):

        US.User().registerUser(user,password)
        self.loadUsers()


    def deleteUser(self, user):

        US.User().deleteUser(user)
        self.loadUsers()


    def addFromFile(self):
        self.route = QFileDialog.getExistingDirectory(self.view, "Select Directory")
        self.pathList.append(self.route)
        file_pattern = os.path.join(self.route, '*.csv')
        file_list = glob.glob(file_pattern)
        review_count = 0
        for file in file_list:
            with open(file) as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                for row in readCSV:
                    review_count += 1
                    self.starList.append(row[0])
                    self.contentList.append(row[1])
                    rowPosition = self.view.tableWidget.rowCount()
                    self.view.tableWidget.insertRow(rowPosition)
                    self.view.tableWidget.resizeColumnsToContents()
                    item = QTableWidgetItem(f"{self.route}")
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    item2 = QTableWidgetItem(str(row[0]))
                    item2.setFlags(QtCore.Qt.ItemIsEnabled)
                    item3 = QTableWidgetItem(str(row[1]))
                    item3.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.view.tableWidget.setItem(rowPosition, 0, item)
                    self.view.tableWidget.setItem(rowPosition, 1,
                                                  item2)
                    self.view.tableWidget.setItem(rowPosition, 2,
                                                  item3)


    def validate(self):
        if 'https://www.metacritic.com' in self.view.lineEdit_URL.text() and self.view.comboBox_websites.currentText() == 'Metacritic':            
            if re.search("https://www.metacritic.com/movie/.*", self.view.lineEdit_URL.text()) or re.search("https://www.metacritic.com/game/.*/.*", self.view.lineEdit_URL.text()) or re.search("https://www.metacritic.com/tv/.*/.*", self.view.lineEdit_URL.text()) or re.search("https://www.metacritic.com/music/.*/.*", self.view.lineEdit_URL.text()):
                self.view.label_formatError.setVisible(False)
                self.addURL()
            else:
                self.view.label_formatError.setVisible(True)
                self.view.label_formatError.setText('Invalid Metacritic URL.')
        elif 'store.steampowered.com' in self.view.lineEdit_URL.text() and self.view.comboBox_websites.currentText() == 'Steam':
            if re.search("store.steampowered.com/app/.*", self.view.lineEdit_URL.text()):
                self.view.label_formatError.setVisible(False)
                self.addURL()
            else:
                self.view.label_formatError.setVisible(True)
                self.view.label_formatError.setText('Invalid Steam URL.')
        elif 'https://www.amazon.com' in self.view.lineEdit_URL.text() and self.view.comboBox_websites.currentText() == 'Amazon':
            if re.search("https://www.amazon.com/.*?/ref", self.view.lineEdit_URL.text()):
                self.view.label_formatError.setVisible(False)
                self.addURL()
            else:
                self.view.label_formatError.setVisible(True)
                self.view.label_formatError.setText('Invalid Amazon URL.')
        elif 'https://www.yelp.' in self.view.lineEdit_URL.text() and self.view.comboBox_websites.currentText() == 'Yelp':
            if re.search("yelp.*/biz/.*", self.view.lineEdit_URL.text()):
                self.view.label_formatError.setVisible(False)
                self.addURL()
            else:
                self.view.label_formatError.setVisible(True)
                self.view.label_formatError.setText('Invalid Yelp URL.')
        else:
            self.view.label_formatError.setVisible(True)
            self.view.label_formatError.setText('Invalid path, please insert a valid path.')

    def addURL(self):
        self.link = self.view.lineEdit_URL.text()
        self.linkList.append(self.link)
        self.scrapLinks()
        self.view.lineEdit_URL.setText("")
        self.linkList.clear()

        
    def switch_view(self,new_view):
        self.view.close()
        self.view = new_view(self)
        self.view.show()

    def scrapLinks(self):
        metacriticScrapper = MS.MetacriticScrapper()
        steamScrapper = SS.SteamScrapper()
        yelpScrapper = YS.YelScrapper()
        amazonScrapper = AS.AmazonScrapper()
        if not self.linkList and not self.pathList:
            self.view.labelError1.setVisible(True)
        else:
            self.view.labelError1.setVisible(False)
            for url in self.linkList:
                print("Scrapping link: " + url)
                url_stars, url_reviews = [], []
                if 'metacritic.com' in url:
                    print("Detected as Metacritic URL")
                    url_stars, url_reviews = metacriticScrapper.scrapURL(url)
                elif 'store.steampowered.com' in url:
                    print("Detected as Steam URL")
                    url_stars, url_reviews = steamScrapper.scrapURL(url)
                elif 'amazon.com' in url:
                    print("Detected as Amazon URL")
                    url_stars, url_reviews = amazonScrapper.scrapURL(url)
                elif 'yelp.com' in url:
                    print("Detected as Yelp URL")
                    url_stars, url_reviews = yelpScrapper.scrapURL(url)
                else:
                    print("Detected as invalid link")
                print("Finished scrapping URL")

                self.starList += url_stars
                self.contentList += url_reviews
            cont = 0
            for i in range(0, len(self.contentList)):
                rowPosition = self.view.tableWidget.rowCount()
                self.view.tableWidget.insertRow(rowPosition)
                self.view.tableWidget.resizeColumnsToContents()
                item = QTableWidgetItem(f"{self.link}")
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                item2 = QTableWidgetItem(str(self.starList[cont]))
                item2.setFlags(QtCore.Qt.ItemIsEnabled)
                item3 = QTableWidgetItem(str(self.contentList[cont]))
                item3.setFlags(QtCore.Qt.ItemIsEnabled)
                self.view.tableWidget.setItem(rowPosition, 0, item)
                self.view.tableWidget.setItem(rowPosition, 1,
                                              item2)
                self.view.tableWidget.setItem(rowPosition, 2,
                                              item3)
                cont = cont + 1

    def goBack(self):
        self.linkList = []
        self.pathList = []
        self.starList = []
        self.contentList = []
        self.starList2 = []
        self.contentList2 = []
        self.categoryList = []
        self.addedList = []
        self.labels = []
        self.algorithm = ''
        self.algorithm_name = ''
        self.stopword = ''
        self.route = ''
        self.link = ''
        self.subdirectories = []

        self.switch_view(AM.AdminMenu)

    def guardar_modelo(self):


        nombre_modelo = self.view.modelName_text_.text()

        if not nombre_modelo:
            self.view.label_guardarModelo_.setVisible(True)
            self.view.label_guardarModelo_.setText("You didn't choose a name for the model. Please choose a name")
        elif not self.algorithm:
            self.view.label_guardarModelo_.setVisible(True)
            self.view.label_guardarModelo_.setText('Please do a training to save the model.')
        else:
            self.view.label_guardarModelo_.setVisible(False)
            # Aqui guardamos el Modelo en formato pickle
            with open(f'./Resources/Models/{nombre_modelo}', 'wb') as modelo_completo:

                pickle.dump(self.algorithm, modelo_completo)
                pickle.dump(self.vectorizador, modelo_completo)
                pickle.dump(self.labels, modelo_completo)

            MD.Model().uploadToS3(nombre_modelo)

            self.view.label_guardarModelo_.setText('¡Saved!')
            self.view.label_guardarModelo_.setVisible(True)

    def __starsToCategories(self):
        category_number = self.view.comboBox_categorias.currentText()

        if category_number == '2':
            self.categoryList = [self.view.lineEdit_cat1.text(), self.view.lineEdit_cat2.text()]
            for item in self.starList:
                value = int(item)
                if value < 3:  # Originally >3 but it seemed so weird to invert the order here, so I assumed it was a bug
                    self.labels.append(self.view.lineEdit_cat2.text())
                else:
                    self.labels.append(self.view.lineEdit_cat1.text())

        elif category_number == '3':
            self.categoryList = [self.view.lineEdit_cat1.text(), self.view.lineEdit_cat2.text(),
                                 self.view.lineEdit_cat3.text()]
            for item in self.starList:
                value = int(item)
                if value < 2:
                    self.labels.append(self.view.lineEdit_cat3.text())
                elif value < 4:
                    self.labels.append(self.view.lineEdit_cat2.text())
                else:
                    self.labels.append(self.view.lineEdit_cat1.text())

        elif category_number == '4':
            self.categoryList = [self.view.lineEdit_cat1.text(), self.view.lineEdit_cat2.text(),
                                 self.view.lineEdit_cat3.text(), self.view.lineEdit_cat4.text()]
            for item in self.starList:
                value = int(item)
                if value < 1:
                    self.labels.append(self.view.lineEdit_cat4.text())
                elif value < 3:
                    self.labels.append(self.view.lineEdit_cat3.text())
                elif value < 5:
                    self.labels.append(self.view.lineEdit_cat2.text())
                else:
                    self.labels.append(self.view.lineEdit_cat1.text())

        elif category_number == '5':
            self.categoryList = [self.view.lineEdit_cat1.text(), self.view.lineEdit_cat2.text(),
                                 self.view.lineEdit_cat3.text(), self.view.lineEdit_cat4.text(),
                                 self.view.lineEdit_cat5.text()]

            for item in self.starList:
                value = int(item)
                if value < 2:  # A heart!
                    self.labels.append(self.view.lineEdit_cat5.text())
                elif value < 3:
                    self.labels.append(self.view.lineEdit_cat4.text())
                elif value < 4:
                    self.labels.append(self.view.lineEdit_cat3.text())
                elif value < 5:
                    self.labels.append(self.view.lineEdit_cat2.text())
                else:
                    self.labels.append(self.view.lineEdit_cat1.text())

    def webscrapper_train(self):
        if not self.contentList:
            self.view.boton_clasificador_.setText('Please perform webscraping before training.')
        else:
            self.view.boton_clasificador_.setText('Execute Training')
            self.__starsToCategories()

            print("Ejecutando el entrenador...")
            nltk.download('stopwords')
            stemmer = PorterStemmer()

            X, y = self.contentList, self.labels

            documentos = []
            self.stopword = str(self.view.comboBox_stopwords.currentText())
            for sen in range(0, len(X)):
                # Elimina: carácteres especiales
                documento = re.sub(r'\W', ' ', str(X[sen]))

                # Elimina: carácteres solos
                # remove all single characters
                documento = re.sub(r'\s+[a-zA-Z]\s+', ' ', documento)

                # Elimina: números
                documento = re.sub(r'\d', ' ', documento)

                # Elimina: carácteres solos al principio de una línea.
                documento = re.sub(r'\^[a-zA-Z]\s+', ' ', documento)

                # Sustituye: los tabuladores o multiples espacios por un solo espacio
                documento = re.sub(r'\s+', ' ', documento, flags=re.I)

                # Removing prefixed 'b'
                documento = re.sub(r'^b\s+', '', documento)

                # Convierte todas las mayusuculas a minúsculas
                documento = documento.lower()

                # Hacemos el Stem para sacar las raices de cada una de las palabras
                documento = documento.split()

                documento = [stemmer.stem(word) for word in documento]
                documento = ' '.join(documento)

                documentos.append(documento)
            self.vectorizador = TfidfVectorizer(max_features=1500, min_df=5, max_df=0.7,
                                                stop_words=stopwords.words(self.stopword))

            # Almacenamos las palabras en su respectivo formato numerico en X
            X = self.vectorizador.fit_transform(documentos).toarray()

            X_entrenamiento, X_test, y_entrenamiento, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

            self.choose_algorithm()

            self.algorithm.fit(X_entrenamiento, y_entrenamiento)
            y_pred = self.algorithm.predict(X_test)
            matriz_confusion = confusion_matrix(y_test, y_pred)

            figura = plt.figure()
            ax = figura.add_subplot(111)

            cmap = plt.get_cmap('Blues')
            cax = ax.matshow(matriz_confusion, interpolation='nearest', cmap=cmap)
            figura.colorbar(cax)

            etiquetas = np.arange(len(self.categoryList))
            plt.xticks(etiquetas, self.categoryList, rotation=45)
            plt.yticks(etiquetas, self.categoryList)

            fmt = '.2f'
            thresh = matriz_confusion.max() / 2.
            for i, j in itertools.product(range(matriz_confusion.shape[0]), range(matriz_confusion.shape[1])):
                plt.text(j, i, format(matriz_confusion[i, j], fmt),
                         horizontalalignment="center",
                         color="white" if matriz_confusion[i, j] > thresh else "black")

            plt.xlabel('Predicted')
            plt.ylabel('True')
            figura.savefig('./Resources/UIElements/Matriz.png')
            print("Imagen guardada")

            self.switch_view(TOW.TrainOutputWindow)

            label = QLabel(self.view)
            pixmap = QPixmap('./Resources/UIElements/Matriz.png')
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.show()
            self.view.lay_.addWidget(label)

            true_positive = matriz_confusion[0][0]
            false_positive = matriz_confusion[0][1]
            false_negative = matriz_confusion[1][0]
            true_negative = matriz_confusion[1][1]

            print(matriz_confusion)
            print(classification_report(y_test, y_pred))
            self.precision = accuracy_score(y_test, y_pred)

            print('True positive = ', true_positive)
            print('False positive = ', false_positive)
            print('False negative = ', false_negative)
            print('True negative = ', true_negative)
            print(self.precision)
            
            self.view.label_precision_.setText("Accuracy of " + str(self.precision))

    def choose_algorithm(self):
        self.algorithm_name = str(self.view.comboBox_algoritmos.currentText())

        if self.algorithm_name == 'Random Forest':
            self.algorithm = RandomForestClassifier(n_estimators=self.n_estimators, random_state=self.random_state,
                                                    max_depth=self.max_depth, verbose=self.verbose,
                                                    oob_score=self.oob_score)

        elif self.algorithm_name == 'Naive Bayes':
            self.algorithm = GaussianNB(var_smoothing=self.var_smoothing)

        elif self.algorithm_name == 'SVM':
            self.algorithm = SVC(max_iter=self.max_iter, verbose=self.verbose, random_state=self.random_state,
                                 shrinking=self.shrinking)

        # def save_model(self):

    def editAlgorithm(self):
        self.algorithm_name = str(self.view.comboBox_algoritmos.currentText())
        dialog = AlgorithmDialog.AlgorithmDialog(self.algorithm_name, self)
        dialog.show()

    def change_category_combo(self):

        category_number = str(self.view.comboBox_categorias.currentText())

        if category_number == '2':
            self.categoryList = [self.view.lineEdit_cat1.text(), self.view.lineEdit_cat2.text()]
            self.view.lineEdit_cat1.setText('Good')
            self.view.lineEdit_cat2.setText('Bad')
            self.view.label_12.setVisible(False)
            self.view.lineEdit_cat3.setVisible(False)
            self.view.label_13.setVisible(False)
            self.view.lineEdit_cat4.setVisible(False)
            self.view.label_14.setVisible(False)
            self.view.lineEdit_cat5.setVisible(False)


        elif category_number == '3':
            self.view.lineEdit_cat1.setText('Good')
            self.view.lineEdit_cat2.setText('Neutral')
            self.view.lineEdit_cat3.setText('Bad')
            self.view.label_12.setVisible(True)
            self.view.lineEdit_cat3.setVisible(True)
            self.view.label_13.setVisible(False)
            self.view.lineEdit_cat4.setVisible(False)
            self.view.label_14.setVisible(False)
            self.view.lineEdit_cat5.setVisible(False)


        elif category_number == '4':
            self.view.lineEdit_cat1.setText('Very good')
            self.view.lineEdit_cat2.setText('Good')
            self.view.lineEdit_cat3.setText('Bad')
            self.view.lineEdit_cat4.setText('Very bad')
            self.view.label_12.setVisible(True)
            self.view.lineEdit_cat3.setVisible(True)
            self.view.label_13.setVisible(True)
            self.view.lineEdit_cat4.setVisible(True)
            self.view.label_14.setVisible(False)
            self.view.lineEdit_cat5.setVisible(False)


        elif category_number == '5':
            self.view.lineEdit_cat1.setText('Very good')
            self.view.lineEdit_cat2.setText('Good')
            self.view.lineEdit_cat3.setText('Neutral')
            self.view.lineEdit_cat4.setText('Bad')
            self.view.lineEdit_cat5.setText('Very bad')
            self.view.label_12.setVisible(True)
            self.view.lineEdit_cat3.setVisible(True)
            self.view.label_13.setVisible(True)
            self.view.lineEdit_cat4.setVisible(True)
            self.view.label_14.setVisible(True)
            self.view.lineEdit_cat5.setVisible(True)


if __name__ == "__main__":
    # execute only if run as a script
    app = QApplication(sys.argv)

    test = AdminController()
    test.switch_view(TOW.TrainOutputWindow)


