# coding:utf-8
import PyQt5
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import cv2

class myLabel(QLabel):
	def __init__(self):
		super(myLabel, self).__init__()
		# 矩形框开始和结束位置
		self.start_x = 0
		self.start_y = 0
		self.end_x = 0
		self.end_y = 0
		# draw_flag画框标志位，adjust_flag调整框大小标志位，drag_flag拖拽标志位
		self.draw_flag = False
		self.adjust_flag = False
		self.drag_flag = False
		# 当调整框大小标志位生效时，分为四种情况，分别是对四条边的操作
		self.left = False
		self.bottom = False
		self.right = False
		self.top = False
		# 矩形框拖拽时鼠标光标起点，当按下鼠标拖拽时drag_rectangle标志位生效
		# 同时记录矩形框的宽度和高度
		self.drag_start_x = 0
		self.drag_start_y = 0
		self.drag_rectangle = False
		self.rectangle_width = 0
		self.rectangle_height = 0
	def get_four_point(self):
		# 分别得到矩形框四条边的中点
		point_top = ((self.start_x + self.end_x) // 2, self.start_y)
		point_bottom = ((self.start_x + self.end_x) // 2, self.end_y)
		point_left = (self.start_x, (self.start_y + self.end_y) // 2)
		point_right = (self.end_x, (self.start_y + self.end_y) // 2)
		return (point_top, point_bottom, point_left, point_right)
	def border_process(self):
		# 边界处理，当绘制矩形框或调整框的大小时将边界进行限制
		self.start_x = max(0, self.start_x)
		self.start_x = min(self.start_x, self.width())
		self.start_y = max(0, self.start_y)
		self.start_y = min(self.start_y, self.height())
		self.end_x = max(0, self.end_x)
		self.end_x = min(self.end_x, self.width())
		self.end_y = max(0, self.end_y)
		self.end_y = min(self.end_y, self.height())
	def move_process(self):
		# 边界处理，当拖拽矩形框超出显示界面时将边界进行限制，保持矩形框的长和宽不变
		temp_start_x = min(self.start_x, self.end_x)
		temp_end_x = max(self.start_x, self.end_x)
		temp_start_y = min(self.start_y, self.end_y)
		temp_end_y = max(self.start_y, self.end_y)
		if temp_start_x <= 0:
			temp_start_x = 0
			temp_end_x = self.rectangle_width
			if temp_start_y <= 0:
				temp_start_y = 0
				temp_end_y = self.rectangle_height
			elif temp_end_y >= self.height():
				temp_end_y = self.height()
				temp_start_y = temp_end_y - self.rectangle_height
			else:
				pass
		elif temp_end_x >= self.width():
			temp_end_x = self.width()
			temp_start_x = temp_end_x - self.rectangle_width
			if temp_start_y <= 0:
				temp_start_y = 0
				temp_end_y = self.rectangle_height
			else:
				pass
		else:
			if temp_start_y <= 0:
				temp_start_y = 0
				temp_end_y = self.rectangle_height
			elif temp_end_y >= self.height():
				temp_end_y = self.height()
				temp_start_y = temp_end_y - self.rectangle_height
			else:
				pass
		self.start_x, self.end_x, self.start_y, self.end_y = temp_start_x, temp_end_x, temp_start_y, temp_end_y
	def mousePressEvent(self,event):
		# 鼠标按下事件
		# adjust_flag和drag_flag分别是对矩形框大小调整和矩形框位置调整的标志位，
		# 当其中有任何一个为True时，表明矩形框已经绘制完成，否则表明当前事件为准备绘制
		print(self.adjust_flag, self.drag_flag)
		if not (self.adjust_flag or self.drag_flag):
			self.draw_flag = True
			self.start_x = event.x()
			self.start_y = event.y()
			self.end_x = event.x()
			self.end_y = event.y()
		else:
			# 判断当前鼠标的形状，从而判断当前操作状态
			# 6表明鼠标是左右调整大小
			# 5表明鼠标是上下调整大小
			# 9表示鼠标光标在矩形框内部
			# 对于鼠标大小调整和位置调整均需要触发两个Flag的改变
			# 对于大小调整，有adjust_flag和
			# 				left、right、top、bottom共两层Flag
			# 对于位置调整，有drag_flag和
			#				drag_rectangle两层Flag
			if self.cursor().shape() == 6:
				if abs(event.x() - self.start_x) <= abs(event.x() - self.end_x):
					self.left = True
				else:
					self.right = True
			elif self.cursor().shape() == 5:
				if abs(event.y() - self.start_y) <= abs(event.y() - self.end_y):
					self.top = True
				else:
					self.bottom = True
			elif self.cursor().shape() == 9:
				self.drag_start_x = event.x()
				self.drag_start_y = event.y()
				self.rectangle_width = abs(self.start_x - self.end_x)
				self.rectangle_height = abs(self.start_y - self.end_y)
				self.drag_rectangle = True
	def mouseReleaseEvent(self,event):
		if self.draw_flag:
			self.draw_flag = False
			# 单击鼠标左键时删除当前矩形框，并在左上角画长宽为0的框
			if self.start_x == self.end_x and self.start_y == self.end_y:
				self.start_x = self.start_y = self.end_x = self.end_y = 0
				self.update()
		else:
			if self.adjust_flag:
				self.left = False
				self.right = False
				self.top = False
				self.bottom = False
				self.adjust_flag = False
			if self.drag_flag:
				self.drag_flag = False
				if self.drag_rectangle:
					self.drag_rectangle = False
	# 判断矩形框边长的四个中点(all_points)是否在传入的四个参数围成的矩形框中
	def judge_cursor_on_line(self, current_x_min, current_x_max, current_y_min, current_y_max):
		flag = False
		all_points = self.get_four_point()
		if abs(all_points[0][0] - current_x_min) + abs(all_points[0][0] - current_x_max) <= 6:
			if abs(all_points[0][1] - current_y_min) + abs(all_points[0][1] - current_y_max) <= 6 \
			 		or abs(all_points[1][1] - current_y_min) + abs(all_points[1][1] - current_y_max) <= 6:
				self.setCursor(Qt.SizeVerCursor)
				self.adjust_flag = True
				self.drag_flag = False
				flag = True
			# else不可省，因为可能会出现内层if条件不满足但是外层if条件满足的情况
			# 这样就会造成一个情况，x在指定范围内，但是y超出了范围，结果就是鼠标光标不会发生改变
			else:
				self.adjust_flag = False
				self.drag_flag = False
		elif abs(all_points[2][1] - current_y_min) + abs(all_points[2][1] - current_y_max) <= 6:
			if abs(all_points[2][0] - current_x_min) + abs(all_points[2][0] - current_x_max) <= 6 \
			 		or abs(all_points[3][0] - current_x_min) + abs(all_points[3][0] - current_x_max) <= 6:
				self.setCursor(Qt.SizeHorCursor)
				self.adjust_flag = True
				self.drag_flag = False
				flag = True
			# else不可省，同上
			else:
				self.adjust_flag = False
				self.drag_flag = False
		return flag
	def mouseMoveEvent(self,event):
		# 当鼠标移动到矩形框边的中点或鼠标处于矩形框内部时，鼠标光标会发生改变
		# 此时会分别触发adjust_flag和drag_flag一级标志位
		# 当前面的条件满足时，按动鼠标才会触发二级标志位([left, top, right, bottom], [drag_rectangle])
		current_x_min, current_x_max = event.x() - 3, event.x() + 3
		current_y_min, current_y_max = event.y() -3, event.y() + 3
		# 使用鼠标绘制矩形框
		if self.draw_flag:
			self.end_x = event.x()
			self.end_y = event.y()
			self.border_process()
			# 重新绘制图像
			self.update()
		# 使用鼠标调整矩形框大小
		elif self.left or self.right or self.top or self.bottom:
			if self.left:
				self.start_x = event.x()
			elif self.right:
				self.end_x = event.x()
			elif self.top:
				self.start_y = event.y()
			elif self.bottom:
				self.end_y = event.y()
			self.border_process()
			self.update()
		# 使用鼠标拖拽矩形框，更改矩形框位置
		elif self.drag_rectangle:
			x_move = event.x() - self.drag_start_x
			y_move = event.y() - self.drag_start_y
			self.start_x += x_move
			self.start_y += y_move
			self.end_x += x_move
			self.end_y += y_move
			self.drag_start_x = event.x()
			self.drag_start_y = event.y()
			self.move_process()
			self.update()
		# 上面条件均不满足，即鼠标不按下的情况下移动
		else:
			# 判断矩形框四个边的中点是否在以当前鼠标光标位置为中心，边长为6的邻域内
			# 问题转换为判断一个点是否在一个矩形内
			# 对于x的判断，可以将x与起点和终点分别求距离，再求和，如果等于矩形的宽，则表明该点的x处于矩形的水平范围内
			# 对于y的判断，同上
			if self.judge_cursor_on_line(current_x_min, current_x_max, current_y_min, current_y_max):
				pass
			else:
				if abs(event.x() - self.start_x) + abs(event.x() - self.end_x) <= abs(self.start_x - self.end_x) and \
					abs(event.y() - self.start_y) + abs(event.y() - self.end_y) <= abs(self.start_y - self.end_y):
					self.setCursor(Qt.SizeAllCursor)
					self.drag_flag = True
					self.adjust_flag = False
				else:
					self.drag_flag = False
					self.adjust_flag = False
					self.setCursor(Qt.CrossCursor)
	def paintEvent(self, event):
		# 每次调用update时会触发该函数
		super(myLabel, self).paintEvent(event)
		rect = QRect(min(self.start_x, self.end_x), min(self.start_y, self.end_y), abs(self.end_x-self.start_x), abs(self.end_y-self.start_y))
		painter = QPainter(self)
		painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
		painter.drawRect(rect)
		points = self.get_four_point()
		square_color = QColor()
		square_color.setNamedColor('black')
		# painter.fillRect(points[0][0]-3, points[0][1]-3, 6, 6, QColor(0xCCCC66))
		painter.fillRect(points[0][0], points[0][1]-3, 6, 6, square_color)
		painter.fillRect(points[1][0]-3, points[1][1]-3, 6, 6, square_color)
		painter.fillRect(points[2][0]-3, points[2][1]-3, 6, 6, square_color)
		painter.fillRect(points[3][0]-3, points[3][1]-3, 6, 6, square_color)


class Example(QWidget):
	def __init__(self):
		super(Example, self).__init__()
		self.initUI()
	def initUI(self):
		self.mainlayout = QVBoxLayout()
		self.setWindowTitle('xyp first pyqt opencv test')

		self.lb = myLabel()
		self.img = cv2.imread('1.jpg')
		height, width, bytesPerComponent = self.img.shape
		bytesPerLine = 3 * width
		cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB, self.img)
		QImg = QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888)
		pixmap = QPixmap.fromImage(QImg)

		self.lb.setPixmap(pixmap)
		self.lb.setCursor(Qt.CrossCursor)
		self.lb.setFocusPolicy(Qt.ClickFocus)
		self.lb.setMouseTracking(True)
		self.mainlayout.addWidget(self.lb)

		self.setLayout(self.mainlayout)
		self.setGeometry(100, 100, 300, 300)

		self.show()
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter:
			start_x, start_y = min(self.lb.start_x, self.lb.end_x), min(self.lb.start_y, self.lb.end_y)
			end_x, end_y = max(self.lb.start_x, self.lb.end_x), max(self.lb.start_y, self.lb.end_y)
			cv2.imwrite('result.jpg', self.img[start_y:end_y, start_x:end_x, ::-1])
		if event.key() == Qt.Key_Escape:
			self.close()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())