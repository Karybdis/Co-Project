#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QDesktopWidget, QHBoxLayout, QVBoxLayout,
                             QGridLayout, QLabel, QLineEdit, QTextEdit,
                             QComboBox, QMessageBox, QInputDialog, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()  # 界面绘制交给InitUi方法

    def initUI(self):
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        # 设置窗口的位置和大小，从屏幕上（300，300）位置开始，显示一个300*220的界面（宽300，高220）
        self.setGeometry(300, 300, 800, 500)
        self.center()
        # 设置窗口的标题
        self.setWindowTitle('论文下载神器')
        # 设置窗口的图标，引用当前目录下的web.png图片
        self.setWindowIcon(QIcon('web.png'))

        # 设置按键
        statisticsBtn = QPushButton('一键统计', self)
        # sizeHint()显示默认尺寸
        statisticsBtn.resize(90, 30)
        # 移动窗口的位置
        statisticsBtn.move(110, 175)

        monthvisualizationBtn = QPushButton('该月可视化', self)
        monthvisualizationBtn.resize(90, 30)
        monthvisualizationBtn.move(10, 210)
        yearvisualizationBtn = QPushButton('该年可视化', self)
        yearvisualizationBtn.resize(90, 30)
        yearvisualizationBtn.move(110, 210)
        trendBtn = QPushButton('趋势可视化', self)
        trendBtn.resize(90, 30)
        trendBtn.move(210, 210)
        downloadBtn = QPushButton('下载', self)
        downloadBtn.resize(60, 30)
        downloadBtn.move(300, 430)
        searchBtn = QPushButton('查询', self)
        searchBtn.resize(60, 30)
        searchBtn.move(260, 300)
        openBtn = QPushButton('打开', self)
        openBtn.resize(60, 30)
        openBtn.move(230, 430)

        # 将点击事件与不同的按键结合
        # statisticsBtn.clicked.connect(self.statisticsBtnClicked)
        # monthvisualizationBtn.clicked.connect(self.monthvisualizationBtnClicked)
        # yearvisualizationBtn.clicked.connect(self.yearvisualizationBtnClicked)
        # trendBtn.clicked.connect(self.trendBtnClicked)
        downloadBtn.clicked.connect(self.downloadBtnClicked)
        openBtn.clicked.connect(self.showDialog)

        # 设置各个部位
        title1 = QLabel('统计可视', self)
        title1.move(10, 10)
        title2 = QLabel('查询', self)
        title2.move(10, 260)
        title3 = QLabel('批量下载', self)
        title3.move(10, 390)
        title4 = QLabel('信息显示', self)
        title4.move(410, 10)
        title5 = QLabel('文档地址', self)
        title5.move(10, 430)
        title6 = QLabel('科目', self)
        title6.move(60, 55)
        title7 = QLabel('时间', self)
        title7.move(60, 95)
        title8 = QLabel("年", self)
        title8.move(170, 94)
        title9 = QLabel("月", self)
        title9.move(250, 94)
        title10 = QLabel("年", self)
        title10.move(170, 124)
        title11 = QLabel("月", self)
        title11.move(250, 124)
        title12 = QLabel("至", self)
        title12.move(100, 124)
        title13 = QLabel("输入序号", self)
        title13.move(20, 340)

        self.edit = QTextEdit(self)
        self.edit.resize(370, 430)
        self.edit.move(410, 50)

        self.searchedit = QLineEdit(self)
        self.searchedit.resize(150, 30)
        self.searchedit.move(100, 300)

        self.pathedit = QLineEdit(self)
        self.pathedit.resize(150, 30)
        self.pathedit.move(70, 430)

        yearedit = QLineEdit(self)
        monthedit = QLineEdit(self)
        yearedit.resize(40, 20)
        monthedit.resize(40, 20)
        yearedit.move(120, 100)
        monthedit.move(200, 100)
        yearedit2 = QLineEdit(self)
        monthedit2 = QLineEdit(self)
        yearedit2.resize(40, 20)
        monthedit2.resize(40, 20)
        yearedit2.move(120, 130)
        monthedit2.move(200, 130)

        grid = QGridLayout()
        grid.setSpacing(10)

        subjectcombo = QComboBox(self)
        subjectcombo.addItem("Mathemastics")
        subjectcombo.addItem("Physics")
        subjectcombo.addItem("Computer Science")
        subjectcombo.addItem("Quantitative Biology")
        subjectcombo.addItem("Quantitative Finance")
        subjectcombo.addItem("Statistics")
        subjectcombo.resize(subjectcombo.sizeHint())
        subjectcombo.move(120, 60)

        selectcombo = QComboBox(self)
        selectcombo.addItem("论文标题")
        selectcombo.addItem("关键词")
        selectcombo.addItem("arxivID")
        selectcombo.resize(80, 30)
        selectcombo.move(10, 300)

        self.setLayout(grid)

        # 显示窗口
        self.show()

    # 控制窗口显示在屏幕中心的方法
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # def statisticsBtnClicked(self):


    # def monthvisualizationBtnClicked(self):
    #     sender = self.sender()
    #     self.statusBar().showMessage(sender.text() + ' was pressed')
    #
    # def yearvisualizationBtnClicked(self):
    #     sender = self.sender()
    #     self.statusBar().showMessage(sender.text() + ' was pressed')
    #
    # def trendBtnClicked(self):
    #     sender = self.sender()
    #     self.statusBar().showMessage(sender.text() + ' was pressed')
    #
    def downloadBtnClicked(self):
        text = self.pathedit.text()
        self.searchedit.setText(str(text))
        # if path:
        #     reply = QMessageBox.question(self, '信息', path)
        # else:
        #     reply = QMessageBox.question(self, '信息', "请重新输入")
        # reply = QMessageBox.question(self, '信息', '确认退出吗？',
        #                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    def showDialog(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                'open file',
                                                                self.cwd,  # 起始路径
                                                                "All Files (*);;Text Files (*.txt)")

        self.pathedit.setText(fileName_choose)



if __name__ == '__main__':
    # 每一pyqt5应用程序必须创建一个应用程序对象。sys.argv参数是一个列表，从命令行输入参数。
    app = QApplication(sys.argv)

    ex = Example()

    # # QWidget部件是pyqt5所有用户界面对象的基类。他为QWidget提供默认构造函数。默认构造函数没有父类。
    # w = QWidget()
    # # resize()方法调整窗口的大小。这离是250px宽150px高
    # w.resize(500, 300)
    # # move()方法移动窗口在屏幕上的位置到x = 300，y = 300坐标。
    # w.move(300, 300)
    # # 设置窗口的标题
    # w.setWindowTitle('论文下载神器')
    # # 显示在屏幕上
    # w.show()

    # 系统exit()方法确保应用程序干净的退出
    # 的exec_()方法有下划线。因为执行是一个Python关键词。因此，exec_()代替
    sys.exit(app.exec_())