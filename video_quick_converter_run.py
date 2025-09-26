#-*- coding:utf-8 -*-

'''
__ author __ = lighting_joonsoo

'''

import os
import re
import sys
import glob
import collections

from functools import partial

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

from imp import reload # PYTHON 3.7
import video_quick_converter_ui as VQCU
reload(VQCU)
import video_quick_converter_model as VQCM
reload(VQCM)


class Widget():
    # option widget   
    OUPUT_WIDGET_LIST = ['width', 'speed', 'fps', 'quality', 'output_startFrame']                         
            
    # TaskThread에 연동하기 위한 데이터
    PATH_LIST = ''
    OPTIONS_DICT = ''
            
    def __init__(self, mainUI, toolName):
        # Load UI.
        self.ui = VQCU.Ui(mainUI, toolName)    
        self.widget_show_n_hide(['output_startFrame'], 'hide')             
            
        # Connect Button Command.        
        self.ui.start_button.clicked.connect(self.start_run)            
        self.ui.cancel_button.clicked.connect(self.close_run) 
        self.ui.ext_combobox.activated.connect(self.auto_output_hide)                  
        # event trigger command        
        self.ui.connect(self.ui.output_treeWidget, QtCore.SIGNAL('dropped'), self.drop_event)
        self.ui.connect(self.ui.output_treeWidget, QtCore.SIGNAL('delete'), self.delete_event)        
        
        # Open UI
        self.ui.show()
    
        # progress thread
        self.progressTask = TaskThread()
        self.progressTask.taskFinished.connect(self._onFinished)


    def drop_event(self, mime):
        '''
        Widget에 드랍 했을 때 이벤트 발생
        이름, 경로, 포맷, 시작 프레임 미리 담아두게 구성
        시작 프레임은 드랍한 이름에서 가장 빠른 번호 자동찾게 구성 나머지는 -999
        
        Args:
            mime (list): 드래그앤드랍 한 경로 리스트            
        '''       
        output_exist_list, _x = self.get_output_all_items() #리스트에 존재하는 아이템 가져오기

        items = mime
        for item in items:                            
            name = os.path.basename(item)
            ext = str(os.path.splitext(item)[-1]).lower()
            start_frame = '-999'
            
            # 이미지 시퀀스의 경우 %?d로 네이밍 변경 
            if ext in VQCM.IMAGE_EXT:
                name, item, start_frame = self.convert_image_sequence(item, ext)
                        
                        
            format_list = (VQCM.IMAGE_EXT +
                VQCM.VIDEO_EXT +
                VQCM.GIF_EXT) 
            if ext in format_list: # 정해진 포맷들만 add                         
                if name not in output_exist_list: # 리스트 중복 방지
                    rowcount = self.ui.output_treeWidget.topLevelItemCount()            
                    self.ui.output_treeWidget.addTopLevelItem(QTreeWidgetItem(rowcount))
                    self.ui.output_treeWidget.topLevelItem(rowcount).setText(0, name.decode('utf-8'))
                    self.ui.output_treeWidget.topLevelItem(rowcount).setText(1, item.decode('utf-8'))
                    self.ui.output_treeWidget.topLevelItem(rowcount).setText(2, ext)                        
                    self.ui.output_treeWidget.topLevelItem(rowcount).setText(3, start_frame)   
        
        
    def delete_event(self, delete):
        '''
        del키 눌렀을 때 이벤트 발생
        선택된 아이템들 지움
        
        Args:
            delete (str): del *무시해도 됨            
        '''     
        selected_items = self.ui.output_treeWidget.selectedItems()
        for item in selected_items:
            index = self.ui.output_treeWidget.indexOfTopLevelItem(item)
            self.ui.output_treeWidget.takeTopLevelItem(index)      
                       
        
    def get_output_all_items(self):
        '''
        output_treeWidget에서 모든 아이템 데이터 가져오기
        
        Return:
            output_treeWidget (list): 파일 이름들 - 드래그앤드랍 시 아이템 중복 체크로 사용중 
            output_widget_path (list): (파일 경로, 시작프레임) 쓰레드로 넘길 때
        '''     
        output_widget_names = []
        output_widget_path = []
        rowcount = self.ui.output_treeWidget.topLevelItemCount()           
        for i in range(rowcount):
            output_widget_names.append( str(self.ui.output_treeWidget.topLevelItem(i).text(0).encode('utf-8')) )
            output_widget_path.append( (str(self.ui.output_treeWidget.topLevelItem(i).text(1).encode('utf-8')), 
                                    str(self.ui.output_treeWidget.topLevelItem(i).text(3))) )

        return output_widget_names, output_widget_path
                                
            
    def convert_image_sequence(self, item, ext):
        '''
        이미지 시퀀스를 가져왔을때 이슈 해결하기 위한 함수      
        
        Args:
            item (str): 파일 경로 ex) /home/w10110/gif/ml/ml.0001.exr
            ext (str): 확장자 ex) .exr
        Return:
            new_name (str): %?d 포맷으로 이름 변경 ex) test.1001.png -> test.%4d.png
            os.path.join(path, new_name) (str): %?d 포맷으로 경로 변경
            start_frame (str): 불러온 이름 제일 첫번째 번호를 스타트 프레임으로 지정  
        '''     
        path = os.path.dirname(item)
        name = os.path.basename(item)                                

        # 선택한 이미지 이름 바꾸기
        match = re.findall(r'\d+', name)[-1]       
        match_len = len(match)        
        split_match = name.split(match)
        new_name = name.replace(match, '%{}d'.format(match_len))

        # 선택한 이름의 맨 처음 프레임 찾기        
        ext_list = glob.glob(os.path.join(path, split_match[0]+'*'+ext))
        ext_list.sort()
        
        start_name = os.path.basename(ext_list[0])  
        start_frame = re.findall(r'\d+', start_name)[-1]   

        return new_name, os.path.join(path, new_name), start_frame


    def widget_show_n_hide(self, widget_list, status):
        '''
        ogvConverter_run에서 options값을 받는 옵션들은 _commedit네이밍 규칙 사용
        label = eval('self.ui.' + widget_name + '_label')
        commedit = eval('self.ui.' + widget_name + '_commedit')         
        수정시 - 위젯 추가 후 *_run.py에 있는 클래스 리스트에 추가하기
        '''  
        for widget_name in widget_list:                                  

            label = eval('self.ui.' + widget_name + '_label')
            commedit = eval('self.ui.' + widget_name + '_commedit') 

            if status == 'show':
                label.show(), commedit.show()
            elif status == 'hide':
                label.hide(), commedit.hide()


    def auto_output_hide(self):
        output_ext = self.ui.ext_combobox.currentText()    
        
        # output option hide                
        self.widget_show_n_hide(['output_startFrame'], 'hide')

        if output_ext in VQCM.IMAGE_EXT: # 이미지 포맷 관련일때 보여주기                        
            self.widget_show_n_hide(['output_startFrame'], 'show')


    def start_run(self):
        options_dict = {}        
        # 옵션 위젯리스트에 있는 데이터 가져오기
        for widget in Widget.OUPUT_WIDGET_LIST:   
            commedit = eval('self.ui.' + widget + '_commedit')                                       

            if commedit.isHidden(): # 숨겨진 값들은 필요없어서 않쓰는 값 지정
                options_dict[widget] = -999 
            else: 
                try:
                    options_dict[widget] = str(commedit.text())                
                except: # text()으로 값 못받아오면 여기에 추가
                    if widget == 'quality':     
                        options_dict[widget] = str(commedit.currentText())

        output_ext = self.ui.ext_combobox.currentText()   
        output_dir = self.ui.output_path_lineedit.text()    
        _x, get_output_all_list = self.get_output_all_items()
        
        # 만약 빈 리스트라면
        if get_output_all_list == []:
            info_box = QMessageBox.warning(None, 'Warning', 'Nothing items')
            return

        # 경로관련 데이터 컨터팅 부분
        all_path_list = []
        for output in get_output_all_list:
            input_path = output[0]            
            input_dir = os.path.dirname(input_path)           
            input_name, input_ext = os.path.splitext(os.path.basename(input_path))
            start_frame = output[1]        
                                                  
            output_path = os.path.join(output_dir, input_name+output_ext)                               
            # 인풋이 비디오이고 아웃풋이 이미지 시퀀스 일 때, % 포맷팅 추가             
            if output_ext in VQCM.IMAGE_EXT:   
                if input_ext not in VQCM.IMAGE_EXT:
                    output_path = os.path.join(output_dir, input_name , input_name + '.%4d' + output_ext)
             
            # 인풋이 이미지 시퀀스이고 아웃풋이 비디오 일때, % 포맷팅 제거    
            if output_ext not in VQCM.IMAGE_EXT:   
                if input_ext in VQCM.IMAGE_EXT:
                    find_index = input_name.find('%') - 1
                    find_name = input_name[0:find_index]
                    output_path = os.path.join(output_dir, find_name + output_ext)
                    
            output_path = str(output_path.encode('utf-8'))              
            all_path_list.append( (input_path, output_path, start_frame) )                    

            # 폴더없으면 생성               
            check_dir = os.path.dirname(output_path)        
            if not os.path.exists(check_dir):
                os.makedirs(check_dir)
            
        Widget.PATH_LIST = all_path_list
        Widget.OPTIONS_DICT = options_dict
        
        # TaskThread 실행       
        self._onStart()                   


    def close_run(self):
        self.ui.close()


    def _onStart(self):
        #start bar
        self.progressTask.start()
        self.ui.progressbar.setRange(0, 0)


    def _onFinished(self):
        #finish bar
        self.ui.progressbar.setRange(0, 1)
        self.ui.progressbar.setValue(1)

        #message box
        if TaskThread.STATUS == 0:
            QMessageBox.about(None, 'Done..!!!', 'Created!!!!')
            self.ui.progressbar.setValue(0)
        else:
            QMessageBox.warning(None, 'Warning', 'Check plz. cmd error messaage')
            self.ui.progressbar.setValue(0)
            
        # return bar            
        self.ui.progressbar.setValue(0)
        


