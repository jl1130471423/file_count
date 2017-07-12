#coding:utf-8
import os
import socket
import datetime
import time
import glob
import pymysql
import apscheduler.schedulers.background
import math


#获取本机名
myname = socket.getfqdn(socket.gethostname())
#获取当前IP地址
myaddr = socket.gethostbyname(myname)

#获取服务器盘符函数
def getDriveLetters():
	import win32file
	import string
	driveletters = []
	for drive in string.ascii_uppercase:
		if win32file.GetDriveType(drive + ":") == win32file.DRIVE_FIXED:
			driveletters.append(drive + ":")
	return driveletters

#获取今日文件夹位置函数
def file_find():
	#获取今日日期
	now = datetime.datetime.now()
	strnow_day = now.strftime('%Y-%m-%d')
	m = 0
	n = len(getDriveLetters())
	file_list = []
	while m < n:
		file_path = glob.glob(r"%s/%s"%(getDriveLetters()[m],strnow_day))
		file_list = file_list + file_path
		m = m + 1
	return file_list
#工作函数
def work():
	# 连接数据库
	connect = pymysql.connect(
		port=3306,
		user='test',
		passwd='test',
		db='test',
		charset='utf8'
		)
	#获取游标
	cur = connect.cursor()
	'''
	创建数据表
	cur.execute("create table day_check(
				id int(4) primary key not null auto_increment,
				Hostname varchar(100),
				IP varchar(100),
				path varchar(100),
				file_update_date datetime,
				create_date datetime,
				cut_date int(4))")
	'''
	if len(file_find()) == 1:
		now = datetime.datetime.now()
		strnow = now.strftime('%Y-%m-%d %H:%M:%S')
		print ("The insert date is: %s" %strnow)
		file_first = str(file_find()[0])
		file_next = os.listdir(file_first)
		n = 0
		while n < len(file_next):
			file_dir = file_first+"/"+"%s" %file_next[n]
			dir_list = []
			for root, dirs, files in os.walk(file_dir):
				for file in files:
					file = os.path.join(root,file)
					dir_list.append(file)
			a = len(dir_list)
			b = a -1
			while b < a:
				my_dir = dir_list[b]
				print ("The recent file is: %s" %my_dir)
				statinfo = os.stat("%s" %my_dir)
				mtime = time.localtime(statinfo.st_mtime)
				update_time = time.strftime('%Y-%m-%d %H:%M:%S',mtime)
				print ("The file updatetime is: %s" %update_time)
				update_time_cut = datetime.datetime.fromtimestamp(time.mktime(time.strptime(update_time,"%Y-%m-%d %H:%M:%S")))
				cut_date = (abs(now-update_time_cut)).seconds/60
				#插入数据
				cur.execute("insert ignore into day_check(id,Hostname,IP,path,file_update_date,create_date,cut_date) values(null,%s,%s,%s,%s,now(),%s)",(myname,myaddr,my_dir,update_time,cut_date))
				b = b + 1
			n = n + 1
	elif len(file_find()) == 2:
		now = datetime.datetime.now()
		strnow = now.strftime('%Y-%m-%d %H:%M:%S')
		print ("The insert date is: %s" %strnow)
		file_first1 = str(file_find()[0])
		file_first2 = str(file_find()[1])
		file_next1 = os.listdir(file_first1)
		file_next2 = os.listdir(file_first2)
		#当日文件更新时间对比并选取最新的文件夹入库
		statinfo_1 = os.stat("%s" %file_find()[0])
		mtime_1 = time.localtime(statinfo_1.st_mtime)
		update_time_1 = time.strftime('%Y-%m-%d %H:%M:%S',mtime_1)
		update_time_cut_1 = datetime.datetime.fromtimestamp(time.mktime(time.strptime(update_time_1,"%Y-%m-%d %H:%M:%S")))
		statinfo_2 = os.stat("%s" %file_find()[1])
		mtime_2 = time.localtime(statinfo_2.st_mtime)
		update_time_2 = time.strftime('%Y-%m-%d %H:%M:%S',mtime_2)
		update_time_cut_2 = datetime.datetime.fromtimestamp(time.mktime(time.strptime(update_time_2,"%Y-%m-%d %H:%M:%S")))
		#判断最新生成的文件夹
		if update_time_cut_1 > update_time_cut_2:
			n = 0
			while n < len(file_next1):
				file_dir1 = file_first1+"/"+"%s" %file_next1[n]
				dir_list1 = []
				for root, dirs, files in os.walk(file_dir1):
					for file in files:
						file = os.path.join(root,file)
						dir_list1.append(file)
				a = len(dir_list1)
				b = a -1
				while b < a:
					my_dir1 = dir_list1[b]
					print ("The recent file is: %s" %my_dir1)
					statinfo = os.stat("%s" %my_dir1)
					mtime = time.localtime(statinfo.st_mtime)
					update_time1 = time.strftime('%Y-%m-%d %H:%M:%S',mtime)
					print ("The file updatetime is: %s" %update_time1)
					update_time_cut1 = datetime.datetime.fromtimestamp(time.mktime(time.strptime(update_time1,"%Y-%m-%d %H:%M:%S")))
					cut_date1 = (abs(now-update_time_cut1)).seconds/60
					#插入数据
					cur.execute("insert ignore into day_check(id,Hostname,IP,path,file_update_date,create_date,cut_date) values(null,%s,%s,%s,%s,now(),%s)",(myname,myaddr,my_dir1,update_time1,cut_date1))
					b = b + 1
				n = n + 1
		elif update_time_cut_2 > update_time_cut_1:
			m = 0
			while m < len(file_next2):
				file_dir2 = file_first2+"/"+"%s" %file_next2[m]
				dir_list2 = []
				for root, dirs, files in os.walk(file_dir2):
					for file in files:
						file = os.path.join(root,file)
						dir_list2.append(file)
				c = len(dir_list2)
				d = c -1
				while d < c:
					my_dir2 = dir_list2[d]
					print ("The recent file is: %s" %my_dir2)
					statinfo = os.stat("%s" %my_dir2)
					mtime = time.localtime(statinfo.st_mtime)
					update_time2 = time.strftime('%Y-%m-%d %H:%M:%S',mtime)
					print ("The file updatetime is: %s" %update_time2)
					update_time_cut2 = datetime.datetime.fromtimestamp(time.mktime(time.strptime(update_time2,"%Y-%m-%d %H:%M:%S")))
					#插入数据
					cur.execute("insert ignore into day_check(id,Hostname,IP,path,file_update_date,create_date,cut_date) values(null,%s,%s,%s,%s,now(),%s)",(myname,myaddr,my_dir2,update_time2,cut_date2))
					d = d + 1
				m = m + 1
	#关闭数据库连接
	cur.close()
	connect.commit()
	connect.close()


#程序每天定时执行
if __name__ == '__main__':
  scheduler = apscheduler.schedulers.background.BlockingScheduler()
  scheduler.add_job(work,'cron',second='0',minute='*/10',hour='*')
  print ('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
  try:
    scheduler.start()
  except (KeyboardInterrupt,SystemExit):
    scheduler.shutdown()
