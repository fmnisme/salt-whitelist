#coding:utf-8
"""
白名单系统

只检查在check_fun_map中的fun,如果fun的arg不符合pillar_whitelist中的规则,则屏蔽.
"""
import re


def check(data,pillar):
    # 如果没有对应的check_fun,则不检查
    if not data['fun'] in check_fun_map:
        return

    check_fun = check_fun_map[data['fun']]
    #如果命令对应的白名单为空,则屏蔽命令. 如果管理员没有配置白名单,或者白名单配置了但有错误没生效,都会拒绝执行命令.
    pillar_whitelist = get_pillar_whitelist(data,pillar)
    if not check_fun(data,pillar_whitelist):
       return "'%s' is not in whitelist. arg: %s" % (data['fun'],str(data['arg']))


def get_pillar_whitelist(data,pillar):
    """
    返回匹配到的第一个pillar whitelist
    :param data:
    :param pillar:
    :return:
    """
    fun = data['fun']
    patterns = pillar.get('whitelist',{}).keys()
    #pattern: "cmd.run.*"
    for pattern in patterns:
        matchs = re.findall(pattern,fun)
        if matchs and len(matchs) == 1:
            return pillar.get('whitelist',{}).get(pattern)


class CheckCmd(object):
    def extract_args_and_kwargs(self,data):
        """
        将data['arg']中的arg与kwarg提取出来
        :param data:
        :return:
        """
        kwargs = {}
        args = []
        for x in data['arg']:
            if isinstance(x,dict):
                if x.has_key('__kwarg__') and x['__kwarg__'] == True:
                    kwargs = x
            else:
                args.append(x)
        return args,kwargs

    def get_cmd(self,data):
        """获取要执行的命令
        :return:
        """
        args,kwargs = self.extract_args_and_kwargs(data)

        if args:
            cmd = args[0]
        else:
            cmd = kwargs.get('cmd')
        return cmd

    def check(self,data,whitelist):
        """
        :param data:
        :return:

        样例
        data = {
            'tgt_type': 'glob',
            'jid': '20151210161230602642',
            'tgt': '*39*',
            'ret': '',
            'user': 'root',
            'arg': ['echo 123', {'pwd': '/tmp', '__kwarg__': True}],
            'fun': 'cmd.run'
        }
        """
        if not whitelist:
            whitelist = []

        cmd = self.get_cmd(data)
        #没有命令则不检查
        if not cmd:
            return True

        for pattern in whitelist:
            matchs = re.findall(pattern,cmd)
            if matchs:
                return True
        return False

    def __call__(self, data,whitelist):
        return self.check(data,whitelist)


class CheckCmdChroot(CheckCmd):
    """
    cmd.run_chroot(root,cmd,...)
    """
    def get_cmd(self,data):
        """
        第二个参数是cmd
        :param data:
        :return:
        """
        args,kwargs = self.extract_args_and_kwargs(data)

        if len(args) > 1:
            cmd = args[1]
        else:
            cmd = kwargs.get('cmd')
        return cmd


check_fun_map = {
    'cmd.run' : CheckCmd(),
    'cmd.run_all' : CheckCmd(),
    'cmd.run_stderr' : CheckCmd(),
    'cmd.run_stdout' : CheckCmd(),
    'cmd.run_chroot' : CheckCmdChroot(),
}
