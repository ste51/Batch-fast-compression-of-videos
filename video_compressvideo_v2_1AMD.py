#v2.0版本，支持多种模式压缩命令，保证视频能够被压缩
import subprocess
import os
import configparser

folders_name = ('仅复制','仅压缩比特率','仅压缩分辨率和比特率')

def compressfunction(video_path,output_path,foldername,commandflag = 0): 
    global failvideo
    print("command命令的模式：",commandflag)
    if foldername != '仅复制':
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', 'scale=1280:720:force_original_aspect_ratio=increase,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
            '-y', 'temp.mp4'
        ]
        
        try:
            result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=1, text=False)
            if "Padded dimensions cannot be smaller than input dimensions" in result.stderr.decode('utf-8', errors='replace'):
                command = [
                    'ffmpeg',
                    '-i', video_path,
                    '-b:v', '2000k',
                    '-keyint_min', '10', #关键帧
                    '-acodec', 'copy',
                    '-y',output_path
                ]
                flag = 1
            else:
                print(f"压缩分辨率：{video_path}")
                command = [
                    'ffmpeg',
                    '-i', video_path,
                    '-b:v', '2000k',
                    '-vf', 'scale=1280:720', 
                    '-keyint_min', '10',
                    '-acodec', 'copy',
                    '-y',output_path
                ]
                flag = 2
        except subprocess.TimeoutExpired: 
            flag = 2
            command = [
                'ffmpeg',
                '-i', video_path,
                '-b:v', '2000k',
                '-vf', 'scale=1280:720', 
                '-keyint_min', '10',
                '-acodec', 'copy',
                '-y',output_path
            ]
    else:
        flag = 3
        command = [
            'ffmpeg',
            '-i', video_path,
            '-c:v', 'copy',
            '-acodec', 'copy',
            '-y',output_path
        ]

    if commandflag == 0:
        command[3:3] = ['-c:v', 'h264_amf']
    elif commandflag == 1:
        command[3:3] = ['-c:v', 'h264_mf']
        command[1:1] = ['-hwaccel', 'dxva2']
    elif commandflag == 2:
        command[3:3] = ['-c:v', 'h264_mf']
        command[1:1] = ['-hwaccel', 'd3d11va']
    elif commandflag == 3:
        command[3:3] = ['-c:v', 'h264_mf']
        command[1:1] = ['-hwaccel', 'vulkan']
    elif commandflag == 4:
        command[3:3] = ['-c:v', 'h264_amf']
        command[1:1] = ['-hwaccel', 'dxva2']
    elif commandflag == 5:
        command[3:3] = ['-c:v', 'h264_amf']
        command[1:1] = ['-hwaccel', 'd3d11va']
    elif commandflag == 6:
        command[3:3] = ['-c:v', 'h264_amf']
        command[1:1] = ['-hwaccel', 'vulkan']
    elif commandflag == 7:
        command[3:3] = ['-c:v', 'h264']
        command[1:1] = ['-hwaccel', 'd3d11va']
    elif commandflag == 8:
        command[3:3] = ['-c:v', 'h264']
        command[1:1] = ['-hwaccel', 'dxva2']
    elif commandflag == 9:
        command[3:3] = ['-c:v', 'h264']
        command[1:1] = ['-hwaccel', 'vulkan']
    elif commandflag == 10:
        command[3:3] = ['-c:v', 'h264']
    result = subprocess.Popen(command,stderr=subprocess.STDOUT, stdout=subprocess.PIPE,universal_newlines=True)
    processstate = 1
    while result.poll() is None:
        try:
            line = result.stdout.readline()
            if line:
                print(line, end='')  # 输出已经是字符串，不需要再次解码
                result.stdout.flush()
            if 'Error reinitializing filters' in line or 'Conversion failed!' in line:
                # pass
                processstate = -1

        except UnicodeDecodeError:
                pass

    # 处理子进程完成后剩余的输出
    for line in result.stdout.readlines():
        print(line, end='')
    
    ffprobe_command = [
    'ffprobe', 
    '-v', 'error',  
    '-select_streams', 'v:0', 
    '-show_entries', 'stream=duration', 
    '-of', 'csv=s=x:p=0', 
    ]

    try:
        if processstate == 1:
            result.wait() 
            ffprobe_command.insert(9, video_path) 
            duration = subprocess.check_output(ffprobe_command, stderr=subprocess.PIPE).decode('utf-8').strip()
            print(int(float(duration))) 
            
            ffprobe_command[9] = output_path 
            duration1 = subprocess.check_output(ffprobe_command, stderr=subprocess.PIPE).decode('utf-8').strip()
            print(int(float(duration1))) 
            
            if int(float(duration)) == int(float(duration1)):
                print("成功压缩") 
            else:
                if commandflag < 10:
                    compressfunction(video_path, output_path, foldername, commandflag=commandflag + 1)
                elif commandflag == 10:
                    failvideo.append('duration添加：' + video_path)
        else:
            if commandflag < 10:
                compressfunction(video_path, output_path, foldername, commandflag=commandflag + 1)
            elif commandflag == 10:
                failvideo.append('processstate添加：' + video_path)
    except subprocess.CalledProcessError:
        if commandflag < 10:
            compressfunction(video_path, output_path, foldername, commandflag=commandflag + 1)
        elif commandflag == 10:
            failvideo.append('CalledProcessError添加：' + video_path)
    except ValueError as verr:
        print("无法读取时长：", video_path)
                


def find_video_files(folder_path):
    for foldername in folders_name:
        compression_directory = os.path.join(folder_path, foldername)
        print('compress floder name:',compression_directory)
        if not os.path.exists(compression_directory):
            continue
        
        # 列出文件夹中的所有文件和子文件夹
        file_list = os.listdir(compression_directory)
        # print(file_list)
        for file in file_list:
            if (file.endswith('_compress.mp4') and os.path.getsize(os.path.join(compression_directory, file)) != 0) or file == "00translog.txt": #避免中途中断后，又重新把所有的文件给压缩一遍
                continue
            new_filename = f"{file.rsplit('.', 1)[0]}_compress.mp4"
            if new_filename not in file_list:
                print(new_filename)
                compressfunction(os.path.join(compression_directory, file),os.path.join(compression_directory, new_filename),foldername)
                

def compressvideo_main():
    global failvideo
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'paths.ini')
    config.read(config_path, encoding='utf-8')
    path_string = config.get('Paths', 'folderspath')
    folders_path = path_string.split(',')
    print('需要处理的文件夹有：',folders_path)
    for folder_path in folders_path:
        failvideo = []
        find_video_files(folder_path)
        
        if failvideo:
            txt_file_path = os.path.join(folder_path,'fail_videos.txt')
            if os.path.exists(txt_file_path):
                with open(txt_file_path, 'a', encoding='utf-8') as txt_file:
                    for i in failvideo:
                        txt_file.write(f"没有成功压缩：{i}\n")
                print(f"已将失败的视频追加到 {txt_file_path} 文件中。")
            else:
                with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                    for i in failvideo:
                        txt_file.write(f"没有成功压缩：{i}\n")
                print(f"已创建 {txt_file_path} 文件并将失败的视频写入其中。")
        else:
            print("没有失败的视频，不创建或追加 txt 文件。")
    
if __name__ == '__main__':
    compressvideo_main()