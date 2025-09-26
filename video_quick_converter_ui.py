#-*- coding:utf-8 -*-

'''
__ author __ = lighting_joonsoo
'''

import os
import sys

try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    
except:
    pysidePath = '/westworld/inhouse/tool/rez-packages/PySide/1.2.4/platform-linux/arch-x86_64/lib64/python2.7/site-packages'
    if pysidePath not in sys.path:
	    sys.path.append(pysidePath)

    from PySide import QtCore, QtGui
    from PySide.QtGui import *
    from PySide.QtCore import *	

import video_quick_converter_model as VQCM
reload(VQCM)


class Ui(QWidget):
    def __init__(self, mainUI, toolName):
        super(Ui, self).__init__() 
        
        # init setting.
        self.WindowSize = [759, 400]
        self.WindowTitle = 'Video Quick Converter'

        # For Applying Toolkit Style
        '''
        widgetTypeList : 배경과 분리되어야 하는 Widget type은 꼭 List 안에 입력해야합니다.
        ignore_widgetList : type 중 포함되지 않아야하는 widget은 직접 변수명으로 입력합니다.
        '''
        self.widgetTypeList = [QPushButton]
        self.ignore_widgetList = []

        if mainUI :
	        mainUI.setWindowPosition(self, mainUI)
        else:
	        main_layout = self.init_ui()
	        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	        self.setWindowTitle(" %s "%self.WindowTitle)
	        self.setMinimumSize(*self.WindowSize)
	        self.setLayout(main_layout)

    def init_ui(self):
        # Create the main main_layout
        main_layout = QVBoxLayout()

        # file browser group                
        file_grpbox = QGroupBox(self)
        file_grpbox.setTitle("")         
        fgb_layout = QVBoxLayout(file_grpbox)        
        fgb_layout.setContentsMargins(10, -1, 10, 0)

        # input group
        input_layout = QVBoxLayout()     

        text_label = QLabel(file_grpbox)
        text_label.setText('Drag Drop files ')        
        input_layout.addWidget(text_label)              
                        
        self.output_treeWidget = MyTreeWidget()         
        input_layout.addWidget(self.output_treeWidget)                                 

        fgb_layout.addLayout(input_layout)  
                          
        # file browser group addWidget                   
        main_layout.addWidget(file_grpbox)  
                
        # option group                
        self.option_grpbox = QGroupBox(self)
        self.option_grpbox.setTitle('Output Option')
        ogb_Policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)              
        ogb_Policy.setHeightForWidth(self.option_grpbox.sizePolicy().hasHeightForWidth())
        self.option_grpbox.setSizePolicy(ogb_Policy)         
        self.option_grpbox.setMinimumSize(QSize(16777215, 110))        
        self.option_grpbox.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)       

        ogb_layout = QVBoxLayout(self.option_grpbox)           
        ogb_layout.setContentsMargins(10, -1, 10, 0)                
      
        '''
        ogvConverter_run에서 options값을 받는 옵션들은 _commedit네이밍 규칙 사용
        label = eval('self.ui.' + widget_name + '_label')
        commedit = eval('self.ui.' + widget_name + '_commedit')         
        수정시 - 위젯 추가 후 *_run.py에 있는 클래스 리스트에 추가하기
        '''                     
        # options line 1
        ogb_line1_layout = QHBoxLayout()  
       
        option1_spacer = QSpacerItem(100, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        ogb_line1_layout.addItem(option1_spacer)   
        
        self.output_path_label = QLabel(self.option_grpbox)     
        self.output_path_label.setText('Output Path')             
        ogb_line1_layout.addWidget(self.output_path_label)            
        self.output_path_lineedit = QLineEdit(self.option_grpbox)
        self.output_path_lineedit.setMaximumSize(QSize(1000, 16777215))
        self.output_path_lineedit.setText('/home/' + os.environ['USER'] + '/gif')       
        ogb_line1_layout.addWidget(self.output_path_lineedit)  
        
        self.ext_label = QLabel(self.option_grpbox)     
        self.ext_label.setText('Ext')             
        ogb_line1_layout.addWidget(self.ext_label)       
        self.ext_combobox = QComboBox(self.option_grpbox)
        format_list = (VQCM.GIF_EXT +
            VQCM.VIDEO_EXT +
            VQCM.IMAGE_EXT)
        for i in format_list:
            self.ext_combobox.addItem(i)                
        ogb_line1_layout.addWidget(self.ext_combobox)                    
        
        ogb_layout.addLayout(ogb_line1_layout)               
        
        # options line 2
        ogb_line2_layout = QHBoxLayout()                       

        option2_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        ogb_line2_layout.addItem(option2_spacer)             
        self.width_label = QLabel(self.option_grpbox)     
        self.width_label.setText('Width')             
        ogb_line2_layout.addWidget(self.width_label)

        self.width_commedit = QLineEdit(self.option_grpbox)
        self.width_commedit.setMaximumSize(QSize(60, 16777215))
        self.width_commedit.setAlignment(Qt.AlignCenter)
        self.width_commedit.setText('0')        
        ogb_line2_layout.addWidget(self.width_commedit)    
                    
        self.speed_label = QLabel(self.option_grpbox)     
        self.speed_label.setText('Speed')             
        ogb_line2_layout.addWidget(self.speed_label)
                
        self.speed_commedit = QLineEdit(self.option_grpbox)
        self.speed_commedit.setMaximumSize(QSize(60, 16777215))
        self.speed_commedit.setAlignment(Qt.AlignCenter)
        self.speed_commedit.setText('1')        
        ogb_line2_layout.addWidget(self.speed_commedit)        
                        
        self.fps_label = QLabel(self.option_grpbox)     
        self.fps_label.setText('Fps')             
        ogb_line2_layout.addWidget(self.fps_label)
                
        self.fps_commedit = QLineEdit(self.option_grpbox)
        self.fps_commedit.setMaximumSize(QSize(60, 16777215))
        self.fps_commedit.setAlignment(Qt.AlignCenter)
        self.fps_commedit.setText('15')        
        ogb_line2_layout.addWidget(self.fps_commedit)  
                                
        self.quality_label = QLabel(self.option_grpbox)     
        self.quality_label.setText('Quality')             
        ogb_line2_layout.addWidget(self.quality_label)
        #콤보박스지만 for문 쉽게 쓰기 위해 네이밍 수정
        self.quality_commedit = QComboBox(self.option_grpbox)
        self.quality_commedit.addItem('High')
        self.quality_commedit.addItem('Low')        
        ogb_line2_layout.addWidget(self.quality_commedit)          

        ogb_layout.addLayout(ogb_line2_layout)            
                    
        # options line 3
        ogb_line3_layout = QHBoxLayout()        
        
        option2_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        ogb_line3_layout.addItem(option2_spacer)                                   
        
        null_label = QLabel(file_grpbox)
        null_label.setText(' ')        
        null_label.setMinimumSize(QSize(16777215, 25))        
        ogb_line3_layout.addWidget(null_label)
                
        self.output_startFrame_label = QLabel(file_grpbox)
        self.output_startFrame_label.setText('Ouput Start Frame')        
        ogb_line3_layout.addWidget(self.output_startFrame_label)

        self.output_startFrame_commedit = QLineEdit(self.option_grpbox)
        self.output_startFrame_commedit.setMaximumSize(QSize(60, 16777215))
        self.output_startFrame_commedit.setAlignment(Qt.AlignCenter)
        self.output_startFrame_commedit.setText('1001') 
        ogb_line3_layout.addWidget(self.output_startFrame_commedit)         
        
        ogb_layout.addLayout(ogb_line3_layout)            
                               
                               
        # option group addWidget 
        main_layout.addWidget(self.option_grpbox)

        # button group
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, -1, 10, 0)    
        # button items       
        self.progressbar = QProgressBar(self)
        button_layout.addWidget(self.progressbar)  
        
        self.start_button = QPushButton(self)
        self.start_button.setText('Start')        
        button_layout.addWidget(self.start_button)  

        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')        
        button_layout.addWidget(self.cancel_button)  
                
        # button group addWidget         
        main_layout.addLayout(button_layout)

        return main_layout



class MyTreeWidget(QTreeWidget):
    '''
    이벤트 필터 오버라이드
    '''
    def __init__(self):
        QTreeWidget.__init__(self)
        self.setColumnCount(3)
        self.setHeaderLabels(['Name', 'Path', 'Ext', 'Start Frame'])
        self.setColumnWidth(0, 180)          
        self.setColumnWidth(1, 350)    
        self.setColumnWidth(2, 70)    
        self.setColumnWidth(3, 70)                             
        self.setAcceptDrops(True) 
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)          
        
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.emit(QtCore.SIGNAL('delete'), 'del')            
    
       
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()                
        else:
            event.ignore()
    
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()                
        else:
            event.ignore()    
    
        
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()  
            links = []
            for url in event.mimeData().urls():        
                encode_url = url.toLocalFile().encode('utf-8')            
                links.append(encode_url)
            self.emit(QtCore.SIGNAL('dropped'), links)              
        else:
            event.ignore()      

        
        
        
        
        
        
        
        
        
        
        
        
    
    

		
		
		
