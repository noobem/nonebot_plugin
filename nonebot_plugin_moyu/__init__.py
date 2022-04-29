from nonebot import on_command, require, get_bot, get_driver
from nonebot.adapters.onebot.v11 import (
    Message,
)
from nonebot.log import logger
import requests
import httpx
import base64
from re import findall

moyu_helper = require("nonebot_plugin_apscheduler").scheduler



moyu = on_command("摸鱼")



def convert_b64(content) -> str:
    ba = str(base64.b64encode(content))
    pic = findall(r"\'([^\"]*)\'", ba)[0].replace("'", "")
    return pic


def down_pic(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    re = requests.get(url=url, headers=headers, timeout=120)
    if re.status_code == 200:
        logger.debug("成功获取图片")
        return re.content
    else:
        logger.error(f"获取图片失败: {re.status_code}")
        return re.status_code


def get_moyuimg():
    error = "error"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    req_url = "https://api.vvhan.com/api/moyu"
    try:
        res = httpx.post(req_url, headers=headers, timeout=120)
    except Exception as e:
        logger.warning(e)
        return error

    try:
        url = res.headers['location']
        img = down_pic(url)
        base64 = convert_b64(img)
        pic = ""
        if type(base64) == str:
            pic = "[CQ:image,file=base64://" + base64 + "]"
            return pic
    except Exception as e:
        logger.error("获取摸鱼图片时出错。", e)
        return error


@moyu.handle()
async def send_moyu():
    try:
         result = get_moyuimg()
    except Exception as e:
        await moyu.finish(f"{result}\n请稍后再试！！")
        raise e
    await moyu.send(message=Message(result))


group_list = get_driver().config.moyugroups if hasattr(get_driver().config, "moyugroups") else list()
try:
    for groupid in enumerate(group_list):
        logger.info(f"已加载摸鱼群列表：{groupid[0]}-{groupid[1]} \n")
except TypeError:
    logger.error("插件定时发送相关设置有误，请检查.env.*文件。")
    
# 早上摸鱼提醒
@moyu_helper.scheduled_job("cron", hour=9, minute=0)
async def time_for_moyu():
    bot = get_bot()
    try:
         result = get_moyuimg()
    except Exception as e:
        logger.error("获取摸鱼图片时出错。", e)
        raise e
    result = get_moyuimg()
    if result and len(group_list) > 0:
        for group_id in group_list:
            await bot.send_group_msg(group_id=int(group_id), message=result)
        
        logger.info(f"已群发摸鱼提醒")