class TaskThread(QtCore.QThread):
    '''
    테스크 시그널 오버라이드
    '''
    taskFinished = QtCore.Signal()
    
    # Widget에 os 상태 데이터 보내기 위해서
    STATUS = ''
    
    def run(self):           
        for i in Widget.PATH_LIST:
            input_path = i[0]
            output_path = i[1]
            start_frame = i[2]
            input_ext = os.path.splitext(input_path)[1]
            output_ext = os.path.splitext(output_path)[1]
            
            # cmd 실행용으로 변환
            converting = VQCM.PyToCmd()
            # 인풋 필터
            input_option = converting.get_input_options(
                start_frame)         
                
            # 아웃풋 필터   
            output_options = converting.get_output_options(
                Widget.OPTIONS_DICT['speed'],
                Widget.OPTIONS_DICT['fps'],
                Widget.OPTIONS_DICT['width'],
                Widget.OPTIONS_DICT['output_startFrame'])    
                
            # 고정 config 데이터 가져오기
            fixed_config = converting.get_fixed_config(
                input_ext,
                output_ext,
                Widget.OPTIONS_DICT['quality'])
            
            # gif high 필요 커멘드가 다름
            if Widget.OPTIONS_DICT['quality'] == 'High' and output_ext.lower() == '.gif':
                combine_data = converting.only_gif_high(
                    input_path,
                    output_path, 
                    input_option, 
                    output_options,
                    fixed_config)
            # 나머지 공용                
            else:
                combine_data = converting.combine_data(
                    input_path,
                    output_path, 
                    input_option, 
                    output_options,
                    fixed_config)

            # cmd로 실행
            for i in combine_data:
                TaskThread.STATUS = os.system(i)   
        self.taskFinished.emit()  

            

def Tools(mainUI, toolName):
    global ToolsApp
    ToolsApp = Widget(mainUI, toolName)
    return ToolsApp



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ToolsApp = Tools('', 'ogvConverter')
    sys.exit(app.exec_())
    
    
    
