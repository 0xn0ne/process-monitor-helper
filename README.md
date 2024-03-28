# Pocess Monitor Helper

Process Monitor（ProcMon）常用于程序行为分析，但是 ProcMon 的输出数据太多，虽然可以通过过滤器筛选，但还是仍会存在噪点数据输出扰乱。整个 CSV 格式记录分析助手，只需要运行 ProcMon 等待一段时间保存 CSV 格式事件即可，程序会根据解析规则提取重点数据，并将提取后的数据输出到 CSV 格式的文件中并打印出来。

Process Monitor (ProcMon) is often used for program behavior analysis, but the output data of ProcMon is too much, although it can be filtered by filters, but there will still be noisy data output disturbance. For the whole CSV format log analysis assistant, you just need to run ProcMon and wait for some time to save the CSV format events, the program will extract the key data according to the parsing rules, and output the extracted data to a CSV format file and print it out.

## 快速开始

### 依赖

+ python >= 3.6
+ Process Monitor: <https://learn.microsoft.com/en-us/sysinternals/downloads/procmon>

进入项目目录，使用以下命令安装依赖库

```bash
pip3 install pandas
```

或者使用 PIP 的 requirement 参数安装依赖库

```bash
pip3 install -r requirements.txt
```

## 使用方法

### Process Monitor 的使用

1. 准备好需要分析的恶意文件；
2. 下载 Process Monitor；
3. 在虚拟机中运行 Process Monitor；
4. 等待 30~120s；
5. 用 CSV 格式保存 Process Monitor 的事件记录；
6. 使用 process-monitor-helper.py 帮忙分析。

### 使用帮助

```bash
optional arguments:
  -h, --help            show this help message and exit
  -p PROCESS_NAME [PROCESS_NAME ...], --process-name PROCESS_NAME [PROCESS_NAME ...]
                        跟踪目标程序名称，可跟踪多个（如：hello.exe）
  -l LOGS_PATH [LOGS_PATH ...], --logs-path LOGS_PATH [LOGS_PATH ...]
                        搜索 ProcessMonitor 导出的 CSV 记录文件或文件夹路径，默认：cache；（如：~/download/Logfile.CSV）。
  -c RULE_PATH, --rule-path RULE_PATH
                        Json 规则文件的路径，默认：rules.json
```

### 输出样例

```bash
% python3 process-monitor-helper.py -p a.exe

    ██████╗ ███╗   ███╗██╗  ██╗
    ██╔══██╗████╗ ████║██║  ██║
    ██████╔╝██╔████╔██║███████║
    ██╔═══╝ ██║╚██╔╝██║██╔══██║
    ██║     ██║ ╚═╝ ██║██║  ██║
    ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝
    v0.1.1
    by 0xn0ne, https://github.com/0xn0ne/process-monitor-helper

> 4716,a.exe; 进程启动; NAN.DATA; ParentPID:696,Commandli....osoft;windir=C:\Windows
| 4716,a.exe; 目录扫描; C:\Windows\System32\winhttp.dll; DesiredAccess:ReadData/....e:n/a,OpenResult:Opened
......
| 4716,a.exe; 目录扫描; C:\Windows\System32\uxtheme.dll; DesiredAccess:ReadData/....e:n/a,OpenResult:Opened
| 4716,a.exe; 目录扫描; C:\Users\microsoft\AppD....4e4b-A14B-C5D08F1BA73A}; DesiredAccess:ReadData/....ze:0,OpenResult:Created
| 4716,a.exe; 网络数据接收; localhost:49815 -> 8.138.18.29:http; Length:0,seqnum:0,connid:0
```
