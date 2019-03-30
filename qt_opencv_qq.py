# coding:utf-8
import PyQt5
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import cv2
import numpy as np
import copy


class myLabel(QLabel):
    def __init__(self, image_width, image_height):
        super(myLabel, self).__init__()
        self.image_width = image_width
        self.image_height = image_height

        self.upper_left_corner_limit_x = 0
        self.upper_left_corner_limit_y = 0
        self.set_initial_variable()
        self.is_entry_key = False
        self.windowIsMaximum = False

        self.is_outside_the_image = False

    def set_initial_variable(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.draw_flag = False
        self.adjust_flag = False
        self.drag_flag = False

        self.left = False
        self.bottom = False
        self.right = False
        self.top = False
        self.top_left = False
        self.bottom_left = False
        self.top_right = False
        self.bottom_right = False

        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_rectangle = False
        self.rectangle_width = 0
        self.rectangle_height = 0

    def get_eight_point(self):
        allPoints = {}
        point_top = ((self.start_x + self.end_x) // 2, self.start_y)
        point_bottom = ((self.start_x + self.end_x) // 2, self.end_y)
        point_left = (self.start_x, (self.start_y + self.end_y) // 2)
        point_right = (self.end_x, (self.start_y + self.end_y) // 2)
        point_top_left = (self.start_x, self.start_y)
        point_bottom_left = (self.start_x, self.end_y)
        point_top_right = (self.end_x, self.start_y)
        point_bottom_right = (self.end_x, self.end_y)
        allPoints['point_top'] = point_top
        allPoints['point_bottom'] = point_bottom
        allPoints['point_left'] = point_left
        allPoints['point_right'] = point_right
        allPoints['point_top_left'] = point_top_left
        allPoints['point_bottom_left'] = point_bottom_left
        allPoints['point_top_right'] = point_top_right
        allPoints['point_bottom_right'] = point_bottom_right
        return allPoints

    def border_process(self):
        self.start_x = max(self.upper_left_corner_limit_x, self.start_x)
        self.start_x = min(self.start_x, self.image_width)
        self.start_y = max(self.upper_left_corner_limit_y, self.start_y)
        self.start_y = min(self.start_y, self.image_height)
        self.end_x = max(self.upper_left_corner_limit_x, self.end_x)
        self.end_x = min(self.end_x, self.image_width)
        self.end_y = max(self.upper_left_corner_limit_y, self.end_y)
        self.end_y = min(self.end_y, self.image_height)

    def move_process(self):
        temp_start_x = min(self.start_x, self.end_x)
        temp_end_x = max(self.start_x, self.end_x)
        temp_start_y = min(self.start_y, self.end_y)
        temp_end_y = max(self.start_y, self.end_y)
        if temp_start_x <= self.upper_left_corner_limit_x:
            temp_start_x = self.upper_left_corner_limit_x
            temp_end_x = self.rectangle_width + temp_start_x
            if temp_start_y <= self.upper_left_corner_limit_y:
                temp_start_y = self.upper_left_corner_limit_y
                temp_end_y = self.rectangle_height + temp_start_y
            elif temp_end_y >= self.image_height:
                temp_end_y = self.image_height
                temp_start_y = temp_end_y - self.rectangle_height
            else:
                pass
        elif temp_end_x >= self.image_width:
            temp_end_x = self.image_width
            temp_start_x = temp_end_x - self.rectangle_width
            if temp_start_y <= self.upper_left_corner_limit_y:
                temp_start_y = self.upper_left_corner_limit_y
                temp_end_y = self.rectangle_height + temp_start_y
            elif temp_end_y >= self.image_height:
                temp_end_y = self.image_height
                temp_start_y = temp_end_y - self.rectangle_height
            else:
                pass
        else:
            if temp_start_y <= self.upper_left_corner_limit_y:
                temp_start_y = self.upper_left_corner_limit_y
                temp_end_y = self.rectangle_height + temp_start_y
            elif temp_end_y >= self.image_height:
                temp_end_y = self.image_height
                temp_start_y = temp_end_y - self.rectangle_height
            else:
                pass
        self.start_x, self.end_x, self.start_y, self.end_y = temp_start_x, temp_end_x, temp_start_y, temp_end_y

    def mousePressEvent(self, event):
        print("事件获得的位置坐标：", event.x(), event.y())
        # 判断当前点是否超出图像边界

        if event.x() < self.upper_left_corner_limit_x or event.x() > self.image_width or \
                event.y() < self.upper_left_corner_limit_y or event.y() > self.image_height:
            self.is_outside_the_image = True
            self.setCursor(Qt.ArrowCursor)
            self.update()
            return

        if not (self.adjust_flag or self.drag_flag):
            self.draw_flag = True
            self.start_x = event.x()
            self.start_y = event.y()
            self.end_x = event.x()
            self.end_y = event.y()
        else:
            # 水平光标
            if self.cursor().shape() == 6:
                if abs(event.x() - self.start_x) <= abs(event.x() - self.end_x):
                    self.left = True
                else:
                    self.right = True
            # 垂直光标
            elif self.cursor().shape() == 5:
                if abs(event.y() - self.start_y) <= abs(event.y() - self.end_y):
                    self.top = True
                else:
                    self.bottom = True
            # 光标斜向上
            elif self.cursor().shape() == 7:
                if abs(event.x() - self.start_x) <= abs(event.x() - self.end_x) and \
                        abs(event.y() - self.end_y) <= abs(event.y() - self.start_y):
                    self.bottom_left = True
                else:
                    self.top_right = True
            # 光标斜向下
            elif self.cursor().shape() == 8:
                if abs(event.x() - self.start_x) <= abs(event.x() - self.end_x) and \
                        abs(event.y() - self.start_y) <= abs(event.y() - self.end_y):
                    self.top_left = True
                else:
                    self.bottom_right = True
            elif self.cursor().shape() == 9:
                self.drag_start_x = event.x()
                self.drag_start_y = event.y()
                self.rectangle_width = abs(self.start_x - self.end_x)
                self.rectangle_height = abs(self.start_y - self.end_y)
                self.drag_rectangle = True

    def mouseReleaseEvent(self, event):
        if self.draw_flag:
            self.draw_flag = False
            if abs(self.start_x - self.end_x) <= 1 and abs(self.start_y - self.end_y) <= 1:
                self.start_x = self.end_x = self.upper_left_corner_limit_x
                self.start_y = self.end_y = self.upper_left_corner_limit_y
                self.update()
        else:
            if self.adjust_flag:
                self.left = False
                self.right = False
                self.top = False
                self.bottom = False
                self.top_left = False
                self.top_right = False
                self.bottom_left = False
                self.bottom_right = False
                self.adjust_flag = False
            if self.drag_flag:
                self.drag_flag = False
                if self.drag_rectangle:
                    self.drag_rectangle = False

    def judge_cursor_on_point(self, current_x, current_y):
        all_points = self.get_eight_point()
        current_point = (current_x, current_y)
        if self.twoPointDistance(all_points['point_top'], current_point) or self.twoPointDistance(
                all_points['point_bottom'], current_point):
            # 设置垂直光标
            self.setCursor(Qt.SizeVerCursor)
            self.adjust_flag = True
            self.drag_flag = False
            flag = True
        elif self.twoPointDistance(all_points['point_left'], current_point) or self.twoPointDistance(
                all_points['point_right'], current_point):
            # 设置水平光标
            self.setCursor(Qt.SizeHorCursor)
            self.adjust_flag = True
            self.drag_flag = False
            flag = True
        elif self.twoPointDistance(all_points['point_top_left'], current_point) or self.twoPointDistance(
                all_points['point_bottom_right'], current_point):
            # 设置斜向下光标
            self.setCursor(Qt.SizeFDiagCursor)
            self.adjust_flag = True
            self.drag_flag = False
            flag = True
        elif self.twoPointDistance(all_points['point_bottom_left'], current_point) or self.twoPointDistance(
                all_points['point_top_right'], current_point):
            # 设置斜向上光标
            self.setCursor(Qt.SizeBDiagCursor)
            self.adjust_flag = True
            self.drag_flag = False
            flag = True
        else:
            self.adjust_flag = False
            self.drag_flag = False
            flag = False
        return flag

    def twoPointDistance(self, point1, point2):
        LimitRange = 10
        if (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 <= LimitRange:
            return True
        else:
            return False

    def mouseMoveEvent(self, event):
        current_x, current_y = event.x(), event.y()
        if self.draw_flag:
            self.end_x = event.x()
            self.end_y = event.y()
            self.border_process()
            self.update()
        elif self.left or self.right or self.top or self.bottom or self.top_left or \
                self.bottom_left or self.top_right or self.bottom_right:
            if self.left:
                self.start_x = event.x()
            elif self.right:
                self.end_x = event.x()
            elif self.top:
                self.start_y = event.y()
            elif self.bottom:
                self.end_y = event.y()
            elif self.top_left:
                self.start_x = event.x()
                self.start_y = event.y()
            elif self.bottom_left:
                self.start_x = event.x()
                self.end_y = event.y()
            elif self.top_right:
                self.start_y = event.y()
                self.end_x = event.x()
            elif self.bottom_right:
                self.end_x = event.x()
                self.end_y = event.y()

            self.border_process()
            self.update()
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
        else:
            # 如果光标在点的附近
            if self.judge_cursor_on_point(current_x, current_y):
                pass
            else:
                # 如果鼠标在那个框的里面或框的线上但不在点的附近
                if abs(event.x() - self.start_x) + abs(event.x() - self.end_x) <= abs(self.start_x - self.end_x) and \
                        abs(event.y() - self.start_y) + abs(event.y() - self.end_y) <= abs(self.start_y - self.end_y):
                    # 双箭头标签
                    self.setCursor(Qt.SizeAllCursor)
                    self.drag_flag = True
                    self.adjust_flag = False
                else:
                    # 如果鼠标在那个框外的外面时，设置光标为十字架
                    self.drag_flag = False
                    self.adjust_flag = False

                    self.setCursor(Qt.CrossCursor)

    def paintEvent(self, event):
        super(myLabel, self).paintEvent(event)

        if self.is_outside_the_image is True:
            self.is_outside_the_image = False
            return

        if not self.is_entry_key:
            # print('self.draw_flag,self.adjust_flag,self.drag_flag', self.draw_flag, self.adjust_flag, self.drag_flag)
            if self.windowIsMaximum is False:
                if self.draw_flag or self.adjust_flag or self.drag_flag:
                    self.paintRect()
            else:
                if self.start_x == self.upper_left_corner_limit_x and self.start_y == self.upper_left_corner_limit_y and \
                        self.end_x == self.upper_left_corner_limit_x and self.end_y == self.upper_left_corner_limit_y:
                    pass
                else:
                    self.paintRect()
        else:
            pass

    def paintRect(self):
        # print('ffffffs')
        rect = QRect(min(self.start_x, self.end_x), min(self.start_y, self.end_y),
                     abs(self.end_x - self.start_x),
                     abs(self.end_y - self.start_y))
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
        painter.drawRect(rect)
        allPoints = self.get_eight_point()
        square_color = QColor()
        square_color.setNamedColor('black')
        painter.fillRect(allPoints['point_top'][0] - 3, allPoints['point_top'][1] - 3, 6, 6, square_color)
        painter.fillRect(allPoints['point_bottom'][0] - 3, allPoints['point_bottom'][1] - 3, 6, 6, square_color)
        painter.fillRect(allPoints['point_left'][0] - 3, allPoints['point_left'][1] - 3, 6, 6, square_color)
        painter.fillRect(allPoints['point_right'][0] - 3, allPoints['point_right'][1] - 3, 6, 6, square_color)
        painter.fillRect(allPoints['point_top_left'][0] - 3, allPoints['point_top_left'][1] - 3, 6, 6,
                         square_color)
        painter.fillRect(allPoints['point_bottom_left'][0] - 3, allPoints['point_bottom_left'][1] - 3, 6, 6,
                         square_color)
        painter.fillRect(allPoints['point_top_right'][0] - 3, allPoints['point_top_right'][1] - 3, 6, 6,
                         square_color)
        painter.fillRect(allPoints['point_bottom_right'][0] - 3, allPoints['point_bottom_right'][1] - 3, 6, 6,
                         square_color)


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.is_press_Enter_key = False
        self.window_maximum_flag = False
        self.move_w = 0
        self.move_h = 0
        self.initUI()

    def initUI(self):
        self.mainlayout = QVBoxLayout()
        self.setWindowTitle('xyp first pyqt opencv test')

        try:
            self.img = cv2.imread('1.jpg')
        except:
            return
        height, width, bytesPerComponent = self.img.shape

        self.lb = myLabel(width, height)

        print('self.img.shape', self.img.shape)

        bytesPerLine = 3 * width
        cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB, self.img)
        QImg = QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        self.lb.setPixmap(pixmap)

        # self.lb.setCursor(Qt.CrossCursor)
        # self.lb.setCursor(Qt.PointingHandCursor)

        self.lb.setFocusPolicy(Qt.ClickFocus)
        self.lb.setMouseTracking(True)
        self.lb.setAlignment(Qt.AlignCenter)
        self.mainlayout.addWidget(self.lb)
        self.setLayout(self.mainlayout)

        # print('窗口尺寸', self.width(), self.height())
        # print('此QLabel的尺寸', self.lb.width(), self.lb.height())
        self.show()

    def changeEvent(self, e):
        if e.type() == QtCore.QEvent.WindowStateChange:
            print('窗口改变')
            self.lb.windowIsMaximum = True

            self.original_image_w = self.img.shape[1]
            self.original_image_h = self.img.shape[0]
            if self.isMinimized():
                pass
            elif self.isMaximized():
                if self.window_maximum_flag is False:
                    self.original_image_w = self.img.shape[1]
                    self.original_image_h = self.img.shape[0]
                    print("窗口最大化")
                    print('label的宽和高', self.lb.image_width, self.lb.image_height)
                    self.move_w = (self.lb.width() - self.original_image_w) // 2
                    self.move_h = (self.lb.height() - self.original_image_h) // 2
                    self.lb.start_x = self.lb.start_x + self.move_w
                    self.lb.start_y = self.lb.start_y + self.move_h
                    self.lb.end_x = self.lb.end_x + self.move_w
                    self.lb.end_y = self.lb.end_y + self.move_h

                    self.lb.image_width = self.lb.image_width + self.move_w
                    self.lb.image_height = self.lb.image_height + self.move_h
                    self.lb.upper_left_corner_limit_x = self.lb.upper_left_corner_limit_x + self.move_w
                    self.lb.upper_left_corner_limit_y = self.lb.upper_left_corner_limit_y + self.move_h

                    self.lb.update()
                    self.window_maximum_flag = True
                else:
                    pass
            else:
                # print(self.lb.width(),self.lb.height())
                if self.lb.width() == self.img.shape[1] and self.lb.height() == self.img.shape[0]:
                    print('self.lb.start_x', self.lb.start_x)
                    print('self.move_w', self.move_w)
                    print('self.move_h', self.move_h)
                    self.lb.start_x = self.lb.start_x - self.move_w
                    self.lb.start_y = self.lb.start_y - self.move_h
                    self.lb.end_x = self.lb.end_x - self.move_w
                    self.lb.end_y = self.lb.end_y - self.move_h
                    self.lb.image_width = self.lb.image_width - self.move_w
                    self.lb.image_height = self.lb.image_height - self.move_h
                    self.lb.upper_left_corner_limit_x = self.lb.upper_left_corner_limit_x - self.move_w
                    self.lb.upper_left_corner_limit_y = self.lb.upper_left_corner_limit_y - self.move_h
                    self.move_w = 0
                    self.move_h = 0
                    self.window_maximum_flag = False
                    self.lb.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            temp = min(self.lb.start_y, self.lb.end_y)
            if temp != self.lb.upper_left_corner_limit_y:
                self.lb.start_y = self.lb.start_y - 1
                self.lb.end_y = self.lb.end_y - 1
        elif event.key() == Qt.Key_Down:
            temp = max(self.lb.start_y, self.lb.end_y)
            if temp != self.lb.image_height:
                self.lb.start_y = self.lb.start_y + 1
                self.lb.end_y = self.lb.end_y + 1
        elif event.key() == Qt.Key_Left:
            temp = min(self.lb.start_x, self.lb.end_x)
            if temp != self.lb.upper_left_corner_limit_x:
                self.lb.start_x = self.lb.start_x - 1
                self.lb.end_x = self.lb.end_x - 1
        elif event.key() == Qt.Key_Right:
            temp = max(self.lb.start_x, self.lb.end_x)
            if temp != self.lb.image_width:
                self.lb.start_x = self.lb.start_x + 1
                self.lb.end_x = self.lb.end_x + 1

        self.lb.adjust_flag = True
        self.lb.update()
        print(event.key())
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            print(self.lb.start_x)
            if self.is_press_Enter_key is False:

                start_x, start_y = min(self.lb.start_x, self.lb.end_x), min(self.lb.start_y, self.lb.end_y)
                end_x, end_y = max(self.lb.start_x, self.lb.end_x), max(self.lb.start_y, self.lb.end_y)

                if self.window_maximum_flag is True:
                    print('self.move_w', self.move_w)
                    start_x = start_x - self.move_w
                    end_x = end_x - self.move_w
                    start_y = start_y - self.move_h
                    end_y = end_y - self.move_h


                print(start_y,end_y, start_x,end_x)
                self.img = np.array(self.img[start_y:end_y, start_x:end_x, :], dtype=np.uint8)
                height, width, channal = self.img.shape
                bytesPerLine = channal * width
                # print(self.img.shape)
                # print(self.img)
                QImg = QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888)
                # self.lb.setAlignment(Qt.AlignCenter)
                pixmap = QPixmap.fromImage(QImg)

                if self.lb is not None:
                    self.lb.is_entry_key = True

                    self.lb.setPixmap(pixmap)
                    # self.lb.setAlignment(Qt.AlignCenter)
                    self.mainlayout.addWidget(self.lb)
                    self.mainlayout.update()

                self.is_press_Enter_key = True

        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
