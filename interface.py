import os.path
from explain import Control
import logging

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPoint,
    QPointF,
    pyqtSignal,
    QEvent,
    QSize,
    QTimer,
)
from PyQt6.QtGui import (
    QImage,
    QPixmap,
    QPainterPath,
    QMouseEvent,
    QPen,
    QCursor,
    QFont
)
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QFileDialog,
    QSizePolicy,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QScrollArea,
)

app_bg_color = "#9bcfb8"
textbox_bg_color_1 = "#ffffff"
textbox_bg_color_2 = "#badece"
text_color_light_gray = "#333333"
text_color_dark_gray = "#1a1a1a"
text_color_title = "#072a24"
button_bg_color = "#7fb174"
slider_handle_color = "#ddeee6"

# UI definition
class Ui_Dialog(object):
    """Set QEP Image To First Query: setImgToViewerA(filepath:string)
    Set QEP Image To Second Query: setImgToViewerB(filepath:string)
    Send Text Results: setTextResults(formatted_QA : str, formatted_QB : str,
                                        explain_QA : str, explain_QB : str,
                                        query_diff_ansi : str, qep_diff: str)
    where query_diff_ansi is ANSI code in string format

    get the query inputs: getQueryTexts(), returns a tuple of two query strings

    TODO: modify onClickGetPlanButton
    """

    def __init__(self, Dialog, host, database, user, password, port):
        Dialog.setObjectName("ABC")
        Dialog.resize(1600, 800)
        Dialog.setMinimumSize(QtCore.QSize(800, 600))
        Dialog.setBaseSize(QtCore.QSize(0, 0))


        Dialog.setStyleSheet("background-color: #ffffcc;")
        
        Dialog.setStyleSheet("background-color: #ffffcc;")
        Dialog.setAutoFillBackground(True)

        # dialog includes content and "get plan" push button
        self.dialog_VerLy = QtWidgets.QVBoxLayout(Dialog)
        self.dialog_VerLy.setObjectName("dialog_VerLy")

        # content includes query input, tree image and difference text
        self.content_HorLy = QtWidgets.QHBoxLayout()
        self.content_HorLy.setObjectName("content_HorLy")

        self.scroll_area = NoWheelScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_widget.setMinimumWidth(
            750
        )  # Set the minimum width of scrolling widget
        self.content_VerLy = QtWidgets.QVBoxLayout(self.scroll_widget)
        self.content_VerLy.setObjectName("content_VerLy")

        self.two_Query_HorLy = QtWidgets.QHBoxLayout()
        self.two_Query_HorLy.setObjectName("two_Query_HorLy")

        self.setQueryA_UI(Dialog)
        self.two_Query_HorLy.addLayout(self.query_A_VerLy)

        spacer_between_queries = QtWidgets.QSpacerItem(
            40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.two_Query_HorLy.addItem(spacer_between_queries)

        self.setQueryB_UI(Dialog)
        self.two_Query_HorLy.addLayout(self.query_B_VerLy)

        self.content_VerLy.addLayout(self.two_Query_HorLy)

        self.tree_info = QtWidgets.QLabel()
        self.tree_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheetInfoLabel(self.tree_info)
        self.content_VerLy.addWidget(self.tree_info)

        empty_verLy = QtWidgets.QVBoxLayout()
        empty_verLy.setObjectName("empty_verLy1")
        self.content_VerLy.addLayout(empty_verLy)

        self.two_Explain_HorLy = QtWidgets.QHBoxLayout()
        self.two_Explain_HorLy.setObjectName("two_Explain_HorLy")

        self.setExplainA_UI(Dialog)
        self.two_Explain_HorLy.addLayout(self.explain_A_VerLy)

        self.two_Explain_HorLy.addItem(spacer_between_queries)

        self.setExplainB_UI(Dialog)
        self.two_Explain_HorLy.addLayout(self.explain_B_VerLy)

        empty_verLy = QtWidgets.QVBoxLayout()
        empty_verLy.setObjectName("empty_verLy2")
        self.two_Explain_HorLy.addLayout(empty_verLy)
        self.content_VerLy.addLayout(self.two_Explain_HorLy)

        self.difference_verLy = QtWidgets.QVBoxLayout()
        self.difference_verLy.setObjectName("difference_verLy")

        # init query difference output text box
        self.initQueryDifference(Dialog)

        # init QEP difference output text box
        self.initQEPDifference(Dialog)

        self.content_VerLy.addLayout(self.difference_verLy)

        self.scroll_area.setWidget(self.scroll_widget)
        self.content_HorLy.addWidget(self.scroll_area)
        self.dialog_VerLy.addLayout(self.content_HorLy)

        # set Get Plan Button
        self.setGetPlanBtnUI(Dialog)

        # set stylesheet
        self.setStyleSheetUI(Dialog)

        # set contents
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.my_control = Control(host, database, user, password, port)
        
        self.getPlan_PushBtn.clicked.connect(self.onClickGetPlanButton)

    

    def setQueryA_UI(self, Dialog):
        self.query_A_VerLy = QtWidgets.QVBoxLayout()
        self.query_A_VerLy.setObjectName("query_A_VerLy")

        self.textlabel_query_A = QtWidgets.QLabel(Dialog)
        self.textlabel_query_A.setScaledContents(False)
        self.textlabel_query_A.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_query_A.setObjectName("textlabel_query_A")
        self.query_A_VerLy.addWidget(self.textlabel_query_A)

        self.query_A_textEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.query_A_textEdit.setObjectName("query_A_textEdit")
        self.query_A_textEdit.setAutoFillBackground(True)
        self.query_A_textEdit.setMinimumHeight(150)
        self.query_A_VerLy.addWidget(self.query_A_textEdit)

        spacer_between_query_tree_A = QtWidgets.QSpacerItem(
            40, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.query_A_VerLy.addItem(spacer_between_query_tree_A)

        self.textlabel_QEP_A = QtWidgets.QLabel(Dialog)
        self.textlabel_QEP_A.setScaledContents(False)
        self.textlabel_QEP_A.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_QEP_A.setObjectName("textlabel_QEP_A")
        self.query_A_VerLy.addWidget(self.textlabel_QEP_A)

        self.imgViewer_A = QtImageViewer()
        self.initImgViewer(self.imgViewer_A)
        self.query_A_VerLy.addWidget(self.imgViewer_A)

    def setExplainA_UI(self, Dialog):

        self.explain_A_VerLy = QtWidgets.QVBoxLayout()
        self.explain_A_VerLy.setObjectName("explain_A_VerLy")

        spacer_between_tree_explain_A = QtWidgets.QSpacerItem(
            40, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.explain_A_VerLy.addItem(spacer_between_tree_explain_A)

        self.textlabel_explain_A = QtWidgets.QLabel(Dialog)
        self.textlabel_explain_A.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_explain_A.setObjectName("textlabel_explain_A")
        self.explain_A_VerLy.addWidget(self.textlabel_explain_A)

        self.explain_A_TextBrowser = QtWidgets.QTextBrowser(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.explain_A_TextBrowser.sizePolicy().hasHeightForWidth()
        )
        self.explain_A_TextBrowser.setSizePolicy(sizePolicy)
        self.explain_A_TextBrowser.setMinimumHeight(250)
        self.explain_A_TextBrowser.setObjectName("explain_A_TextBrowser")
        self.explain_A_TextBrowser.setAutoFillBackground(True)
        self.explain_A_VerLy.addWidget(self.explain_A_TextBrowser)


    def setQueryB_UI(self, Dialog):
        self.query_B_VerLy = QtWidgets.QVBoxLayout()
        self.query_B_VerLy.setObjectName("query_B_VerLy")

        self.textlabel_query_B = QtWidgets.QLabel(Dialog)
        self.textlabel_query_B.setScaledContents(False)
        self.textlabel_query_B.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_query_B.setObjectName("textlabel_query_B")
        self.query_B_VerLy.addWidget(self.textlabel_query_B)

        self.query_B_textEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.query_B_textEdit.setObjectName("query_B_textEdit")
        self.query_B_textEdit.setAutoFillBackground(True)
        self.query_B_textEdit.setMinimumHeight(150)
        self.query_B_VerLy.addWidget(self.query_B_textEdit)

        spacer_between_query_tree_B = QtWidgets.QSpacerItem(
            40, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.query_B_VerLy.addItem(spacer_between_query_tree_B)

        self.textlabel_QEP_B = QtWidgets.QLabel(Dialog)
        self.textlabel_QEP_B.setScaledContents(False)
        self.textlabel_QEP_B.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_QEP_B.setObjectName("textlabel_QEP_B")
        self.query_B_VerLy.addWidget(self.textlabel_QEP_B)

        self.imgViewer_B = QtImageViewer()
        self.initImgViewer(self.imgViewer_B)
        self.query_B_VerLy.addWidget(self.imgViewer_B)

    def setExplainB_UI(self, Dialog):

        self.explain_B_VerLy = QtWidgets.QVBoxLayout()
        self.explain_B_VerLy.setObjectName("explain_B_VerLy")

        spacer_between_tree_explain_B = QtWidgets.QSpacerItem(
            40, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.explain_B_VerLy.addItem(spacer_between_tree_explain_B)

        self.textlabel_explain_B = QtWidgets.QLabel(Dialog)
        self.textlabel_explain_B.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_explain_B.setObjectName("textlabel_explain_B")
        self.explain_B_VerLy.addWidget(self.textlabel_explain_B)

        self.explain_B_TextBrowser = QtWidgets.QTextBrowser(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.explain_B_TextBrowser.sizePolicy().hasHeightForWidth()
        )
        self.explain_B_TextBrowser.setSizePolicy(sizePolicy)
        self.explain_B_TextBrowser.setMinimumHeight(250)
        self.explain_B_TextBrowser.setObjectName("explain_B_TextBrowser")
        self.explain_B_TextBrowser.setAutoFillBackground(True)
        self.explain_B_VerLy.addWidget(self.explain_B_TextBrowser)


    def initQueryDifference(self, Dialog):
        before_difference_spacer = QtWidgets.QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.difference_verLy.addItem(before_difference_spacer)

        self.textlabel_query_difference = QtWidgets.QLabel(Dialog)
        self.textlabel_query_difference.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_query_difference.setObjectName("textlabel_query_difference")
        self.difference_verLy.addWidget(self.textlabel_query_difference)

        self.query_difference_TextBrowser = QtWidgets.QTextBrowser(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.query_difference_TextBrowser.sizePolicy().hasHeightForWidth()
        )
        self.query_difference_TextBrowser.setSizePolicy(sizePolicy)
        self.query_difference_TextBrowser.setMinimumHeight(250)
        self.query_difference_TextBrowser.setObjectName("query_difference_TextBrowser")
        self.query_difference_TextBrowser.setAutoFillBackground(True)
        self.difference_verLy.addWidget(self.query_difference_TextBrowser)

    def initQEPDifference(self, Dialog):
        before_QEP_difference_spacer = QtWidgets.QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.difference_verLy.addItem(before_QEP_difference_spacer)

        self.textlabel_QEP_difference = QtWidgets.QLabel(Dialog)
        self.textlabel_QEP_difference.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textlabel_QEP_difference.setObjectName("textlabel_QEP_difference")
        self.difference_verLy.addWidget(self.textlabel_QEP_difference)

        self.QEP_difference_TextBrowser = QtWidgets.QTextBrowser(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.QEP_difference_TextBrowser.sizePolicy().hasHeightForWidth()
        )
        self.QEP_difference_TextBrowser.setSizePolicy(sizePolicy)
        self.QEP_difference_TextBrowser.setMinimumHeight(250)
        self.QEP_difference_TextBrowser.setObjectName("query_difference_TextBrowser")
        self.QEP_difference_TextBrowser.setAutoFillBackground(True)
        self.difference_verLy.addWidget(self.QEP_difference_TextBrowser)

    def setGetPlanBtnUI(self, Dialog):
        before_GetPlan_spacer = QtWidgets.QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.dialog_VerLy.addItem(before_GetPlan_spacer)

        self.getPlan_button_layout = QtWidgets.QHBoxLayout()
        self.getPlan_button_layout.addStretch()

        self.getPlan_PushBtn = QtWidgets.QPushButton(Dialog)
        self.getPlan_PushBtn.setMinimumSize(QtCore.QSize(250, 30))
        self.getPlan_PushBtn.setMaximumSize(QtCore.QSize(250, 30))
        self.getPlan_PushBtn.setMouseTracking(False)
        self.getPlan_PushBtn.setObjectName("getPlan_PushBtn")
        self.setStyleSheetPushButton(self.getPlan_PushBtn)
        self.getPlan_PushBtn.setAutoFillBackground(True)

        self.getPlan_button_layout.addWidget(self.getPlan_PushBtn)
        self.getPlan_button_layout.addStretch()
        self.dialog_VerLy.addLayout(self.getPlan_button_layout)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle("CZ4031 Project 2")

        self.textlabel_query_A.setText("Input query 1:")
        self.textlabel_query_B.setText("Input query 2:")

        self.textlabel_QEP_A.setText("Query Execution Plan (QEP) tree 1")
        self.textlabel_QEP_B.setText("Query Execution Plan (QEP) tree 2")

        str1 = "Red: different node;                 Green: same node;"
        str2 = "Scroll to zoom in/out;  Left mouse button to drag a rectangle to zoom in;  Single-click right mouse button to zoom out."
        str3 = str1 + "\n" + str2
        self.tree_info.setText(str3)

        self.textlabel_explain_A.setText("QEP 1 explanation")
        self.textlabel_explain_B.setText("QEP 2 explanation")

        self.textlabel_query_difference.setText("Difference based on formatted query")
        self.textlabel_QEP_difference.setText("QEP tree difference")

        self.getPlan_PushBtn.setToolTip(
            _translate(
                "Dialog", '<html><head/><body><p align="center"><br/></p></body></html>'
            )
        )
        self.getPlan_PushBtn.setText("Format query and get QEP")

    def setStyleSheetUI(self, Dialog):
        
        Dialog.setStyleSheet(f"background-color: {app_bg_color};")
        self.setStyleSheetScrollArea(self.scroll_area)

        self.setStyleSheetTextEdit(self.query_A_textEdit)
        self.setStyleSheetTextEdit(self.query_B_textEdit)

        self.setStyleSheetLabel(self.textlabel_query_A)
        self.setStyleSheetLabel(self.textlabel_query_B)
        self.setStyleSheetLabel(self.textlabel_QEP_A)
        self.setStyleSheetLabel(self.textlabel_QEP_B)
        self.setStyleSheetLabel(self.textlabel_explain_A)
        self.setStyleSheetLabel(self.textlabel_explain_B)
        self.setStyleSheetLabel(self.textlabel_query_difference)
        self.setStyleSheetLabel(self.textlabel_QEP_difference)

        self.setStyleSheetTextBrowser(self.explain_A_TextBrowser, textbox_bg_color_1)
        self.setStyleSheetTextBrowser(self.explain_B_TextBrowser, textbox_bg_color_1)
        self.setStyleSheetTextBrowser(self.query_difference_TextBrowser, textbox_bg_color_1)
        self.setStyleSheetTextBrowser(self.QEP_difference_TextBrowser, textbox_bg_color_1)
        

    def setStyleSheetScrollArea(self, scroll_area):
        scroll_area.setStyleSheet(
        f"""
            QScrollBar:vertical {{
                background-color: transparent;
                width: 15px;
                margin: 0px 0 0px 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {slider_handle_color};
                min-height: 20px;
                margin-left: 2px;
                margin-right: 2px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                width: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """
        )

    def setStyleSheetTextEdit(self, text_edit):
        text_edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {textbox_bg_color_2};
                color: {text_color_light_gray};
                font-family: Arial;
                font-size: 14px;
            }}
        """)

    def setStyleSheetLabel(self, label):
        label.setStyleSheet(f"background-color: {app_bg_color}; color: {text_color_title};") 
        font = QFont("Arial", 12, QFont.Weight.Bold) 
        label.setFont(font)

    def setStyleSheetInfoLabel(self, label):
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {app_bg_color};
                color: {text_color_light_gray};
                font-family: Arial;
                font-size: 14px;
            }}
        """)

    def setStyleSheetTextBrowser(self, text_browser, bg_color):
        text_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {bg_color};
                color: {text_color_dark_gray};
                font-family: Arial;
                font-size: 14px;
            }}
        """)

    def setStyleSheetPushButton(self, button):
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_bg_color};
                color: {text_color_dark_gray};
            }}
        """)
        font = QFont("Arial", 12, QFont.Weight.Bold)
        button.setFont(font)


    # returns a string tuple
    def getQueryTexts(self):
        query_a = self.query_A_textEdit.toPlainText()
        query_b = self.query_B_textEdit.toPlainText()
        return (query_a, query_b)

    def setTextResults(
        self,
        formatted_QA: str,
        formatted_QB: str,
        explain_QA: str,
        explain_QB: str,
        qep_diff: str,
        query_diff_strs: list,
        query_diff_colors : list
    ):
        self.query_A_textEdit.setPlainText(formatted_QA)
        self.query_B_textEdit.setPlainText(formatted_QB)

        self.explain_A_TextBrowser.setText(explain_QA)
        self.explain_B_TextBrowser.setText(explain_QB)

        self.QEP_difference_TextBrowser.setText(qep_diff)

        html_text = self.constructHtml(query_diff_strs, query_diff_colors)
        
        self.query_difference_TextBrowser.setHtml(html_text)

    def constructHtml(self, strs: list, color_ids: list) -> str:
        html_prefix = '''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                p.red { color: red; }
                p.green { color: green; }
                p.black { color: black; }
            </style>
        </head>
        <body>
        '''

        html_suffix = '''</body>
        </html>
        '''

        color_strs = ("black", "red", "green")

        html_lines = ""
        line_pre = "    <p class=\""
        line_bet = "\">"
        line_suf = "</p>\n"

        for i in range(len(strs)):
            str = strs[i]
            cid = color_ids[i]
            color = color_strs[cid]
            html_line = line_pre + color + line_bet + str + line_suf
            html_lines = html_lines + html_line
        
        html_text = html_prefix + html_lines + html_suffix
        return html_text
    
    def clearTextResults(self):
        self.explain_A_TextBrowser.setText("")
        self.explain_B_TextBrowser.setText("")

        self.QEP_difference_TextBrowser.setText("") 
        self.query_difference_TextBrowser.setText("")

    def initImgViewer(self, viewer):
        viewer.aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio
        viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        viewer.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        viewer.regionZoomButton = Qt.MouseButton.LeftButton
        viewer.zoomOutButton = Qt.MouseButton.RightButton
        viewer.wheelZoomFactor = 1.25
        viewer.panButton = Qt.MouseButton.MiddleButton
        viewer.setMinimumHeight(250)
        return

    def setImgToViewerA(self, filepath):
        self.imgViewer_A.open(filepath)
        self.imgViewer_A.show()

    def setImgToViewerB(self, filepath):
        self.imgViewer_B.open(filepath)
        self.imgViewer_B.show()

    def queryResults(self):
        try:
            query1, query2 = self.getQueryTexts()
            (
                formatted_q1,
                formatted_q2,
                tree1_explanation,
                tree2_explanation,
                tree_diff_statement,
                query_diff_strs, 
                query_diff_colors
            ) = self.my_control.generate_differences(query1, query2)
        except Exception as e:
            self.explain_A_TextBrowser.setText(e.__class__.__name__ + ':\n' + str(e))
            self.explain_B_TextBrowser.setText(e.__class__.__name__ + ':\n' + str(e))
            self.my_control.db.conn.rollback()
            logging.error(e.__class__.__name__ + ':\n' + str(e))
            return
        
        self.setImgToViewerA("tree1.png")
        self.setImgToViewerB("tree2.png")
        self.setTextResults(
            formatted_QA=formatted_q1,
            formatted_QB=formatted_q2,
            explain_QA=tree1_explanation,
            explain_QB=tree2_explanation,
            qep_diff=tree_diff_statement,
            query_diff_strs=query_diff_strs,
            query_diff_colors =query_diff_colors
        )


    def onClickGetPlanButton(self) -> None:
        self.imgViewer_A.clearImage()
        self.imgViewer_A.show()
        self.imgViewer_B.clearImage()
        self.imgViewer_B.show()
        self.clearTextResults()
        self.queryResults()

        


