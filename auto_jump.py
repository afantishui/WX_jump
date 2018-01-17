#!/usr/bin/env python
# -*- coding:utf-8 -*-
from concurrent.futures import process

from PIL import Image
import json
import os
import random
import subprocess
import time
import re


def get_screen_size():
	# 获取屏幕分辨率
	# 1920*1080
	size_str = os.popen('adb shell wm size').read()
	if not size_str:
		print('请安装adb 及驱动并配置环境变量')
		exit()

	m = re.search(r'(\d+)x(\d+)',size_str)
	if m:
		print(m)
		return "%sx%s" % (m.group(2),m.group(1))


def init():
	# 初始化配置，检查环境
	# 获取分辨率
	screen_size = get_screen_size()
	# 配置文件路径
	config_file_path = 'config\\%s\\config.json' % screen_size

	if os.path.exists(config_file_path):
		with open(config_file_path,'r') as f:
			print('Load config file from %s' % config_file_path)
			return json.loads(f.read())  # 使用json返回配置
	else:
		with open(config_file_path,'r') as f:
			print('Load config file from %s' % config_file_path)
			return json.loads(f.read())  # 使用json返回配置


def get_screenshot():
	# 获取截图 auto.png
	process = subprocess.Popen('adb shell screencap -p', shell = True, stdout = subprocess.PIPE)
	screenshot = process.stdout.read()
	# 转码
	screenshot = screenshot.replace(b'\r\r\n', b'\n')
	with open('auto.png','wb') as f:
		f.write(screenshot)


def find_piece_board(img,config):
	# 根据图片和配置文件找到棋盘 棋子坐标
	# 获取图片的宽和高
	w,h = img.size
	board_x = 0
	board_y = 0
	# 扫描起始y坐标
	scan_start_y = 0
	#棋子最大y坐标
	piece_y_max = 0
	board_y_max = 0
	# 图片的像素矩阵
	img_pixel = img.load()
	# 根据屏幕颜色 判断是否循环
	LOOP = False
	if not LOOP:
		if sum(img_pixel[5,5][:-1]) < 150:
			exit('退出游戏')
	# 以50px 为步长扫描 测试出最高点
	for i in range(h//3,h*2//3,50):
		first_pixel = img_pixel[0,i]
		for j in range(0,w):
			pixel = img_pixel[j,i]
			# 如果不是纯色的 就跳出，说明找到了y轴最大值
			if first_pixel[:-1] != pixel[:-1]:
				#  -50是因为以50px进行扫描，要减回误差
				scan_start_y = i - 50
				break
			if scan_start_y:
				break
	# 开始扫描棋子
	left = 0
	right = 0
	for i in range(scan_start_y,h*2//3):
		flag = True # 监测颜色标记，当监测到颜色时设为Flaser
		# 切除左右画面八分之一
		for j in range(w//8,w*7//8):
			pixel = img_pixel[j,i]
			# 根据棋子颜色判断，找到最后一行的点起始后末尾,从截图取点分析到RGB颜色为55,60,102 适当判断是否满足取值范围
			if(50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
				if flag :
					left = j # j是左边x坐标
					flag = False
				right = j # j是右边x坐标
				piece_y_max = max(i,piece_y_max) #比较最大值
	piece_x = (left + right)//2
	piece_y = piece_y_max - config["piece_base_height_1_2"] # 底部Y左边减去20偏差就是中心位置
	print(piece_x,piece_y)

	# 开始扫描棋盘
	if piece_x < w//2:
		board_x_start = piece_x
		board_x_end = w
	else:
		board_x_start = 0
		board_x_end = piece_x

	for i in range(int(h//3),int(h*2//3)):
		last_pixel = img_pixel[0,i]
		if board_x or board_y:
			break
		board_x_sum = 0
		board_x_c = 0

		for j in range(int(board_x_start),int(board_x_end)):
			pixel = img_pixel[j,i]
			if abs(j - piece_x) < config["piece_body_width"]:
				continue
			# 修掉圆顶的时候一条线导致的小 bug，这个颜色判断应该 OK，暂时不提出来
			if abs(pixel[0] - last_pixel[0]) \
					+ abs(pixel[1] - last_pixel[1]) \
					+ abs(pixel[2] - last_pixel[2]) > 10:
				board_x_sum += j
				board_x_c += 1
		if board_x_sum:
			board_x = board_x_sum // board_x_c
	last_pixel = img_pixel[board_x,i]
	# 从上顶点往下 +274 的位置开始向上找颜色与上顶点一样的点，为下顶点
	# 该方法对所有纯色平面和部分非纯色平面有效，对高尔夫草坪面、木纹桌面、
	# 药瓶和非菱形的碟机（好像是）会判断错误

	for k in range(i + 274,i,-1):
		pixel = img_pixel[board_x,k]
		if abs(pixel[0] - last_pixel[0]) \
				+ abs(pixel[1] - last_pixel[1]) \
				+ abs(pixel[2] - last_pixel[2]) < 10:
			break
	board_y = int((i +k)//2)

	for j in range(i ,i+200):
		pixel = img_pixel[board_x,j]
		if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[2] - 245) == 0:
			board_y = j + 10
			break

	if not all((board_x,board_y)):
		return 0,0,0,0
	print(piece_x,piece_y,board_x,board_y)
	return piece_x,piece_y,board_x,board_y


def test_piece():
	# 测试输出棋子中心坐标
	config = init()
	img = Image.open('auto.png')
	find_piece_board(img, config)


def jump(distance,point,ration):
	# 跳一段距离
	press_time = distance * ration
	press_time = max(press_time,200) # 设置200s为最小按压时间
	press_time = int(press_time)
	cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
		x1 = point[0],
		y1 = point[1],
		x2 = point[0] + random.randint(0,3),
		y2 = point[1] + random.randint(0,3),
		duration = press_time
		)
	print(cmd)
	os.system(cmd)
	return press_time


# 主函数
def run():
	# 获取配置，检查环境
	config = init()
	print(config)

	# 循环操作
	while True:
		# 获取截图
		get_screenshot()
		# 打开图片
		img = Image.open('auto.png')
		# 分析棋子 棋盘坐标 piece 棋子 board 棋盘
		piece_x,piece_y,board_x,board_y = find_piece_board(img,config)
		print(piece_x,piece_y,board_x,board_y,'------------->')
		# 棋子与棋盘算距离 勾股定理
		distance =((piece_x - board_x)**2 + (piece_y - board_y)**2)**0.5
		# 生产一个随机按压点
		press_point = (random.randint(*config['swipe']['x']),
						random.randint(*config['swipe']['x']))
		# 根据距离 算出按压系数 然后跳
		jump(distance,press_point,config['press_ration'])
		# 随机间隔1-3秒，防检查  random.random()获取0-1随机数
		time.sleep(1+random.random()*2)


if __name__ == '__main__':
	# test_piece()
	run()