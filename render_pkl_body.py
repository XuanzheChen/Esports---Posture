# -*- coding: utf-8 -*-

# Max-Planck-Gesellschaft zur Förderung der Wissenschaften e.V. (MPG) is
# holder of all proprietary rights on this computer program.
# You can only use this computer program if you have closed
# a license agreement with MPG or you get the right to use the computer
# program from someone who is authorized to grant you that right.
# Any use of the computer program without a valid license is prohibited and
# liable to prosecution.
#
# Copyright©2019 Max-Planck-Gesellschaft zur Förderung
# der Wissenschaften e.V. (MPG). acting on behalf of its Max Planck Institute
# for Intelligent Systems. All rights reserved.
#
# Contact: ps-license@tuebingen.mpg.de
# Contact: Vassilis choutas, vassilis.choutas@tuebingen.mpg.de

import os
import os.path as osp

import argparse
import pickle
import shutil

import torch
import smplx
import numpy as np

from cmd_parser import parse_config
from human_body_prior.tools.model_loader import load_vposer

from utils import JointMapper
import pyrender
import trimesh


def read_file_paths(file_path):
    with open(file_path, 'r') as file:
        paths = [line.strip() for line in file.readlines()]
    return paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pkl', nargs='+', type=str,
                        help='The pkl files that will be read')
    parser.add_argument('--results', nargs='?', type=str,
                        help='The directory above the folder containing the pkl file to be read')
    parser.add_argument('--display', nargs='?', type=str, const='No',
                        help='Enter "Yes" or "yes" to display')

    args, remaining = parser.parse_known_args()

    pkl_paths = args.pkl
    results = args.results
    whether_dis = args.display

    if not pkl_paths:
        pkl_paths = []
        if not results:
            parser.error('Either --pkl or --results must be provided.')
        else:
            for folder_name in os.listdir(results):
                pkl_folder = os.path.join(results, folder_name)

                # 确保是文件夹而不是文件
                if os.path.isdir(pkl_folder):
                    pkl_file_path = os.path.join(pkl_folder, '000.pkl')
                    if os.path.exists(pkl_file_path):
                        pkl_paths.append(pkl_file_path)

    args = parse_config(remaining)
    dtype = torch.float32
    use_cuda = args.get('use_cuda', True)
    if use_cuda and torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    model_type = args.get('model_type', 'smplx')
    print('Model type:', model_type)
    print(args.get('model_folder'))
    model_params = dict(model_path=args.get('model_folder'),
                        #  joint_mapper=joint_mapper,
                        create_global_orient=True,
                        create_body_pose=not args.get('use_vposer'),
                        create_betas=True,
                        create_left_hand_pose=False,
                        create_right_hand_pose=False,
                        create_expression=False,
                        create_jaw_pose=False,
                        create_leye_pose=False,
                        create_reye_pose=False,
                        create_transl=False,
                        dtype=dtype,
                        **args)

    model = smplx.create(**model_params)
    model = model.to(device=device)

    batch_size = args.get('batch_size', 1)
    use_vposer = args.get('use_vposer', True)
    vposer, pose_embedding = [None, ] * 2
    vposer_ckpt = args.get('vposer_ckpt', '')
    if use_vposer:
        pose_embedding = torch.zeros([batch_size, 32],
                                     dtype=dtype, device=device,
                                     requires_grad=True)

        vposer_ckpt = osp.expandvars(vposer_ckpt)
        vposer, _ = load_vposer(vposer_ckpt, vp_model='snapshot')
        vposer = vposer.to(device=device)
        vposer.eval()

    for pkl_path in pkl_paths:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f, encoding='latin1')
        if use_vposer:
            with torch.no_grad():
                pose_embedding[:] = torch.tensor(
                    data['body_pose'], device=device, dtype=dtype)

        est_params = {}
        for key, val in data.items():
            if key == 'body_pose' and use_vposer:
                body_pose = vposer.decode(
                    pose_embedding, output_type='aa').view(1, -1)
                if model_type == 'smpl':
                    wrist_pose = torch.zeros([body_pose.shape[0], 6],
                                             dtype=body_pose.dtype,
                                             device=body_pose.device)
                    body_pose = torch.cat([body_pose, wrist_pose], dim=1)
                est_params['body_pose'] = body_pose
            else:
                est_params[key] = torch.tensor(val, dtype=dtype, device=device)

        model_output = model(**est_params)
        vertices = model_output.vertices.detach().cpu().numpy().squeeze()
        joints = model_output.joints.detach().cpu().numpy().squeeze()


        def write_joints_file(file_path, lines):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.writelines(lines)


        def write_and_clear_joints_files(joints, body_joint_file_path, hand_joint_file_path, face_joint_file_path):
            body_lines = []
            hand_lines = []
            face_lines = []

            for i in range(joints.shape[0]):
                x = joints[i, 0]
                y = joints[i, 1]
                z = joints[i, 2]

                if i < 25 or (i >= 60 and i <= 65):
                    line = "身体关节点 {}: x={}, y={}, z={}\n".format(i, x, y, z)
                    body_lines.append(line)
                    if i == 21 or i == 20:
                        line = "手关节点 {}: x={}, y={}, z={}\n".format(i, x, y, z)
                        hand_lines.append(line)



                elif (i >= 25 and i <= 54) or (i >= 66 and i <= 75):
                    line = "手关节点 {}: x={}, y={}, z={}\n".format(i, x, y, z)
                    hand_lines.append(line)
                else:
                    line = "脸关节点 {}: x={}, y={}, z={}\n".format(i, x, y, z)
                    face_lines.append(line)

            write_joints_file(body_joint_file_path, body_lines)
            write_joints_file(hand_joint_file_path, hand_lines)
            write_joints_file(face_joint_file_path, face_lines)

            print("关节点坐标已成功写入到记事本文件：")
            print("身体关节点：{}".format(body_joint_file_path))
            print("手关节点：{}".format(hand_joint_file_path))
            print("脸关节点：{}".format(face_joint_file_path))


        pkl_dir_name = os.path.dirname(pkl_path)
        pkl_base_name = os.path.basename(pkl_dir_name)

        body_joint_file_path = "./joints_output/{}/body_joints.txt".format(pkl_base_name)
        hand_joint_file_path = "./joints_output/{}/hand_joints.txt".format(pkl_base_name)
        face_joint_file_path = "./joints_output/{}/face_joints.txt".format(pkl_base_name)

        write_and_clear_joints_files(joints, body_joint_file_path, hand_joint_file_path, face_joint_file_path)

        out_mesh = trimesh.Trimesh(vertices, model.faces, process=False)
        material = pyrender.MetallicRoughnessMaterial(
            metallicFactor=0.0,
            alphaMode='OPAQUE',
            baseColorFactor=(1.0, 1.0, 0.9, 1.0))
        mesh = pyrender.Mesh.from_trimesh(
            out_mesh,
            material=material)

        scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0],
                               ambient_light=(0.3, 0.3, 0.3))

        # 注释掉展示整体人体模型的代码：
        # scene.add(mesh, 'mesh')

        # 添加展示身体关节点的代码：
        if whether_dis == "Yes" or whether_dis == "yes":
            sm = trimesh.creation.uv_sphere(radius=0.005)
            sm.visual.vertex_colors = [0.9, 0.1, 0.1, 1.0]
            tfs = np.tile(np.eye(4), (len(joints), 1, 1))

            # 修改关节数量，只保留身体关节点：
            num_body_joints = 25
            tfs = tfs[:num_body_joints + 6, :]
            tfs[:num_body_joints, :3, 3] = joints[:num_body_joints, :]
            tfs[num_body_joints:num_body_joints + 6, :3, 3] = joints[60:66, :]
            joints_pcl = pyrender.Mesh.from_trimesh(sm, poses=tfs)
            scene.add(joints_pcl)

            pyrender.Viewer(scene, use_raymond_lighting=True)
