import uuid

import os
from flask import request, render_template, session
from flask_restful import Api, Resource, marshal_with, fields, marshal, reqparse
from sqlalchemy import or_
from werkzeug.datastructures import FileStorage

import settings
from models import *
from dao import *

api = Api()

def init_api(app):
    api.init_app(app)

class UserApi(Resource):
    def get(self):
        key = request.args.get('key')
        if key:
            result =  {'state': 'fail', 'msg': '查无数据'}
            qs = query(User).filter(or_(User.id == key,
                                        User.name == key,
                                        User.phone == key))
            if qs.count():
                result['state'] = 'ok'
                result['msg'] = '查询成功'
                result['data'] = qs.first().json
                return result

        # 从数据库中查询所有的用户
        users = queryAll(User)

        return {'state':'ok','data':[user.json for user in users]}

    def post(self):
        name = request.form.get('name')
        phone = request.form.get('phone')
        print(name,phone)

        user = User()
        user.name = name
        user.phone = phone

        add(user)

        return {'state':'ok',
                'msg':'添加用户成功'}

    def delete(self):
        id = request.args.get('id')  # id ->str
        # user = queryById(User,id) # 是否考虑 id 不存在的情况
        # delete(user)
        flag = deleteById(User,id)
        return {'state':'ok',
                'msg':'删除{}成功'.format(id)}

    def put(self):
        id = request.form.get('id')
        user = queryById(User, id)
        user.name = request.form.get('name')
        user.phone = request.form.get('phone')
        add(user)
        return {'state':'ok',
                'msg':user.name+'更新成功！'}

class ImageApi(Resource):
    img_fields = {'id':fields.Integer,
                  'name':fields.String,
                  'url':fields.String,
                  'size':fields.Integer(default=0)}
    get_out_fields = {
        'state':fields.String(default='ok'),
        'data':fields.Nested(img_fields),
        'size': fields.Integer(default=1)
    }

    # 输入的定制
    parser = reqparse.RequestParser()
    parser.add_argument('id',
                        type=int, # 参数类型
                        required=False, # 是否必必须要
                        help = '请提供id参数') # 必须的参数不存在是的错误提示

   # @marshal_with(get_out_fields)
    def get(self):
        id = request.args.get('id')
        if id:
           img =  query(Image).filter(Image.id == id).first()
           return img
        else:
            image = queryAll(Image)
            data = {'state':'ok',
                'data':image,
                'size':len(image)}
            # 向session中存入用户名
            session['login_name'] = 'disen'
        return marshal(data,self.get_out_fields)
    parser = reqparse.RequestParser()
    parser.add_argument('name',required=True,help='必须提供name')
    parser.add_argument('url', required=True, help='必须提供图片路径')

    def post(self):
        args = self.parser.parse_args()
        # 保存数据
        img = Image()
        img.name = args.get('name')
        img.url = args.get('url')
        add(img)
        return {'msg':'添加图片成功！'}



class MusicApi(Resource):

    # 创建request参数的解析器
    parser = reqparse.RequestParser()

    # 向参数解析器中添加请求参数说明
    parser.add_argument('key',dest = 'name',type=str,required=True,help='必须提供name搜素的关键字')
    parser.add_argument('id',type=int,required=True,help='请确定数值类型')
    parser.add_argument('tag',action = 'append',required=True,help='至少提供一个tag标签')
    parser.add_argument('session',location='cookies',help='不存在session')

    # 定制输出
    music_fields = {
        'id':fields.Integer,
        'name':fields.String,
        'singer':fields.String,
        'url':fields.String(attribute='mp3_url')
    }

    out_fields = {
        'state':fields.String(default='ok'),
        'msg':fields.String(default='查询成功'),
        'data':fields.Nested(music_fields)
    }
    @marshal_with(out_fields)
    def get(self):
        # 按名字搜素
        # 通过request参数解析器，开始解析请求参数
        #如果请求参数不能满足条件，则直接返回参数相关的help说明
        args = self.parser.parse_args()
        # 从 args 中读取name请求参数
        name = args.get('name')
        tag = args.get('tag')
        session = args.get('session')
        music = query(Music).filter(Music.name.like('%{}%'.format(name)))
        if music.count():
            return {'data':music.all()}
        print(session)
        return {'msg': '无{},标签{}'.format(name,tag)}

class UploadApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('img',type=FileStorage,
                        location = 'files',
                        required = True,
                        help = '必须提供一个名为img的File表单参数')
    def post(self):
        # 验证 请求参数是否满足条件
        args = self.parser.parse_args()

        # 保存上传的文件
        uFile:FileStorage = args.get('img')
        newFileName = str(uuid.uuid4()).replace('-','')
        newFileName += '.'+uFile.filename.split('.')[-1]
        uFile.save(os.path.join(settings.MEDIA_DIR,newFileName))

        return {'msg':'上传成功',
                'path':'/static/images/{}'.format(newFileName)}

# 将资源添加到api对象中，并声明uri
api.add_resource(UserApi,'/user/')
api.add_resource(ImageApi,'/images/')
api.add_resource(MusicApi,'/music/')
api.add_resource(UploadApi,'/upload/')