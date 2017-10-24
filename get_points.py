import cv2
import numpy as np

title = "Image"
im = cv2.namedWindow(title)
cv2.moveWindow(title, 1000, 200)
im = cv2.imread("1.png")


mouse_params = {'tl_list':[], 'br_list':[], 'tl': None, 'br': None, 'current_pos': None, 'released_once': False}

def onMouse(event, x, y, flags, param):
    param['current_pos'] = (x, y)

    if param['tl'] is None and param['br'] is None:
        if param['tl_list'] == []:
            pass
        else:
            if flags & cv2.EVENT_FLAG_RBUTTON:
                param['tl_list'].pop()
                param['br_list'].pop()

    if param['tl'] is not None and (flags & cv2.EVENT_FLAG_RBUTTON):
        param['tl'] = None
        param['br'] = None
        param['released_once'] = False

    if param['tl'] is not None and not (flags & cv2.EVENT_FLAG_LBUTTON):
        param['released_once'] = True

    if flags & cv2.EVENT_FLAG_LBUTTON:
        if param['tl'] is None:
            param['tl'] = param['current_pos']
            # param['temp_tl'] = param['tl']
        elif param['released_once']:
            param['br'] = param['current_pos']
            param['tl_list'].append(param['tl'])
            param['br_list'].append(param['br'])

cv2.setMouseCallback(title, onMouse, mouse_params)
cv2.imshow(title, im)

while True:
    im_draw = np.copy(im)
    for x,y in zip(mouse_params['tl_list'],mouse_params['br_list']):
        cv2.rectangle(im_draw, x, y, (0,0,255))
    if mouse_params['tl'] is not None:
        cv2.rectangle(im_draw, mouse_params['tl'],mouse_params['current_pos'], (0, 0, 255))
    if mouse_params['br'] is not None:
        mouse_params['tl'] = None
        mouse_params['br'] = None
        mouse_params['released_once'] = False
    cv2.imshow(title, im_draw)
    _ = cv2.waitKey(1)
    if _ == 27:
        break
