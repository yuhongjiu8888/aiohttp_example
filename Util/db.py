# import logging
# logging.basicConfig(level=logging.INFO)
from Util.logtool import logger

import aiomysql
from conf.settings import DATABASES

def log(sql, args=()):
    logger.info('SQL: %s' % sql, *args)

async def create_pool( **kw):
    """定义mysql全局链接池"""
    logger.info('create database connection pool...')
    global _mysql_pool
    try:
        _mysql_pool = await aiomysql.create_pool(host=DATABASES['host'], port=DATABASES['port'], user=DATABASES['user'],
                                      password=DATABASES['password'], db=DATABASES['db'], loop=None,
                                      charset=kw.get('charset', 'utf8'), autocommit=kw.get('autocommit', True),
                                      maxsize=kw.get('maxsize', 10), minsize=kw.get('minsize', 1))
        logger.info('create database connection success...')
        return _mysql_pool
    except:
            logger.info('connect error.', exc_info=True)

async def fetchone(sql, args=(), size=None):
    """封装select，查询单个，返回数据为字典"""
    log(sql, args)
    async with _mysql_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, args)
            rs = await cur.fetchone()
            return rs

async def select(sql, args=(), size=None):
    """封装select，查询多个，返回数据为列表"""
    log(sql, args)
    async with _mysql_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, args)
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
            logger.info('rows returned: %s' % len(rs))
            return rs

async def execute(sql, args=()):
    """封装insert, delete, update"""
    log(sql, args)
    async with _mysql_pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(sql, args)
            except BaseException:
                await conn.rollback()
                return
            else:
                affected = cur.rowcount
                return affected


