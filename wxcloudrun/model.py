from datetime import datetime

from wxcloudrun import db


# 计数表
class Counters(db.Model):
    # 设置结构体表格名称
    __tablename__ = "Counters"

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    created_at = db.Column(
        "createdAt", db.TIMESTAMP, nullable=False, default=datetime.now()
    )
    updated_at = db.Column(
        "updatedAt", db.TIMESTAMP, nullable=False, default=datetime.now()
    )


# 解析链接
class ParseUrl(db.Model):
    """
    orderby delay,-count, 拿3条进行比较, 如果失败, 刷新数据, 返回 "服务器出小差了"
    """

    # 表名称
    __tablename__ = "ParseUrls"

    # 表字段
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column('次数', db.Integer, default=10)  # 成功+1 失败//2
    url = db.Column('serverUrl', db.String(200), unique=True)
    arg = db.Column('参数名', db.String(10), default='url')
    method = db.Column('请求方式', db.String(10))
    active = db.Column('启用', db.Boolean, default=True)
    delay = db.Column('延迟', db.Float, default=0)
    video = db.Column('源视频参数', db.String(1024))
    music = db.Column('bgm参数', db.String(1024))
    title = db.Column('标题', db.String(1024))
    cover = db.Column('封面', db.String(1024))
    code = db.Column('code', db.String(10))
    error_code = db.Column('error', db.String(10))
