# WX_jump
* 微信跳一跳 非原创，根据看别人教程学习开发思路，记录一下方便日后自己查看
## 大致思路
* 现在主函数列出实现步骤的方法，方法里可能有哪些参数，再分别取定义各个实现方法
* 1.先读取配置config
* 2.进行截图
* 3.分析截图里棋子跟棋盘的位置
* 4.根据位置算出距离，按压系数没在代码里实现 应该是通过不断调试得出
* 5.实现调的方法
### 准备阶段
* 1.配置adb环境，具体百度
*  手机连接电脑，cmd输入adb devices可看到手机设备ID即可
* 2.安装模块，里面用到的有
*    from concurrent.futures import process
*    from PIL import Image
*    import json
*    import os
*    import random
*    import subprocess
*    import time
*    import re
* 3.里面会用到一下adb shell命令，可先大致了解

### 实现阶段
* 1.adb shell wm size 获取手机屏幕分辨率 
  adb shell screencap -p 实现截图 
  adb shell input swipe {x1} {y1} {x2} {y2} {duration}  屏幕按压的操作
* 2.文件读取操作
  with open() as f:
* 3.代码中的难点在扫描棋子跟棋盘部分，有多个for循环 理解好这个，剩下的基本OK
  





