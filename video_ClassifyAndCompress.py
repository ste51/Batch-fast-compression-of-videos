import video_compressvideo_v2_1AMD
import platform
import video_compressvideo_v2_1Intel

if __name__ == '__main__':
    cpu_info = platform.processor()
    if 'amd' in cpu_info.lower():
        video_compressvideo_v2_1AMD.compressvideo_main()
    elif 'intel' in cpu_info.lower():
        video_compressvideo_v2_1Intel.compressvideo_main()
    
    