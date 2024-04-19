import argparse
import shutil
import subprocess
import os


def find_exe_file(root_directory, target_filename):
    # 遍历指定目录下的所有文件和文件夹
    for root, dirs, files in os.walk(root_directory):
        # 检查每个文件是否为目标文件
        for file in files:
            if file == target_filename:
                # 返回找到的文件的完整路径
                return os.path.join(root, file)
    # 如果未找到，返回None
    return None


def find_first_video_file(folder_path):
    # 列出文件夹中的所有文件
    files = os.listdir(folder_path)

    # 遍历文件夹中的文件
    for file in files:
        # 检查文件扩展名是否为视频格式
        if file.endswith(('.mp4', '.avi', '.mkv', '.mov')):
            # 返回找到的第一个视频文件的路径
            return os.path.join(folder_path, file)

    # 如果没有找到视频文件，返回None
    return None


video_folder = "video_input/"
# 查找第一个视频文件
video = find_first_video_file(video_folder)
root_directory = "/"

# 在指定根目录中搜索目标文件
exe_path1 = find_exe_file(root_directory, "OpenPoseDemo.exe")
openpose_folder = os.path.dirname(os.path.dirname(exe_path1))

images = "data/images"
keypoints = "data/keypoints"

# 删除旧的output_frames和output_jsons文件夹（如果存在）
shutil.rmtree(images, ignore_errors=True)
shutil.rmtree(keypoints, ignore_errors=True)

# 重新创建这两个文件夹
os.makedirs(images)
os.makedirs(keypoints)

# 使用subprocess模块调用FFmpeg命令
subprocess.run(['ffmpeg', '-i', video, images + '/frame_%05d.jpg'])

# 保存当前工作目录
original_dir = os.getcwd()

# 切换到openpose目录
os.chdir(openpose_folder)

# 定义路径变量
exe_path = r'bin\OpenPoseDemo.exe'

image_dir = os.path.join(original_dir, images)
output_jsons = os.path.join(original_dir, "data/keypoints")

# 构建命令字符串
command = f'{exe_path} --image_dir {image_dir} --hand --display 0 --write_json {output_jsons} --render_pose 0'

# 使用subprocess模块执行命令
subprocess.run(command, shell=True)

# 切换回原来的工作目录
os.chdir(original_dir)

output_folder = "smplx_debug"
# 删除旧的smplx_debug文件夹（如果存在）
shutil.rmtree(output_folder, ignore_errors=True)
os.makedirs(output_folder)

command1 = "python smplifyx/main.py --config cfg_files/fit_smplx.yaml --use_face False --interpenetration False"
command2 = "python smplifyx/render_pkl_body.py --results smplx_debug/results" \
           " -c cfg_files/fit_smplx.yaml --interpenetration False"

subprocess.run(command1, shell=True)

shutil.rmtree("joints_output", ignore_errors=True)
os.makedirs("joints_output")
subprocess.run(command2, shell=True)

subprocess.run(["python", "backbone_curve.py"])
