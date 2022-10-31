import decimal
import os
import asyncio

import aiohttp
from aiohttp import web
import time, datetime
import json
from Util.db import *
import pandas as pd

# from Util.LogUtils import Log
# logger = Log().get_log()
from Util.logtool import logger


routes = web.RouteTableDef()

class RewriteJsonEncoder(json.JSONEncoder):
    """重写json类，为了解决datetime类型的数据无法被json格式化"""

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        elif hasattr(obj, 'isoformat'):
            # 处理日期类型
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

def json_dumps(obj):
    return json.dumps(obj, cls=RewriteJsonEncoder)


@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")


# 定义一个路由映射，接收网址参数，post方式
# 上传设备列表文件并插入到数据库中
@routes.post('/calmcar/uploadFile')
async def uploadfile(request):
    logger.info("uploadfile start!")
    reader = await request.multipart()
    field = await reader.next()
    assert field.name == 'name'
    name = await field.read(decode=True)
    file_type = name.decode('utf-8')
    logger.info(file_type)
    assert file_type == 'csv'

    field = await reader.next()
    assert field.name == 'oem'
    name = await field.read(decode=True)
    oem_id = name.decode('utf-8')
    logger.info(oem_id)

    field = await reader.next()
    assert field.name == 'batch'
    name = await field.read(decode=True)
    batch_id = name.decode('utf-8')
    logger.info(batch_id)

    field = await reader.next()
    assert field.name == 'filename'
    filename = field.filename
    logger.info(filename)

    size = 0
    with open(os.path.join('C:\\workspace\\test', filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    # user = await fetchone('select device_id from tb_device')
    #读取文件存到数据库
    csv_file = 'C:\\workspace\\test\\'+filename
    filedatas = pd.read_csv(csv_file, usecols=['DEVICE_ID'])
    listdata = filedatas['DEVICE_ID'].values.tolist()
    for data in listdata:
        params = (data, batch_id, oem_id)
        result = await execute('INSERT INTO tb_device(device_id, batch_id, oem_id) VALUES(%s, %s, %s)', params)
        if result:
            msg = {'error_code': 0, 'error_msg': 'ok'}
        else:
            msg = {'error_code': 20002, 'error_msg': 'Please try again if registration fails'}

    return web.json_response(data=msg, dumps=json_dumps)

    # return web.Response(text='{} sized of {} successfully stored'
    #                          ''.format(filename, size))

    # data = await request.json()
    # logger.info('请求post的信息data为: %s' % str(data))
    # name = data["name"]
    # try:
    #     return web.json_response({'code': 0, 'data': name})
    # except Exception as e:
    #     return web.json_response({'msg': e.value}, status=500)
# 查询指定时间段内激活设备列表
@routes.post('/calmcar/queryActivateList')
async def query_activate_list(request):
    logger.info("query_activate_list start!")
    data = await request.json()
    star_time = data["star_time"]
    end_time = data["end_time"]
    # print("time {} {} {}".format(star_time, end_time, type(end_time)))
    try:
        result = await select('select * from tb_device where active_time between %s and %s', (star_time, end_time,))
        result_data = {'error_code': 0, 'error_msg': 'ok', 'data': result}
    except Exception as e:
        result_data = {'error_code': e.value, 'error_msg': 'failed'}
    return web.json_response(result_data, dumps=json_dumps)

# 激活指定设备并返回激活码
@routes.post('/calmcar/activateDevice')
async def activate_device(request):
    logger.info("activate_device start!")
    req_data = await request.json()
    # 1.先查询设备是否存在
    result = await fetchone('select device_id from tb_device where device_id =  %s', (req_data["device_id"], ))
    if not bool(result):
        result_data = {'error_code': 20003, 'error_msg': 'Device_id does not exists'}
        return web.json_response(result_data, dumps=json_dumps)

    if req_data["device_id"] != result.get("device_id"):
        result_data = {'error_code': 20004, 'error_msg': 'Device_id mismatch'}
        return web.json_response(result_data, dumps=json_dumps)

    # 调用激活接口激活
    str_activate = ""
    async with aiohttp.ClientSession('http://81.70.250.220:8010') as session:
        body = {
            "deviceId": req_data["device_id"],
            "secretId": "s6iXh7SXSKiX8OYrfzzOVQ==",
            "secretKey": "tq6JeYZeRknJXnm6eMu1+Gr7eNdToDZwsOB8NexHc0c="
        }
        async with session.post('/v1/auth/device', json=body) as resp:
            res = await resp.json()
            logger.debug(res)
            if res['code'] == 0:
                str_activate = res['data']
            else:
                result_data = {'error_code': 20005, 'error_msg': 'Device_id active failed!'}
                return web.json_response(result_data, dumps=json_dumps)

    # 更新数据库
    try:
        result = await execute('update tb_device set active_time = CURRENT_TIMESTAMP , active_code = %s where device_id = %s', (str_activate, req_data["device_id"],))
        result_data = {'error_code': 0, 'error_msg': 'ok', 'activate_code': str_activate}
    except Exception as e:
        result_data = {'error_code': e.value, 'error_msg': 'failed'}
    return web.json_response(result_data, dumps=json_dumps)


async def init():
    mysql_pool = await create_pool()

    async def dispose_mysql_pool():
        mysql_pool.close()
        await mysql_pool.wait_closed()

    async def dispose_pool(app):
        await dispose_mysql_pool()

    app = web.Application()
    app.add_routes(routes)
    app.on_cleanup.append(dispose_pool)
    return app

if __name__ == '__main__':
    logger.info('http server begin work!')

    # loop = asyncio.get_event_loop()
    app = init()
    logger.info('Server started at http://127.0.0.1:8000...')
    web.run_app(app, host='127.0.0.1', port=8000)
    logger.info('Server stoped at http://127.0.0.1:8000...')
