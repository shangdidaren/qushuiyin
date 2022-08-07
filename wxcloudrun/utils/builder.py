import pathlib
import re
import subprocess

path = '../video_spider/src/video_spider.php'

HandleDict = {'pipix': 'pipixia', 'douyin': 'douyin', 'huoshan': 'huoshan', 'h5.weishi': 'weishi',
              'isee.weishi': 'weishi', 'weibo.com': 'weibo', 'oasis.weibo': 'lvzhou', 'zuiyou': 'zuiyou',
              'xiaochuankeji': 'zuiyou', 'bbq.bilibili': 'bbq', 'kuaishou': 'kuaishou', 'quanmin': 'quanmin',
              'moviebase': 'quanmin', 'hanyuhl': 'basai', 'eyepetizer': 'before', 'immomo': 'kaiyan',
              'vuevideo': 'momo', 'xiaokaxiu': 'vuevlog', 'ippzone': 'xiaokaxiu', 'pipigx': 'pipigaoxiao',
              'qq.com': 'quanminkge', 'ixigua.com': 'xigua', 'doupai': 'doupai', '6.cn': 'sixroom',
              'huya.com/play/': 'huya', 'pearvideo.com': 'pear', 'xinpianchang.com': 'xinpianchang',
              'acfun.cn': 'acfan', 'meipai.com': 'meipai'}


class Builder:
    cmd = 'php -f %s %s "%s"'
    handle_dict = HandleDict

    def get_work(self, url):
        method = self.get_method(url)

        if not method:
            return None

        cmd = self.cmd % (path, method, url)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        res = proc.stdout.read()
        if res:
            return res.decode()

    def get_method(self, url: str):
        self.handle_dict = self.refresh_dict()

        for comp, method in self.handle_dict.items():
            if url.find(comp) != -1:
                return method

    @staticmethod
    def refresh_dict():
        # git checkout . 将没有add 的代码回滚
        with open('../video_spider/index.php', 'r', encoding='utf-8') as f:
            data = f.read()
            x = re.findall(r".*?strpos.*?\'(.+?)\'", data)
            y = re.findall(r".*?->(.*?)\(\$.+?\);", data)
            if len(x) == len(y):
                return dict(zip(x, y))
            else:
                return HandleDict
