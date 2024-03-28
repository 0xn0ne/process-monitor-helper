#!/bin/python3
# _*_ coding:utf-8 _*_
#
# process-monitor-helper.py
# Process Monitor 记录文件解析助手
# 下载地址：https://learn.microsoft.com/en-us/sysinternals/downloads/procmon
# TODO:优化相似数据输出

import copy
import json
import pathlib
import re
from typing import List, Union

import pandas


class Helper:
    def __init__(self, logs_path: List[pathlib.Path], rule_path: pathlib.Path):
        self.log_pid = []
        if not isinstance(logs_path, List):
            logs_path = [logs_path]
        self.dataframe = None
        for index, l_path in enumerate(logs_path):
            if index == 0:
                self.dataframe = pandas.read_csv(l_path)
                continue
            pandas.concat([self.dataframe, pandas.read_csv(l_path)], axis=0, ignore_index=True)
        if not isinstance(self.dataframe, pandas.DataFrame) or not len(self.dataframe):
            raise ValueError('未找到 CSV 文件或 CSV 文件无数据，当前文件列表：{}'.format(logs_path))
        self.dataframe.loc[:, 'Remark'] = 'NO.DATA'
        self.dataframe.fillna('NO.DATA', inplace=True)
        self.dataframe.reset_index(drop=True)
        self.rules = json.loads(rule_path.read_bytes())
        if not self.rules:
            raise ValueError('未找到规则文件或规则文件无数据，当前文件：{}'.format(rule_path))

    def trace_process(self, process_name_or_id: Union[str, int]):
        """
        跟踪目标进程

        :param name_or_id:
        :param _level:
        :return:
        """
        pname = ''
        pid = 0
        ret = pandas.DataFrame(columns=self.dataframe.columns.values)
        pname_list = self.dataframe[(self.dataframe['Process Name'] == process_name_or_id)]
        pid_list = self.dataframe[(self.dataframe['PID'] == process_name_or_id)]
        if isinstance(process_name_or_id, str) and not pname_list.empty:
            pname = process_name_or_id
            pid = int(pname_list.iloc[0]['PID'])
        elif isinstance(process_name_or_id, int) and not pid_list.empty:
            pid = process_name_or_id
            pname = pid_list.iloc[0]['Process Name']
        else:
            return ret
        # if pid in self.log_pid:
        #     return ret
        # self.log_pid.append(pid)
        df_proc = self.dataframe[self.dataframe['Process Name'] == pname]

        for f_name in self.rules:
            if isinstance(self.rules[f_name], str):
                filter = {'expr': self.rules[f_name]}
            else:
                filter = self.rules[f_name]
            df_query_result = df_proc.query(**filter)
            df_query_result.loc[:, 'Remark'] = f_name
            ret = pandas.concat([ret, df_query_result])
            if 'Process Create' not in filter['expr']:
                continue
            for _, row in df_query_result.iterrows():
                d_row = row.to_dict()
                r_pid = re.search('PID:\s*(\d+)', d_row['Detail'])
                if not r_pid:
                    print('[E] 无法找到PID,', d_row)
                ret = pandas.concat([ret, self.trace_process(int(r_pid.group(1)))])

        if not len(ret):
            print('未找到程序名 {}，进程编号 {} 的数据'.format(pname, pid))

        ret.sort_index(inplace=True)
        ret.drop_duplicates(inplace=True)
        return ret

    def print_pretty(self, process_dataframe: pandas.DataFrame):
        df_proc = copy.deepcopy(process_dataframe)
        frist_pid = df_proc.iloc[0,]['PID']

        def _recurse(curr_proc_id: int, level: int = 0):
            index = 0
            for _, row in df_proc.iterrows():
                if row['PID'] != curr_proc_id:
                    continue
                if row['Operation'] == 'Process Create':
                    r_pid = re.search('PID:\s*(\d+)', row['Detail'])
                    if not r_pid:
                        print('[E] 无法找到PID,', row)

                    _recurse(int(r_pid.group(1)), level + 1)
                prefix = '  ' * level
                # if index < 1 and row['PID'] == frist_pid:
                #     prefix += '-'
                if index == 0:
                    prefix += '>'
                else:
                    prefix += '|'
                # detail 长度缩减
                detail = re.sub(r'\s', '', row['Detail'])
                file_path = re.sub(r'DESKTOP[^:]+', 'localhost', row['Path'], flags=re.I)
                if len(detail) > 50:
                    detail = detail[:23] + '....' + detail[-23:]
                if len(file_path) > 50:
                    file_path = file_path[:23] + '....' + file_path[-23:]
                print(
                    '{} {},{}; {}; {}; {}'.format(
                        prefix, row['PID'], row['Process Name'], row['Remark'], file_path, detail
                    )
                )
                index += 1

        _recurse(frist_pid)


if __name__ == '__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
    ██████╗ ███╗   ███╗██╗  ██╗
    ██╔══██╗████╗ ████║██║  ██║
    ██████╔╝██╔████╔██║███████║
    ██╔═══╝ ██║╚██╔╝██║██╔══██║
    ██║     ██║ ╚═╝ ██║██║  ██║
    ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝
    v0.1.1
    by 0xn0ne, https://github.com/0xn0ne/process-monitor-helper
''',
    )
    # trace the target program name, can trace multiple (eg. hello.exe).
    parser.add_argument(
        '-p',
        '--process-name',
        required=True,
        nargs='+',
        help='跟踪目标程序名称，可跟踪多个（如：hello.exe）',
    )
    # search for the CSV file or folder path that ProcessMonitor exports (eg. ~/download/Logfile.CSV).
    parser.add_argument(
        '-l',
        '--logs-path',
        default=['cache'],
        nargs='+',
        help='搜索 ProcessMonitor 导出的 CSV 记录文件或文件夹路径，默认：cache；（如：~/download/Logfile.CSV）。',
    )
    # path to the json rule file. default: rules.json
    parser.add_argument(
        '-c',
        '--rule-path',
        default='rules.json',
        help='Json 规则文件的路径，默认：rules.json',
    )
    args = parser.parse_args()

    print(parser.description)

    # 本来打算做成每次允许根据 rule 更新参数的方式，算了先留着用来初始化参数
    nargs = dict(args.__dict__)
    for key in args.__dict__:
        if nargs[key] is None:
            del nargs[key]
    t_logs_path = nargs['logs_path']
    nargs['logs_path'] = []
    for it in t_logs_path:
        path = pathlib.Path(it)
        if path.is_file():
            nargs['logs_path'].append(path)
            continue
        for filepath in path.rglob('*'):
            if filepath.suffix.lower() != '.csv':
                continue
            nargs['logs_path'].append(filepath)
    nargs['rule_path'] = pathlib.Path(nargs['rule_path'])

    hel = Helper(nargs['logs_path'], nargs['rule_path'])
    for pname in nargs['process_name']:
        ret = hel.trace_process(pname)
        hel.print_pretty(ret)
        ret.to_csv('output_{}_{}.csv'.format(pname, time.strftime("%y%m%d%H%M%S", time.localtime())), encoding='utf-8')