class NoWheelScrollArea(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def wheelEvent(self, event):
        pass


class QtImageViewer(QGraphicsView):
    """PyQt image viewer widget based on QGraphicsView with mouse zooming/panning and ROIs."""

    # Mouse button signals emit image scene (x, y) coordinates.
    leftMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    middleMouseButtonPressed = pyqtSignal(float, float)
    middleMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)

    # Emitted upon zooming/panning.
    viewChanged = pyqtSignal()

    # Emitted on mouse motion.
    # Emits mouse position over image in image pixel coordinates.
    # !!! setMouseTracking(True) if you want to use this at all times.
    mousePositionOnImageChanged = pyqtSignal(QPoint)

    # Emit index of selected ROI
    roiSelected = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        QGraphicsView.__init__(self, *args, **kwargs)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self._image = None

        self.aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.regionZoomButton = Qt.MouseButton.LeftButton
        self.zoomOutButton = Qt.MouseButton.RightButton
        self.panButton = Qt.MouseButton.MiddleButton
        self.wheelZoomFactor = 1.25

        self.zoomStack = []
        self.zoomCenter = None
        self.resetZoomCenterTimer = QTimer(self)
        self.resetZoomCenterTimer.setSingleShot(True)
        self.resetZoomCenterTimer.timeout.connect(self.resetZoomCenter)

        self._isZooming = False
        self._isPanning = False

        self._pixelPosition = QPoint()
        self._scenePosition = QPointF()

        self.ROIs = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))

    def sizeHint(self):
        return QSize(900, 600)

    def hasImage(self):
        """Returns whether the scene contains an image pixmap."""
        return self._image is not None

    def clearImage(self):
        """Removes the current image pixmap from the scene if it exists."""
        if self.hasImage():
            self.scene.removeItem(self._image)
            self._image = None

    def pixmap(self):
        """Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._image.pixmap()
        return None

    def image(self):
        """Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._image.pixmap().toImage()
        return None

    def setImage(self, image):
        """Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        elif (np is not None) and (type(image) is np.ndarray):
            if qimage2ndarray is not None:
                qimage = qimage2ndarray.array2qimage(image, True)
                pixmap = QPixmap.fromImage(qimage)
            else:
                image = image.astype(np.float32)
                image -= image.min()
                image /= image.max()
                image *= 255
                image[image > 255] = 255
                image[image < 0] = 0
                image = image.astype(np.uint8)
                height, width = image.shape
                bytes = image.tobytes()
                qimage = QImage(bytes, width, height, QImage.Format.Format_Grayscale8)
                pixmap = QPixmap.fromImage(qimage)
        else:
            raise RuntimeError(
                "ImageViewer.setImage: Argument must be a QImage, QPixmap, or numpy.ndarray."
            )
        if self.hasImage():
            self._image.setPixmap(pixmap)
        else:
            self._image = self.scene.addPixmap(pixmap)

        self.setSceneRect(QRectF(pixmap.rect()))
        self.updateViewer()

    def open(self, filepath=None):
        """Load an image from file.
        Without any arguments, loadImageFromFile() will pop up a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if filepath is None:
            filepath, _ = QFileDialog.getOpenFileName(self, "Open image file.")
        if len(filepath) and os.path.isfile(filepath):
            image = QImage(filepath)
            self.setImage(image)

    def updateViewer(self):
        """Show current zoom (if showing entire image, apply current aspect ratio mode)."""
        if not self.hasImage():
            return
        if len(self.zoomStack):
            self.fitInView(
                self.zoomStack[-1], self.aspectRatioMode
            )  # Show zoomed rect.
        else:
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image.

    def clearZoom(self):
        if len(self.zoomStack) > 0:
            self.zoomStack = []
            self.updateViewer()
            self.viewChanged.emit()

    def resizeEvent(self, event):
        """Maintain current zoom on resize."""
        self.updateViewer()

    def mousePressEvent(self, event):
        """Start mouse pan or zoom mode."""
        # Ignore dummy events. e.g., Faking pan with left button ScrollHandDrag.
        dummyModifiers = Qt.KeyboardModifier(
            Qt.KeyboardModifier.ShiftModifier
            | Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        )
        if event.modifiers() == dummyModifiers:
            QGraphicsView.mousePressEvent(self, event)
            event.accept()
            return

        if (self.regionZoomButton is not None) and (
            event.button() == self.regionZoomButton
        ):
            self._pixelPosition = event.pos()  # store pixel position
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            QGraphicsView.mousePressEvent(self, event)
            event.accept()
            self._isZooming = True
            return

        if (self.zoomOutButton is not None) and (event.button() == self.zoomOutButton):
            if len(self.zoomStack):
                self.zoomStack.pop()
                self.updateViewer()
                self.viewChanged.emit()
            event.accept()
            return

        # Start dragging to pan?
        if (self.panButton is not None) and (event.button() == self.panButton):
            self._pixelPosition = event.pos()  # store pixel position
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if self.panButton == Qt.MouseButton.LeftButton:
                QGraphicsView.mousePressEvent(self, event)
            else:
                self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
                dummyModifiers = Qt.KeyboardModifier(
                    Qt.KeyboardModifier.ShiftModifier
                    | Qt.KeyboardModifier.ControlModifier
                    | Qt.KeyboardModifier.AltModifier
                    | Qt.KeyboardModifier.MetaModifier
                )
                dummyEvent = QMouseEvent(
                    QEvent.Type.MouseButtonPress,
                    QPointF(event.pos()),
                    Qt.MouseButton.LeftButton,
                    event.buttons(),
                    dummyModifiers,
                )
                self.mousePressEvent(dummyEvent)
            sceneViewport = (
                self.mapToScene(self.viewport().rect())
                .boundingRect()
                .intersected(self.sceneRect())
            )
            self._scenePosition = sceneViewport.topLeft()
            event.accept()
            self._isPanning = True
            return

        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())

        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Stop mouse pan or zoom mode (apply zoom if valid)."""
        # Ignore dummy events. e.g., Faking pan with left button ScrollHandDrag.
        dummyModifiers = Qt.KeyboardModifier(
            Qt.KeyboardModifier.ShiftModifier
            | Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        )
        if event.modifiers() == dummyModifiers:
            QGraphicsView.mouseReleaseEvent(self, event)
            event.accept()
            return

        # Finish dragging a region zoom box?
        if (self.regionZoomButton is not None) and (
            event.button() == self.regionZoomButton
        ):
            QGraphicsView.mouseReleaseEvent(self, event)
            zoomRect = (
                self.scene.selectionArea().boundingRect().intersected(self.sceneRect())
            )
            # Clear current selection area (i.e. rubberband rect).
            self.scene.setSelectionArea(QPainterPath())
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            # If zoom box is 3x3 screen pixels or smaller, do not zoom and proceed to process as a click release.
            zoomPixelWidth = abs(event.pos().x() - self._pixelPosition.x())
            zoomPixelHeight = abs(event.pos().y() - self._pixelPosition.y())
            if zoomPixelWidth > 3 and zoomPixelHeight > 3:
                if zoomRect.isValid() and (zoomRect != self.sceneRect()):
                    self.zoomStack.append(zoomRect)
                    self.updateViewer()
                    self.viewChanged.emit()
                    event.accept()
                    self._isZooming = False
                    return

        # Finish panning?
        if (self.panButton is not None) and (event.button() == self.panButton):
            if self.panButton == Qt.MouseButton.LeftButton:
                QGraphicsView.mouseReleaseEvent(self, event)
            else:
                # ScrollHandDrag ONLY works with LeftButton, so fake it.
                # Use a bunch of dummy modifiers to notify that event should NOT be handled as usual.
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                dummyModifiers = Qt.KeyboardModifier(
                    Qt.KeyboardModifier.ShiftModifier
                    | Qt.KeyboardModifier.ControlModifier
                    | Qt.KeyboardModifier.AltModifier
                    | Qt.KeyboardModifier.MetaModifier
                )
                dummyEvent = QMouseEvent(
                    QEvent.Type.MouseButtonRelease,
                    QPointF(event.pos()),
                    Qt.MouseButton.LeftButton,
                    event.buttons(),
                    dummyModifiers,
                )
                self.mouseReleaseEvent(dummyEvent)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            if len(self.zoomStack) > 0:
                sceneViewport = (
                    self.mapToScene(self.viewport().rect())
                    .boundingRect()
                    .intersected(self.sceneRect())
                )
                delta = sceneViewport.topLeft() - self._scenePosition
                self.zoomStack[-1].translate(delta)
                self.zoomStack[-1] = self.zoomStack[-1].intersected(self.sceneRect())
                self.viewChanged.emit()
            event.accept()
            self._isPanning = False
            return

        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

        QGraphicsView.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """Show entire image."""
        # Zoom out on double click?
        if (self.zoomOutButton is not None) and (event.button() == self.zoomOutButton):
            self.clearZoom()
            event.accept()
            return

        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())

        QGraphicsView.mouseDoubleClickEvent(self, event)

    def wheelEvent(self, event):
        if self.wheelZoomFactor is not None:
            if self.wheelZoomFactor == 1:
                return
            if event.angleDelta().y() > 0:
                # zoom in
                if len(self.zoomStack) == 0:
                    self.zoomStack.append(self.sceneRect())
                elif len(self.zoomStack) > 1:
                    del self.zoomStack[:-1]
                zoomRect = self.zoomStack[-1]
                # center = zoomRect.center()
                if self.zoomCenter is None:
                    cursor_position_viewport = self.mapFromGlobal(QCursor.pos())
                    cursor_position_scene = self.mapToScene(cursor_position_viewport)
                    self.zoomCenter = cursor_position_scene

                center = self.zoomCenter

                zoomRect.setWidth(zoomRect.width() / self.wheelZoomFactor)
                zoomRect.setHeight(zoomRect.height() / self.wheelZoomFactor)
                zoomRect.moveCenter(center)
                self.zoomStack[-1] = zoomRect.intersected(self.sceneRect())
                self.updateViewer()
                self.viewChanged.emit()
                self.resetZoomCenterTimer.start(200)
            else:
                # zoom out
                if len(self.zoomStack) == 0:
                    # Already fully zoomed out.
                    return
                if len(self.zoomStack) > 1:
                    del self.zoomStack[:-1]
                zoomRect = self.zoomStack[-1]
                center = zoomRect.center()
                zoomRect.setWidth(zoomRect.width() * self.wheelZoomFactor)
                zoomRect.setHeight(zoomRect.height() * self.wheelZoomFactor)
                zoomRect.moveCenter(center)
                self.zoomStack[-1] = zoomRect.intersected(self.sceneRect())
                if self.zoomStack[-1] == self.sceneRect():
                    self.zoomStack = []
                self.updateViewer()
                self.viewChanged.emit()
            event.accept()
            return

        QGraphicsView.wheelEvent(self, event)

    def resetZoomCenter(self):
        self.zoomCenter = None

    def mouseMoveEvent(self, event):
        # Emit updated view during panning.
        if self._isPanning:
            QGraphicsView.mouseMoveEvent(self, event)
            if len(self.zoomStack) > 0:
                sceneViewport = (
                    self.mapToScene(self.viewport().rect())
                    .boundingRect()
                    .intersected(self.sceneRect())
                )
                delta = sceneViewport.topLeft() - self._scenePosition
                self._scenePosition = sceneViewport.topLeft()
                self.zoomStack[-1].translate(delta)
                self.zoomStack[-1] = self.zoomStack[-1].intersected(self.sceneRect())
                self.updateViewer()
                self.viewChanged.emit()

        scenePos = self.mapToScene(event.pos())
        if self.sceneRect().contains(scenePos):
            # Pixel index offset from pixel center.
            x = int(round(scenePos.x() - 0.5))
            y = int(round(scenePos.y() - 0.5))
            imagePos = QPoint(x, y)
        else:
            # Invalid pixel position.
            imagePos = QPoint(-1, -1)
        self.mousePositionOnImageChanged.emit(imagePos)

        QGraphicsView.mouseMoveEvent(self, event)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.CrossCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def addROIs(self, rois):
        for roi in rois:
            self.scene.addItem(roi)
            self.ROIs.append(roi)

    def deleteROIs(self, rois):
        for roi in rois:
            self.scene.removeItem(roi)
            self.ROIs.remove(roi)
            del roi

    def clearROIs(self):
        for roi in self.ROIs:
            self.scene.removeItem(roi)
        del self.ROIs[:]

    def roiClicked(self, roi):
        for i in range(len(self.ROIs)):
            if roi is self.ROIs[i]:
                self.roiSelected.emit(i)
                print(i)
                break

    def setROIsAreMovable(self, tf):
        if tf:
            for roi in self.ROIs:
                roi.setFlags(roi.flags() | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        else:
            for roi in self.ROIs:
                roi.setFlags(
                    roi.flags() & ~QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                )

    def addSpots(self, xy, radius):
        for xy_ in xy:
            x, y = xy_
            spot = EllipseROI(self)
            spot.setRect(x - radius, y - radius, 2 * radius, 2 * radius)
            self.scene.addItem(spot)
            self.ROIs.append(spot)


class EllipseROI(QGraphicsEllipseItem):
    def __init__(self, viewer):
        QGraphicsItem.__init__(self)
        self._viewer = viewer
        pen = QPen(Qt.yellow)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable)

    def mousePressEvent(self, event):
        QGraphicsItem.mousePressEvent(self, event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._viewer.roiClicked(self)


class RectROI(QGraphicsRectItem):
    def __init__(self, viewer):
        QGraphicsItem.__init__(self)
        self._viewer = viewer
        pen = QPen(Qt.GlobalColor.yellow)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable)

    def mousePressEvent(self, event):
        QGraphicsItem.mousePressEvent(self, event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._viewer.roiClicked(self)


class LineROI(QGraphicsLineItem):
    def __init__(self, viewer):
        QGraphicsItem.__init__(self)
        self._viewer = viewer
        pen = QPen(Qt.GlobalColor.yellow)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable)

    def mousePressEvent(self, event):
        QGraphicsItem.mousePressEvent(self, event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._viewer.roiClicked(self)


class PolygonROI(QGraphicsPolygonItem):
    def __init__(self, viewer):
        QGraphicsItem.__init__(self)
        self._viewer = viewer
        pen = QPen(Qt.GlobalColor.yellow)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable)

    def mousePressEvent(self, event):
        QGraphicsItem.mousePressEvent(self, event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._viewer.roiClicked(self)
