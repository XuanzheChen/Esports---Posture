from mayavi import mlab


def read_joints_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        joints_data = {}
        for line in lines:
            data = line.strip().split(':')
            joint_name = data[0].strip()
            joint_coords = data[1].strip().split(',')
            joint_x = float(joint_coords[0].strip()[2:])
            joint_y = float(joint_coords[1].strip()[2:])
            joint_z = float(joint_coords[2].strip()[2:])
            joints_data[joint_name] = [joint_x, joint_y, joint_z]
        return joints_data


def connect_points(point1, point2, color=(0, 1, 0), tube_radius=0.001):
    mlab.plot3d([point1[0], point2[0]], [point1[1], point2[1]], [point1[2], point2[2]], color=color,
                tube_radius=tube_radius)


# 读取手部关节点数据
hand_joints_file = 'joints_output/hand_joints.txt'
hand_joints_data = read_joints_file(hand_joints_file)

# 绘制身体关节点的坐标
x, y, z = [], [], []
for _, coords in hand_joints_data.items():
    x.append(coords[0])
    y.append(coords[1])
    z.append(coords[2])

mlab.points3d(x, y, z, color=(1, 0, 0), mode='sphere', scale_factor=0.01)  # 将颜色设置为红色
mlab.view(azimuth=0, elevation=90, distance=2)
coords_list = []
coords_list = [0] * 76  # 创建初始的coords_list，每个元素都是0
for i in range(20, 22):
    joint_name = '手关节点 ' + str(i)
    coords = hand_joints_data.get(joint_name)
    if coords:
        coords_list[i] = coords
    else:
        print(f"{joint_name} 的坐标未提供")
for i in range(25, 55):
    joint_name = '手关节点 ' + str(i)
    coords = hand_joints_data.get(joint_name)
    if coords:
        coords_list[i] = coords
    else:
        print(f"{joint_name} 的坐标未提供")
for i in range(66, 76):
    joint_name = '手关节点 ' + str(i)
    coords = hand_joints_data.get(joint_name)
    if coords:
        coords_list[i] = coords
    else:
        print(f"{joint_name} 的坐标未提供")

print(coords_list)

# 右手--------------------------------------------------------------------------------
# 小指
connect_points(coords_list[46], coords_list[47], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[47], coords_list[48], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[48], coords_list[75], color=(0, 1, 0), tube_radius=0.001)
# 无名指
connect_points(coords_list[49], coords_list[50], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[50], coords_list[51], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[51], coords_list[74], color=(0, 1, 0), tube_radius=0.001)
# 中指
connect_points(coords_list[43], coords_list[44], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[44], coords_list[45], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[45], coords_list[73], color=(0, 1, 0), tube_radius=0.001)
# 食指
connect_points(coords_list[40], coords_list[41], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[41], coords_list[42], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[42], coords_list[72], color=(0, 1, 0), tube_radius=0.001)
# 大拇指
connect_points(coords_list[52], coords_list[53], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[53], coords_list[54], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[54], coords_list[71], color=(0, 1, 0), tube_radius=0.001)
# 连接食指大拇指
connect_points(coords_list[40], coords_list[52], color=(0, 1, 0), tube_radius=0.001)
# 连接手指手腕
connect_points(coords_list[21], coords_list[46], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[21], coords_list[49], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[21], coords_list[43], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[21], coords_list[52], color=(0, 1, 0), tube_radius=0.001)

# 左手---------------------------------------------------------------------------------
# 小指
connect_points(coords_list[31], coords_list[32], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[32], coords_list[33], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[33], coords_list[70], color=(0, 1, 0), tube_radius=0.001)
# 无名指
connect_points(coords_list[34], coords_list[35], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[35], coords_list[36], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[36], coords_list[69], color=(0, 1, 0), tube_radius=0.001)
# 中指
connect_points(coords_list[28], coords_list[29], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[29], coords_list[30], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[30], coords_list[68], color=(0, 1, 0), tube_radius=0.001)
# 食指
connect_points(coords_list[25], coords_list[26], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[26], coords_list[27], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[27], coords_list[67], color=(0, 1, 0), tube_radius=0.001)
# 大拇指
connect_points(coords_list[37], coords_list[38], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[38], coords_list[39], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[39], coords_list[66], color=(0, 1, 0), tube_radius=0.001)
# 连接食指大拇指
connect_points(coords_list[25], coords_list[37], color=(0, 1, 0), tube_radius=0.001)
# 连接手指手腕
connect_points(coords_list[20], coords_list[37], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[20], coords_list[28], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[20], coords_list[34], color=(0, 1, 0), tube_radius=0.001)
connect_points(coords_list[20], coords_list[31], color=(0, 1, 0), tube_radius=0.001)

mlab.show()
