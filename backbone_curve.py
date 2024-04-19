import os
import numpy as np
import re
import matplotlib.pyplot as plt


# 定义角度计算函数
def angle_calculate(a, b, c):
    ba = a - b
    bc = c - b

    dot_product = np.dot(ba, bc)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    cos_angle = dot_product / (norm_ba * norm_bc)
    angle_radians = np.arccos(cos_angle)
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees


# 定义滑动平均函数
def moving_average(data, window_size):
    padded_data = np.pad(data, (window_size // 2, window_size // 2), mode='edge')  # 使用edge模式填充数据
    weights = np.repeat(1.0, window_size) / window_size
    smoothed_data = np.convolve(padded_data, weights, 'valid')
    return smoothed_data


base_folder_path = 'joints_output'

folders = [name for name in os.listdir(base_folder_path) if os.path.isdir(os.path.join(base_folder_path, name))]

# 如果有文件夹，获取第一个文件夹的名称
if folders:
    first_folder_name = folders[0]
else:
    print("backbone_curve.py读取joints_output文件夹为空")

# 统计文件夹数量
num_folders = sum(os.path.isdir(os.path.join(base_folder_path, name)) for name in os.listdir(base_folder_path))

x_array = []
y_array = []
z_array = []

folder_prefix = first_folder_name[:-5]  # 文件夹前缀
lines_to_read = {1, 4, 7, 10, 13}  # 定义要读取的行的索引
# 遍历文件夹
for i in range(1, num_folders + 1):
    folder_name = f"{folder_prefix}{i:05d}"  # 构造文件夹名称，保证数字两位数
    folder_path = os.path.join(base_folder_path, folder_name)  # 构造文件夹路径
    if os.path.isdir(folder_path):  # 如果文件夹存在
        filename = 'body_joints.txt'
        full_path = os.path.join(folder_path, filename)

        x = np.empty((0, 1), dtype=float)
        y = np.empty((0, 1), dtype=float)
        z = np.empty((0, 1), dtype=float)
        with open(full_path, 'r') as file:
            for index, line in enumerate(file, start=1):
                if index in lines_to_read:
                    string_body_joints = line.strip()
                    # 使用正则表达式匹配 x、y、z 值
                    match = re.search(r'x=([-0-9.]+), y=([-0-9.]+), z=([-0-9.]+)', string_body_joints)
                    if match:
                        x_value = float(match.group(1))
                        y_value = float(match.group(2))
                        z_value = float(match.group(3))

                        x = np.append(x, x_value)
                        y = np.append(y, y_value)
                        z = np.append(z, z_value)
                    else:
                        print("backbone_curve.py未找到匹配的坐标值")

        # 最小二乘法拟合曲线
        # 创建系数矩阵A和矩阵b
        A = np.vstack((x, y, np.ones_like(x))).T
        coefficients, _, _, _ = np.linalg.lstsq(A, z, rcond=None)
        z_fit = coefficients[0] * x + coefficients[1] * y + coefficients[2]
        x_fit = x
        y_fit = y

        # 数据归一化
        minx = np.min(x_fit)
        miny = np.min(y_fit)
        minz = np.min(z_fit)

        x_fit = (x_fit - minx) / (np.max(x_fit) - minx)
        y_fit = (y_fit - miny) / (np.max(y_fit) - miny)
        z_fit = (z_fit - minz) / (np.max(z_fit) - minz)

        x_array.append(x_fit)
        y_array.append(y_fit)
        z_array.append(z_fit)
    else:
        print(f"joints_output中文件夹不存在 {folder_name} ")
# 对坐标进行样条插值
num_points = len(lines_to_read)
smooth_x = x_array = np.array(x_array)
smooth_y = y_array = np.array(y_array)
smooth_z = z_array = np.array(z_array)

for i in range(num_points):
    # 使用滑动平均处理异常值
    window_size = 5
    smooth_x[:, i] = moving_average(x_array[:, i], window_size)
    smooth_y[:, i] = moving_average(y_array[:, i], window_size)
    smooth_z[:, i] = moving_average(z_array[:, i], window_size)

angle = np.zeros((num_folders, 3))
for j in range(num_folders):
    # 角度计算
    a = np.array([smooth_x[j, 0], smooth_y[j, 0], smooth_z[j, 0]])
    b = np.array([smooth_x[j, 1], smooth_y[j, 1], smooth_z[j, 1]])
    c = np.array([smooth_x[j, 2], smooth_y[j, 2], smooth_z[j, 2]])
    d = np.array([smooth_x[j, 3], smooth_y[j, 3], smooth_z[j, 3]])
    e = np.array([smooth_x[j, 4], smooth_y[j, 4], smooth_z[j, 4]])
    angle[j, 0] = angle_calculate(a, b, c)
    angle[j, 1] = angle_calculate(b, c, d)
    angle[j, 2] = angle_calculate(c, d, e)

# 指定要写入的文件路径
for i in range(3):
    file_path = "angle{:}.txt".format(i + 1)

    # 打开文件以写入模式
    with open(file_path, "w") as file:
        # 将列表中的每个元素写入文件，每个元素占一行
        for item in angle[:, i]:
            file.write(str(item) + "\n")
