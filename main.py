import sys, os
from time import sleep
from PyQt5.QtWidgets import (QApplication, QWidget, QDialog, QPushButton, QMenuBar, QAction, QFileDialog, QTextEdit, QLabel, QSlider, QRadioButton,
                             QActionGroup)
from PyQt5.QtGui import (QPainter, QPen, QPainterPath, QIcon, QMouseEvent)
from PyQt5.QtCore import (Qt, QPointF, QRect, QLine)

global graph_config
graph_config = None

#circle size - 40

class NewGraphWindowText(QDialog):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 700, 250)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        self.setWindowTitle("New Graph")
        self.setWindowIcon(QIcon("icon.jpeg"))

        self.okbtn = QPushButton("OK", self)
        self.okbtn.setGeometry(self.width()-self.okbtn.width(), self.height()-self.okbtn.height(), self.okbtn.width(), self.okbtn.height())
        self.okbtn.clicked.connect(self.OkClicked)

        self.readme = QTextEdit(self)
        self.readme.setGeometry(0, 0, 449, self.height()-self.okbtn.height())
        self.readme.setReadOnly(True)
        with open("README.txt") as f: self.readme.setText(f.read())

        self.graph_conf_text = QTextEdit(self)
        self.graph_conf_text.setGeometry(451, 0, 249, self.height()-self.okbtn.height())

    def OkClicked(self, e):
        if len(self.graph_conf_text.toPlainText()) == 0: self.close(); return
        global graph_config
        graph_config = self.graph_conf_text.toPlainText().split("\n")
        self.close()

