#-*- coding:utf-8 -*-

'''
__ author __ = lighting_joonsoo
'''

import os
import sys
import json
import glob
import subprocess

from collections import OrderedDict


IMAGE_EXT = ['.jpg', '.jpeg', '.png', '.exr', '.tiff', '.tif']
VIDEO_EXT = ['.mov', '.mp4', '.ogv']
GIF_EXT = ['.gif']
   
       
class PyToCmd():
    def combine_data(self, get_input_path, get_output_path, get_input_option, get_output_filter, get_fixed_config):
        '''
        일반적인 커멘드 구조

        '''
        input_path = get_input_path
        output_path = get_output_path
        input_option = get_input_option
        output_filter = get_output_filter
        fixed_config = get_fixed_config      
        
        cmd = ['rez-env ffmpeg -- ffmpeg {input_option} -i {input_name} -vf {filters} {config} -y {output_name}'.format(
            input_option = input_option,
            input_name = input_path,
            filters = output_filter,
            config = fixed_config,
            output_name = output_path)]       
            
        return cmd
        
        
    def only_gif_high(self, get_input_path, get_output_path, get_input_option, get_output_filter, get_fixed_config):
        '''
        gif 커멘트 구조가 달라서 따로 구성
        
        '''
        input_path = get_input_path
        output_path = get_output_path
        input_option = get_input_option
        output_filter = get_output_filter
        fixed_config = get_fixed_config
        
        png = os.path.splitext(output_path)[0] + '.png'

        # 샘플을 올려주는 png이미지 
        cmd = ['rez-env ffmpeg -- ffmpeg {input_option} -i {input_name} -vf palettegen -y {png_path}'.format(
            input_option = input_option,        
            input_name = input_path,
            png_path = png)]

        # gif 명령어
        cmd.append( 'rez-env ffmpeg -- ffmpeg {input_option} -i {input_name}  -i {png_path} -lavfi "{filters} [x]; [x][1:v] paletteuse" {config} -y {output_name}'.format(
            input_option = input_option,
            input_name = input_path,
            png_path = png,
            filters = output_filter,
            config = fixed_config,   
            output_name = output_path))
        
        # png이미지 지우기
        cmd.append('rm {}'.format(png))    

        return cmd

    
    def get_input_options(self, input_startFrame):
        '''
        인풋 옵션 *아웃풋 옵션 함수 따로 분리한건 나중에 인풋 아우풋 옵션 다르게 추가될 경우를 생각해서
        
        Args:
            input_startFrame (str): 첫 프레임 ex) 1001, 101 etc...
            
        Return:
            str: 사용자가 변경 가능한 아웃풋 옵션들을 합친 형태 
            ex) -start_number {input_startFrame}          
        '''    
        input_startFrame = str(input_startFrame)
        start_frame = '-start_number {}'.format(input_startFrame)
        if input_startFrame == '-999':
            start_frame = ''
                
        return '{}'.format(start_frame)


    def get_output_options(self, speed, fps, width, output_startFrame):
        '''
        따로 분리한 이유는 구조적 차이 때문에 나중에 추가적인 옵션 추가 편리하기 위해서
        self.get_output_filter -> -vf setpts={}*PTS,fps={} 필터 안에,으로 연결된 구조
        self.get_start_outputFrame -> '-start_number {}' 하나의 고유 커멘드가 존재    
        '''
        output_filter = self.get_output_filter(speed, fps, width)        
        output_start_frame = self.get_start_outputFrame(output_startFrame)       
        
        return output_filter + output_start_frame
        
        
    def get_output_filter(self, speed, fps, width):  
        '''
        아웃풋 필터
        
        Args:
            speed (str): 1기준으로 -는 빨라지고 +는 배로 느려진다.
            fps (str): 우리가 흔히 생각하는 동영상 프레임
            width (str): 가로축(x), 세로축은 자동으로 비율 조절
            
        Return:
            str: 사용자가 변경 가능한 아웃풋 옵션들을 합친 형태 
            ex) setpts={speed}*PTS,fps={fps}      
        '''
        if speed == -999 and fps == -999 and speed == -999:
            return ''
                    
        speed = 'setpts={}*PTS'.format(str(speed))
        fps = 'fps={}'.format(str(fps))
        width = 'scale={}:-1:flags=lanczos'.format(str(width))        
              
        # 커멘드에 ,이 들어갸야하는데 마지막에 ,는 없어야해서 for문으로 구성                  
        count = 1                 
        filter_name = ''
        filter_list = [speed, fps, width]                  
        for i in filter_list: 
            if '-999' not in i:
                filter_name += i
                
                if len(filter_list) != count:
                    filter_name += ','                    
            count += 1
          
        return '{} '.format(filter_name)
        
        
    def get_start_outputFrame(self, output_startFrame):
        '''
        아웃풋 옵션 *필터 옵션이랑은 조금 다른 구조
                
        Args:
            output_startFrame (str): 첫 프레임 ex) 1001, 101 etc...
            
        Return:
            str: 사용자가 변경 가능한 아웃풋 옵션들을 합친 형태 
            ex) -start_number {output_startFrame}     
        '''   
        frame = '-start_number {}'.format(output_startFrame)
        if output_startFrame == -999:
            frame = ''
            
        return frame                           


    def get_fixed_config(self, input_ext, output_ext, quality):
        '''
        아웃풋 포맷별 고유 옵션들로 구성된 config 파일을 cmd 형식으로 변환
        구성에는 필요하지만 사용자가 굳이 변경할 필요 없는 옵션들
        
        Args:
            input_ext (str): .ogv, .mov etc..
            output_ext (str): .ogv, .mov etc..
            quality (str): high, low
            
        Return:
            str: config 파일을 cmd에 쓸 수 있게 변환   
            ex) -c:v libx264 -preset medium -crf 0 -c:a copy              
        '''        
        config_path = os.path.dirname(os.path.abspath(__file__)) + '/fixed_config'
        config_name = ''    
            
        if output_ext.lower() == '.gif':
            config_name = 'high_gif' 
        elif output_ext.lower() == '.ogv':
            config_name = 'high_ogv'        
        elif output_ext.lower() == '.mov' or output_ext.lower() == '.mp4':
            if quality == 'High':            
                config_name = 'high_h264'    
            elif quality == 'Low':            
                config_name = 'low_h264'                           
        else:
            return ''
        
        with open(os.path.join(config_path, config_name)) as config_file:
            config = json.load(config_file,object_pairs_hook=OrderedDict)
        
        cmds = ''
        for key, value in config.iteritems():
            cmds += str(value) + ' '
            
        return cmds


    
    
    
 


    
    
    
    
    
    
    
