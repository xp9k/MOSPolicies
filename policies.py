import sys, os
import platform
from typing import Dict
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow
)
import xml.etree.ElementTree as xml
from xml.dom import minidom
from ui_mainform import Ui_MainWindow
from ui_editdialog import Ui_Dialog


if platform.system() == "Linux":
    PoliciesDir = "/usr/share/polkit-1/actions/"
else:
    PoliciesDir = ".\\actions\\" # для тестов на винде 

actions = []


def GetPolicyText(TextDict: Dict, language: str = 'ru'):
    return TextDict.get(language, TextDict['default'])
        

def list_policies():
    return os.listdir(PoliciesDir)


def read_xml(filename: str) -> bool:
    global actions
    actions = []
    try:
        xmldoc = minidom.parse(filename)
        actionslist = xmldoc.getElementsByTagName('action')
        for action in actionslist:
            act = {}
            act['id'] = action.attributes['id'].value
            act['descriptions'] = {}
            for description in action.getElementsByTagName('description'):            
                if 'xml:lang' in description.attributes: 
                    if description.firstChild is not None:
                        act['descriptions'][description.attributes['xml:lang'].value] = description.firstChild.nodeValue or ''
                    else:
                        act['descriptions'][description.attributes['xml:lang'].value] = ''
                else:
                    act['descriptions']['default'] = description.firstChild.nodeValue or ''
            act['messages'] = {}             
            for message in action.getElementsByTagName('message'):            
                if 'xml:lang' in message.attributes:
                    if message.firstChild is not None:
                        act['messages'][message.attributes['xml:lang'].value] = message.firstChild.nodeValue
                    else:
                        act['messages'][message.attributes['xml:lang'].value] = ''
                else:
                    act['messages']['default'] = message.firstChild.nodeValue
            tmp = action.getElementsByTagName('allow_active')
            for row in tmp:
                    act['allow_active'] = row.firstChild.nodeValue
            tmp = action.getElementsByTagName('allow_inactive')
            for row in tmp:
                act['allow_inactive'] = row.firstChild.nodeValue
            tmp = action.getElementsByTagName('allow_any')
            for row in tmp:
                    if row.firstChild is not None:
                        act['allow_any'] = row.firstChild.nodeValue
            actions.append(act)
    except:
        return False
    return True


def write_xml(filename: str, id: str, data: Dict) -> bool:
    xmldoc = xml.parse(filename)
    root = xmldoc.getroot()
    action = root.find(f'.//action[@id="{id}"]')
    if action is None:
        return False

    tmp = action.find('.//allow_active')
    tmp.text = data['allow_active']
    tmp = action.find('.//allow_inactive')
    tmp.text = data['allow_inactive']

    tmp = action.find('.//defaults/allow_any')

    try:
        if data['allow_any'] == "":
            action.find(".//defaults").remove(tmp)
        else:
            if tmp is None:
                allow_any = xml.Element("allow_any")
                action.find(".//defaults").append(allow_any)
                action.find('.//defaults/allow_any').text = data["allow_any"]
            else:
                tmp.text = data["allow_any"]
        
        xmldoc.write(filename)
    except:
        return False

    return True


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.listWidget.currentItemChanged.connect(self.listpoliciesclick)
        self.listWidget_2.currentItemChanged.connect(self.listactionsclick)
        self.listWidget_2.doubleClicked.connect(self.listActionsDblClick)

        self.listWidget.clear()
        for file in list_policies():
            self.listWidget.addItem(file)

    def listpoliciesclick(self):
        read_xml(PoliciesDir + self.listWidget.currentItem().text())
        self.listWidget_2.clear()
        for action in actions:
            self.listWidget_2.addItem(GetPolicyText(action['descriptions']))
        self.textEdit.setText('')
        self.statusbar.showMessage(f"Количество опций: {len(actions)}")

    def listactionsclick(self):
        index = self.listWidget_2.currentRow()
        self.textEdit.setText('')
        self.textEdit.setText(GetPolicyText(actions[index]['messages']))

    def listActionsDblClick(self, item):
        index = self.listWidget_2.currentRow()
        frmEdit.lbMessage.setText(GetPolicyText(actions[index]['descriptions']))   # Да, потому что в политиках смысл текста в 
        frmEdit.lbDescription.setText(GetPolicyText(actions[index]['messages']))   # в описании и сообщении местами поменян
        
        cb_index = frmEdit.cbActive.findText(actions[index].get('allow_active'))
        if index != -1:
            frmEdit.cbActive.setCurrentIndex(cb_index)
        cb_index = frmEdit.cbInactive.findText(actions[index].get('allow_inactive'))
        if index != -1:
            frmEdit.cbInactive.setCurrentIndex(cb_index)
        cb_index = frmEdit.cbAny.findText(actions[index].get('allow_any'))
        if index != -1:
            frmEdit.cbAny.setCurrentIndex(cb_index)

        frmEdit.XMLFileName = PoliciesDir + self.listWidget.currentItem().text()
        frmEdit.ActionID = actions[index]["id"]
        frmEdit.show()



class EditDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.btSave.clicked.connect(self.btAcceptClick)
        self.btCancel.clicked.connect(lambda: self.hide())
        

    def btAcceptClick(self):
        data = {
            'allow_active': self.cbActive.currentText(),
            'allow_inactive': self.cbInactive.currentText(),
            'allow_any': self.cbAny.currentText(),
        }
        write_xml(self.XMLFileName, self.ActionID, data)
        read_xml(self.XMLFileName)
        self.hide()


Application = QApplication(sys.argv)
frmMain = MainWindow()
frmEdit = EditDialog()


def main():
    frmMain.show()
    sys.exit(Application.exec())


if __name__ == "__main__":
    main()