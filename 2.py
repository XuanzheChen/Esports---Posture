import numpy as np

# 读取.npy 文件
# data = np.load('3D.npy')

# 打印数据
# print(data)
# 读取.txt文件
# 定义一个空的三维数组
three_dim_array = []

# 文件路径列表
# file_paths = ['joints_output/cxz_00001/body_joints.txt', 'joints_output/cxz_00002/body_joints.txt']  # 修改成你的文件路径列表

# 定义一个空的三维数组
three_dim_array = []

# 从1到100循环，生成文件名后缀 00001 到 00100，并读取文件数据存储为三维数组
for i in range(1, 82):
    file_suffix = str(i).zfill(5)  # 将数字填充成5位数，如1变为00001
    file_path = f'joints_output/frame_{file_suffix}/body_joints.txt'

    with open(file_path, 'r') as file:
        lines = file.readlines()

    coordinates = []
    for line in lines:
        if '身体关节点' in line:
            parts = line.split(', ')
            x = float(parts[0].split('=')[1])
            y = float(parts[1].split('=')[1])
            z = float(parts[2].split('=')[1])
            coordinates.append([x, y, z])

    three_dim_array.append(coordinates)

# 打印三维数组
# print(three_dim_array)

np.set_printoptions(suppress=True)
# 将三维数组保存为.npy文件
np.save('bodyfinal.npy', three_dim_array)

# 加载.npy文件
loaded_array = np.load('bodyfinal.npy')

# 打印加载后的数组
# print(loaded_array)
