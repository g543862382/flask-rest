from flask_sqlalchemy import SQLAlchemy, BaseQuery

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def query(cls) -> BaseQuery: # 通过 -> 声明函数返回的类型
    return db.session.query(cls)

def queryAll(cls):
    return query(cls).all()

def queryById(cls,id):  # 根据id 查找 数据
    return query(cls).get(int(id))

def add(obj):
    db.session.add(obj)
    db.session.commit()

def delete(obj):
    db.session.delete(obj)
    db.session.commit()

def deleteById(cls,id,attrName):
    try:
        obj = queryById(cls,id)
        delete(obj)
        return True
    except:
        pass
    return False