class NewGraphWindowGraphic(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("MyStyleSheet.qss")

        self.coords, self.lines, self.changable_lines, self.graph = [], [], [], []
        self.fromm, self.too, self.line_num, self.line_added = None, None, None, False
        self.mv, self.xdif, self.ydif = None, None, None

        self.setGeometry(0, 0, 800, 500)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        self.setWindowTitle("New Graph")
        self.setWindowIcon(QIcon("icon.jpeg"))

        self.vertice_add_btn = QRadioButton("Add Vertice", self)
        self.vertice_remove_btn = QRadioButton("Remove Vertice", self)
        self.line_add_btn = QRadioButton("Add Line", self)
        self.line_remove_btn = QRadioButton("Remove Line", self)
        self.drag_btn = QRadioButton("Drag", self)
        self.reset_btn = QPushButton("Reset", self); self.reset_btn.clicked.connect(self.Reset_Clicked)
        self.ok_btn = QPushButton("OK", self); self.ok_btn.clicked.connect(self.OK_Cliked)

        self.vertice_add_btn.setChecked(True)

        self.vertice_add_btn.setGeometry(self.width()-120, 30, 120, self.vertice_add_btn.height())
        self.vertice_remove_btn.setGeometry(self.width()-120, self.vertice_add_btn.height()+self.vertice_remove_btn.height(), 120,
                                            self.vertice_remove_btn.height())
        self.line_add_btn.setGeometry(self.width()-120, self.vertice_add_btn.height()+self.vertice_remove_btn.height()+self.line_add_btn.height(),
                                      120, self.line_add_btn.height())
        self.line_remove_btn.setGeometry(self.width()-120, self.vertice_add_btn.height()+self.vertice_remove_btn.height()+self.line_add_btn.height()+self.line_remove_btn.height(),
                                         120, self.line_remove_btn.height())
        self.drag_btn.setGeometry(self.width()-120, self.vertice_add_btn.height()+self.vertice_remove_btn.height()+self.line_add_btn.height()+self.line_remove_btn.height()+self.drag_btn.height(),
                                  120, self.drag_btn.height())
        self.ok_btn.setGeometry(self.width()-120, self.height()-self.ok_btn.height(), 120, self.ok_btn.height())
        self.reset_btn.setGeometry(self.width()-120, self.height()-(self.ok_btn.height()+self.reset_btn.height()), 120, self.reset_btn.height())

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBackground(Qt.white)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.setBrush(Qt.red)

        for line in self.lines:
            path = QPainterPath()
            path.moveTo(*line[0]); path.lineTo(*line[1])
            painter.drawPath(path)

        for x in self.coords:
            painter.drawEllipse(x[0] - 20, x[1] - 20, 40, 40)
            painter.drawText(x[0] - 10, x[1] - 10, 20, 20, Qt.AlignCenter, str(self.coords.index(x) + 1))

    def mousePressEvent(self, e: QMouseEvent):
        if self.vertice_add_btn.isChecked():
            self.coords.append([e.pos().x(), e.pos().y()])
            self.update()
        elif self.vertice_remove_btn.isChecked():
            for x in self.coords:
                if (x[0]-20 <= e.pos().x() <= x[0]+20) and (x[1]-20 <= e.pos().y() <= x[1] + 20):
                    self.coords.pop(self.coords.index(x))
                    self.lines = [line for line in self.lines if x not in line]
                    self.update()
                    return
        elif self.line_add_btn.isChecked():
            for x in self.coords:
                if (x[0] - 20 <= e.pos().x() <= x[0] + 20) and (x[1] - 20 <= e.pos().y() <= x[1] + 20):
                    self.fromm = x
                    self.lines.append([x, x])
                    self.line_num = self.lines.index([x, x])
                    return
        elif self.line_remove_btn.isChecked():
            for line in self.lines:
                if ((line[0][0] <= e.pos().x() <= line[1][0]) or (line[1][0] <= e.pos().x() <= line[0][0])) \
                        and ((line[0][1] <= e.pos().y() <= line[1][1]) or (line[1][1] <= e.pos().y() <= line[0][1])):
                    self.lines.pop(self.lines.index(line))
                    self.update()
                    break
        elif self.drag_btn.isChecked():
            try:
                if self.mv == None and len(self.coords) != 0:
                    for x in self.coords:
                        if (x[0] - 20 <= e.pos().x() <= x[0] + 20) and (x[1] - 20 <= e.pos().y() <= x[1] + 20):
                            self.mv = self.coords.index(x)
                            self.xdif = e.pos().x() - x[0]
                            self.ydif = e.pos().y() - x[1]
                            self.update()
                            break
                else:
                    self.mv, self.xdif, self.ydif = None, None, None
            except: return
    def mouseMoveEvent(self, e: QMouseEvent):
        if self.line_add_btn.isChecked() and self.fromm != None:
            self.too = [e.pos().x(), e.pos().y()]
            self.lines[self.line_num] = [self.fromm, self.too]
            self.update()
        if self.drag_btn.isChecked():
            try:
                if self.mv != None:
                    for line in self.lines:
                        if self.coords[self.mv] in line: self.changable_lines.append([self.lines.index(line), line.index(self.coords[self.mv])])
                    self.coords[self.mv] = [e.pos().x() - self.xdif, e.pos().y() - self.ydif]
                    self.UpdateLines()
                    self.update()
            except: return

    def mouseReleaseEvent(self, e: QMouseEvent):
        if self.line_add_btn.isChecked() and [self.fromm, self.too] != [None, None]:
            for x in self.coords:
                if (x[0] - 20 <= e.pos().x() <= x[0] + 20) and (x[1] - 20 <= e.pos().y() <= x[1] + 20):
                    self.lines[self.line_num] = [self.fromm, x]
                    self.line_added = True
                    self.update()
                    break

            if not self.line_added:
                self.lines.pop(self.line_num)
                self.update()
            else: self.line_added = False
        if self.drag_btn.isChecked():
            try:
                if self.mv != None:
                    self.coords[self.mv] = [e.pos().x() - self.xdif, e.pos().y() - self.ydif]
                    self.UpdateLines()
                    self.update()
                    self.mv, self.xdif, self.ydif = None, None, None
                    self.changable_lines = []
            except: return

    def Reset_Clicked(self, e):
        self.coords, self.lines, self.changable_lines = [], [], []
        self.fromm, self.too, self.line_num, self.line_added = None, None, None, False
        self.mv, self.xdif, self.ydif = None, None, None
        self.update()

    def OK_Cliked(self, e):
        global graph_config
        self.graph = [[str(x+1)] for x in range(len(self.coords))]
        for line in self.lines:
            a, b = self.coords.index(line[0]), self.coords.index(line[1])
            self.graph[a].append(str(b+1))
            self.graph[b].append(str(a+1))
        self.graph = [" ".join(x) for x in self.graph]
        self.coords = [" ".join(list(map(str, x))) for x in self.coords]
        graph_config = [str(len(self.coords)), *self.graph, "COORDS", *self.coords]
        self.close()
        self.Reset_Clicked(None)

    def UpdateLines(self):
        for i, p in self.changable_lines:
            if p == 1: self.lines[i] = [self.lines[i][0], self.coords[self.mv]]
            else: self.lines[i] = [self.coords[self.mv], self.lines[i][1]]

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.new_graph_dialog_text = NewGraphWindowText()
        self.new_graph_dialog_graphic = NewGraphWindowGraphic()

        self.mv, self.xdif, self.ydif, self.start_vertice = None, None, None, None
        self.from_file, self.graph_present = False, False
        self.used, self.con_points, self.tin, self.tout, self.lines = [], [], [], [], []
        self.algo_starts, self.timer = 0, 0
        self.paths, self.coords = [], []

        self.setGeometry(300, 300, 1000, 500)
        self.move(QApplication.desktop().screen().rect().center()-self.rect().center())
        self.setWindowTitle("Articulation Points")
        self.setWindowIcon(QIcon("icon.jpeg"))

        self.menubar = QMenuBar(self)
        self.filemenu = self.menubar.addMenu("File")
        self.newfile = self.filemenu.addMenu("New")
        self.newtext = self.newfile.addAction("New Graph(Text)")
        self.newgraphic = self.newfile.addAction("New Graph(Graphical)")
        self.openfile = self.filemenu.addAction("Open")
        self.savefile = self.filemenu.addAction("Save")
        self.exitfile = self.filemenu.addAction("Exit")

        self.filemenu.triggered[QAction].connect(self.ProcessTrigger)

        self.startalgobtn = QPushButton("Start", self)
        self.startalgobtn.setGeometry(self.width()-self.startalgobtn.width(), self.menubar.height(),self.startalgobtn.width(),
                                      self.startalgobtn.height())
        self.startalgobtn.setVisible(False)
        self.startalgobtn.clicked.connect(self.Algo)

        self.resetgraphbtn = QPushButton("Reset Graph", self)
        self.resetgraphbtn.setGeometry(self.width() - self.startalgobtn.width(), self.menubar.height() + self.resetgraphbtn.height(),
                                      self.startalgobtn.width(), self.startalgobtn.height())
        self.resetgraphbtn.setVisible(False)
        self.resetgraphbtn.clicked.connect(self.Reset)

        self.exitbtn = QPushButton("Exit", self)
        self.exitbtn.setGeometry(self.width()-self.startalgobtn.width(), self.menubar.height() + self.resetgraphbtn.height() + self.exitbtn.height(),
                                 self.startalgobtn.width(), self.startalgobtn.height())
        self.exitbtn.setVisible(False)
        self.exitbtn.clicked.connect(self.Exit)

        self.con_points_lbl = QLabel("meh", self)
        self.con_points_lbl.setVisible(False)

        self.sleepslider = QSlider(Qt.Horizontal, self)
        self.sleepslider.setMinimum(1)
        self.sleepslider.setMaximum(20)
        self.sleepslider.setValue(10)
        self.sleepslider.setTickPosition(QSlider.TicksBelow)
        self.sleepslider.setTickInterval(1)
        self.sleepslider.setGeometry(0, self.height()-self.con_points_lbl.height(), 500,
                                     self.sleepslider.height())

        self.modelbl = QLabel("Mode:", self)
        self.modelbl.setGeometry(0, self.height()-self.sleepslider.height()-40, 50, self.modelbl.height())
        self.editmode = QRadioButton("Edit", self)
        self.editmode.setGeometry(52, self.height()-self.sleepslider.height()-40, 50, self.editmode.height())
        self.editmode.setChecked(True)
        self.choosemode = QRadioButton("Choose starting vertice", self)
        self.choosemode.setGeometry(104, self.height()-self.sleepslider.height()-40, 160, self.choosemode.height())

        self.editmode.setVisible(False)
        self.modelbl.setVisible(False)
        self.choosemode.setVisible(False)
        self.sleepslider.setVisible(False)

        self.show()

    def ProcessTrigger(self, q):
        if q == self.newtext: self.NewFile("t")
        if q == self.newgraphic: self.NewFile("g")
        if q == self.openfile: self.OpenFile()
        if q == self.savefile: self.SaveFile()
        if q == self.exitfile: self.Exit()

    def mousePressEvent(self, e: QMouseEvent):
        QApplication.processEvents()
        if self.editmode.isChecked():
            try:
                if self.mv == None and self.graph_present:
                    for x in self.coords:
                        if (x[0] - 20 <= e.pos().x() <= x[0] + 20) and (x[1] - 20 <= e.pos().y() <= x[1] + 20):
                            self.mv = self.coords.index(x)
                            self.xdif = e.pos().x() - x[0]
                            self.ydif = e.pos().y() - x[1]
                            self.UpdatePath()
                            self.update()
                            break
                else:
                    self.mv, self.xdif, self.ydif = None, None, None
            except:
                return

        elif self.choosemode.isChecked():
            for coord in self.coords:
                if (coord[0]-20 <= e.pos().x() <= coord[0] + 20) and (coord[1]-20 <= e.pos().y() <= coord[1] + 20):
                    coord[2] = Qt.darkMagenta
                    self.coords[self.start_vertice][2] = Qt.red
                    self.start_vertice = self.coords.index(coord)
                    self.update()


    def mouseMoveEvent(self, e: QMouseEvent):
        QApplication.processEvents()
        if self.editmode.isChecked():
            try:
                if self.mv != None:
                    self.coords[self.mv] = [e.pos().x() - self.xdif, e.pos().y() - self.ydif, self.coords[self.mv][2]]
                    self.UpdatePath()
                    self.update()
            except: return

    def mouseReleaseEvent(self, e: QMouseEvent):
        QApplication.processEvents()
        if self.editmode.isChecked():
            try:
                if self.mv != None:
                    self.coords[self.mv] = [e.pos().x() - self.xdif, e.pos().y() - self.ydif, self.coords[self.mv][2]]
                    self.UpdatePath()
                    self.update()
                    self.mv, self.xdif = None, None
            except: return

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBackground(Qt.white)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.setBrush(Qt.NoBrush)
        for path in self.paths:
            painter.drawPath(path)
        for coord in self.coords:
            painter.setBrush(coord[2])
            painter.drawEllipse(coord[0] - 20, coord[1] - 20, 40, 40)
            painter.drawText(coord[0]-10, coord[1]-10, 20, 20,
                             Qt.AlignCenter, str(self.coords.index(coord)+1))
        painter.setPen(QPen(Qt.darkYellow, 4, Qt.SolidLine))
        for i in range(len(self.tin)):
            painter.drawText(self.coords[i][0] + 20, self.coords[i][1] - 40//3, 40, 10,
                             Qt.AlignCenter, str(self.tin[i])+"/"+str(self.tout[i]))

    def UpdatePath(self):
        self.paths = []
        for line in self.lines:
            path = QPainterPath()
            path.moveTo(QPointF(*self.coords[line[0]][:2]))
            path.lineTo(QPointF(*self.coords[line[1]][:2]))
            self.paths.append(path)

    def ResetGraph(self):
        self.paths, self.coords, self.tin, self.tout, self.con_points, self.used = [], [], [], [], [], []
        self.con_points_lbl.setVisible(False)
        self.start_vertice = None
        self.editmode.setVisible(False)
        self.modelbl.setVisible(False)
        self.choosemode.setVisible(False)
        self.sleepslider.setVisible(False)
        self.update()

    def Reset(self, e):
        self.coords = [[*coord[:2], Qt.red] for coord in self.coords]
        self.coords[0][2] = Qt.darkMagenta
        self.start_vertice = 0
        self.tin = self.tout = []
        self.update()

    def NewFile(self, mode):
        self.ResetGraph()
        global graph_config
        self.from_file = False
        if mode == "t": self.new_graph_dialog_text.exec_()
        else: self.new_graph_dialog_graphic.exec_()
        if graph_config == None: return
        self.ReadGraph()

    def OpenFile(self):
        self.ResetGraph()
        try:
            self.from_file = True
            global graph_config
            graph_config = QFileDialog.getOpenFileName(self, "Open File", os.getcwd(), "Text Files (*.txt)")[0]
            self.ReadGraph()
        except: return

    def SaveFile(self):
        global graph_config
        if graph_config == None: return
        else:
            name = list(QFileDialog.getSaveFileName(self, "Save File", os.getcwd(), "Text Files (*.txt)"))
            if ".txt" not in name[0]: name[0] += ".txt"
            with open(name[0], "w") as f:
                f.write(str(self.num_of_peaks)+"\n")
                f.write("\n".join(self.info))

    def Exit(self): QApplication.instance().quit()

    def ReadGraph(self):
        try:
            global graph_config
            movetopoint = None
            startlinevertice = None

            if self.from_file:
                with open(graph_config) as f:
                    data = f.readlines()
            else: data = graph_config

            self.num_of_peaks, *self.info = data
            self.num_of_peaks = int(self.num_of_peaks)
            self.used = [False for x in range(self.num_of_peaks)]
            try: ix = self.info.index("COORDS\n")
            except: ix = self.info.index("COORDS")
            vertices_raw = self.info[:ix]
            coords_raw = self.info[ix + 1:]
            vertices = [list(map(int, vertice.split())) for vertice in vertices_raw]
            coords = [list(map(int, coord.split())) for coord in coords_raw]
            self.graph = [vertice[1::] for vertice in vertices]
            for vertice in vertices:
                path = QPainterPath()
                for i, p in enumerate(vertice):
                    point = QPointF(*coords[p-1])
                    if i == 0:
                        movetopoint = point
                        startlinevertice = p-1
                        path.moveTo(point)
                    else:
                        path.lineTo(point)
                        path.moveTo(movetopoint)
                        self.lines.append([startlinevertice, p-1])
                self.paths.append(path)

            for i in range(len(coords)): self.coords.append([*coords[i], Qt.red])
            self.coords[0] = [*self.coords[0][:2], Qt.darkMagenta]
            self.start_vertice = 0

            self.update()

            self.startalgobtn.setVisible(True)
            self.resetgraphbtn.setVisible(True)
            self.exitbtn.setVisible(True)
            self.graph_present = True
            self.editmode.setVisible(True)
            self.modelbl.setVisible(True)
            self.choosemode.setVisible(True)
            self.sleepslider.setVisible(True)
        except: return

    def UpdateSleep(self):
        self.update()
        QApplication.processEvents()
        sleep(self.sleepslider.value()/10)

    def Algo(self, e):
        QApplication.processEvents()
        self.modelbl.setVisible(False)
        self.editmode.setVisible(False)
        self.choosemode.setVisible(False)
        self.algo_starts += 1
        if self.algo_starts > 1:
            QApplication.processEvents()
            self.con_points_lbl.setVisible(False)
            for coord in self.coords: coord[2] = Qt.red
            self.timer = 0
            self.tin = self.tout = [0 for x in range(self.num_of_peaks)]
            self.update()
        self.used = [False for i in range(self.num_of_peaks)]
        self.tin = [0 for i in range(self.num_of_peaks)]
        self.tout = [0 for i in range(self.num_of_peaks)]

        def dfs(v, p=-1):
            self.used[v] = True
            self.coords[v][2] = Qt.yellow
            self.tin[v] = self.tout[v] = self.timer + 1
            QApplication.processEvents()
            self.UpdateSleep()

            self.timer += 1
            children = 0
            QApplication.processEvents()
            for i in range(0, len(self.graph[v])):
                to = self.graph[v][i]-1
                if to == p: continue
                if self.used[to]:
                    self.tout[v] = min(self.tout[v], self.tin[to])
                    QApplication.processEvents()
                    self.UpdateSleep()
                else:
                    QApplication.processEvents()
                    dfs(to, v)
                    self.tout[v] = min(self.tout[v], self.tout[to])
                    if self.tout[to] >= self.tin[v] and p != -1:
                        self.con_points.append(v + 1)
                        self.coords[v][2] = Qt.green
                    children += 1
                    QApplication.processEvents()
                    self.UpdateSleep()
            if (p == -1 and children > 1 and (v + 1) not in self.con_points):
                self.con_points.append(v + 1)
                self.coords[v][2] = Qt.green
                QApplication.processEvents()
                self.UpdateSleep()

        dfs(self.start_vertice)

        for i in range(self.num_of_peaks):
            QApplication.processEvents()
            if not self.used[i]:
                QApplication.processEvents()
                dfs(i)

        if len(self.con_points) == 0:
            self.con_points_lbl.setText("Connection point(-s) is(are): None")
        else:
            self.con_points_lbl.setText("Connection point(-s) is(are): " + " ".join(list(map(str, set(self.con_points)))))

        self.con_points_lbl.setGeometry(self.width()-400, self.height()-self.con_points_lbl.height(),
                                        400, self.con_points_lbl.height())
        self.con_points_lbl.setVisible(True)

        self.modelbl.setVisible(True)
        self.editmode.setVisible(True)
        self.choosemode.setVisible(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    con_point_app = MainWindow()

    sys.exit(app.exec_())