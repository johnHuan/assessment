# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 11:21
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : app.py
from flask import Flask, render_template

from api.apiFire import fire_bp
from api.apiSan import san_bp
from api.apiValFire import valFire_bp
from api.apiValSan import valSan_bp
from commons.preHandler import pre_handler, pre_gdf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

from flask_socketio import SocketIO

socketio = SocketIO(app)
import sys  # reload()之前必须要引入模块

reload(sys)
sys.setdefaultencoding('utf-8')

async_mode = None
thread = None
from threading import Lock

thread_lock = Lock()

# 注册蓝图
app.register_blueprint(fire_bp)
app.register_blueprint(san_bp)
app.register_blueprint(valFire_bp)
app.register_blueprint(valSan_bp)


@app.template_filter("get_action")
def get_action(x):
    y = str(x).split('/')
    if len(y[-1]) == 0:
        return 'fire_index'
    return y[-1]


@app.route('/')
def empty():
    # 1.1 默认缺省方法 直接定向到 消防设施分布图
    pre_handler()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 消防设施分布图"
    }
    return render_template('/1/item_index.html', **kwargs)


if __name__ == "__main__":
    flag = 'planning'
    pre_gdf(flag)
    socketio.run(app, host='127.0.0.1', debug=True, port=5000)
