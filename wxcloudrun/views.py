import json
import re
import sys
import time
import urllib
from datetime import datetime
import requests
from flask import render_template, request, jsonify
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters, ParseUrl
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
from wxcloudrun import db
from wxcloudrun.dao import logger


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


# code = 0 成功 , msg = ''
# code = 1 错误 , msg = '错误信息'
# code = 2 异常 , msg = ''

@app.route('/api/insert_url', methods=['POST'])
def insert_url():
    """
    插入一条可用的url
        {
            "token": true,
            "url": "https://tenapi.cn/video",
            "arg": "url",
            "method": "GET",
            "video": "url",
            "music": "music",
            "title": "url",
            "cover": "cover",
            "code": "code",
            "error_code": "201",
            "count": 10
        }
        {
            "token": true,
            "url": "http://apps.ourwechat.com/dynowater/api.php",
            "arg": "url",
            "method": "POST",
            "video": "video_url",
            "music": "mp3",
            "title": "intro",
            "cover": "dynamic_url",
            "code": "code",
            "error_code": "404",
            "count": 10
        }
        {
            "token": true,
            "url": "https://api.missuo.me/douyin",
            "arg": "url",
            "method": "GET",
            "video": "mp4",
            "music": "mp3",
            "title": "desc",
            "cover": "id",
            "code": "code",
            "error_code": "404",
            "count": 10
        }
    :return:
    """
    param = request.get_json()
    method = param.get('method')
    new_uri = param.get('url')
    arg = param.get('arg')

    video = param.get('video')
    music = param.get('music')
    title = param.get('title')
    cover = param.get('cover')
    code = param.get('code')
    error_code = param.get('error_code')

    weight = param.get('count')
    token = param.get('token', False)
    if not all([new_uri, arg, video, code, error_code, token]):
        return jsonify({"code": 1, 'msg': "err"})

    exist_url_obj = ParseUrl.query.filter_by(url=new_uri).first()
    if exist_url_obj:
        if exist_url_obj.active:
            return jsonify({"code": 2, "msg": "正在使用中"})
        else:
            exist_url_obj.active = True
            exist_url_obj.count = weight if weight else exist_url_obj.count
            exist_url_obj.arg = arg if arg else exist_url_obj.arg
            exist_url_obj.video = video if video else exist_url_obj.video
            exist_url_obj.music = music if music else exist_url_obj.music
            exist_url_obj.title = title if title else exist_url_obj.title
            exist_url_obj.cover = cover if cover else exist_url_obj.cover
            exist_url_obj.code = code if code else exist_url_obj.code
            exist_url_obj.error_code = error_code if error_code else exist_url_obj.error_code
            exist_url_obj.method = method if method else exist_url_obj.method
            db.session.commit()
            return jsonify({"code": 2, "msg": "已激活"})
    else:
        # 不存在则添加, 不过应该要校验一下
        url_obj = ParseUrl(
            count=weight or 0,
            url=new_uri,
            arg=arg or 'url',
            video=video or 'url',
            music=music or 'music',
            title=title or 'title',
            cover=cover or 'cover',
            code=code or 'code',
            error_code=error_code or '404',
            method=method or 'GET',
        )
        db.session.add(url_obj)
        db.session.commit()
        return jsonify({"code": 0, 'msg': "已添加"})


Headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


def get_result(url: ParseUrl, meta):
    try:
        ret = {}

        start_time = time.perf_counter()
        data = {url.arg: meta}
        if url.method.lower() == 'get':
            res = requests.get(url.url, data, headers=Headers)
        else:
            res = requests.post(url.url, data, headers=Headers)

        end_time = time.perf_counter()
        res = res.json()
        if res.get(url.code) == url.error_code:
            logger.warning(f'get {meta} from {url.url} failed!')
            return False, {'delay': end_time - start_time, 'msg': '获取失败'}

        ret['delay'] = end_time - start_time
        ret['video'] = res.get(url.video)
        ret['music'] = res.get(url.music)
        ret['title'] = res.get(url.title)
        ret['cover'] = res.get(url.cover)
        ret['code'] = 0

        return True, ret
    except Exception as e:
        logger.error(f'{time.asctime()}: get source from {url.url} failed!')
        return False, str(e)


# code = 0 成功 , msg = ''
# code = 1 错误 , msg = '错误信息'

@app.route('/api/execute', methods=['POST'])
def execute_action():
    """
    :return: 去水印后的结构体, 包含作者昵称,头像地址,时间标题,封面,视频url.
    """
    param = request.get_json()  # type: dict
    meta_url = param.get("meta_url")

    url_list = re.findall(r"(http[s]{0,1}://[^\s]+)", meta_url)
    url = url_list[0] if url_list else meta_url
    parse_urls = ParseUrl.query \
        .order_by(ParseUrl.delay, db.desc(ParseUrl.count)) \
        .filter_by(active=True) \
        .limit(3) \
        .all()
    if not parse_urls:
        parse_urls = ParseUrl.query \
            .order_by(ParseUrl.delay, db.desc(ParseUrl.count)) \
            .limit(3) \
            .all()

    for parse_url_obj in parse_urls:
        ok, res = get_result(parse_url_obj, url)
        if ok:
            # 增加权重, 刷新delay, 返回结果
            parse_url_obj.active = True
            parse_url_obj.delay = res.get('delay')
            parse_url_obj.count += 1
            db.session.commit()
            logger.info(f"{parse_url_obj.url} success response returned!")
            return jsonify(res)
        else:
            parse_url_obj.count //= 2
            if parse_url_obj.count <= 0:
                parse_url_obj.active = False

            if isinstance(res, dict):
                parse_url_obj.delay = float(res.get('delay'))
            else:
                logger.warning(f'{sys._getframe().f_code.co_name} with exc: {res}')
                db.session.commit()
            continue
    else:
        # 没有找到合适的, 再来一次请求吧!
        return jsonify({"code": 1, 'msg': '服务器出小差了'})
