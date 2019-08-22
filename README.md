# webanalyzer

[![PyPI](https://img.shields.io/pypi/v/webanalyzer.svg)](https://pypi.python.org/pypi/webanalyzer)


## 安装

```sh
pip install -U webanalyzer
```

## 使用

### 命令行

第一次运行程序必须先下载指纹规则
``` sh
[*] webanalyzer --update -d /path/to/rules
```

也可以使用 git 自行下载规则
``` sh
[*] git clone https://github.com/webanalyzer/rules.git /path/to/rules
```

使用方法:

``` sh
[*] webanalyzer --help
Usage: webanalyzer [OPTIONS]

Options:
  -u, --url TEXT                  Target  [required]
  -d, --directory TEXT            Rules directory, default ./rules
  -a, --aggression INTEGER RANGE  Aggression mode, default 0
  -U, --user-agent TEXT           Custom user agent
  -H, --header TEXT               Pass custom header LINE to serve
  -v, --verbose INTEGER RANGE     Verbose level, default 2
  -r, --rule TEXT                 Specify rule
  --disallow-redirect             Disallow redirect
  --list-rules                    List rules
  --update                        Update rules
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

例子:

```sh
[*] webanalyzer -u "http://blog.fatezero.org" -d path/to/rules
[
    {
        "name": "Fastly",
        "origin": "wappalyzer"
    },
    {
        "name": "Hexo",
        "origin": "wappalyzer",
        "version": "3.8.0"
    },
    {
        "name": "Varnish",
        "origin": "wappalyzer"
    },
    {
        "name": "GitHub Pages",
        "origin": "wappalyzer"
    },
    {
        "name": "Ruby on Rails",
        "origin": "implies"
    },
    {
        "name": "Ruby",
        "origin": "implies"
    }
]
```

使用路径指定某个 rule
``` sh
[*] webanalyzer -u "http://blog.fatezero.org" -p /path/to/hexo.json
{
    "name": "Hexo",
    "origin": "test",
    "version": "3.8.0"
}
```

### 类库

作为类库使用

``` python
import webanalyzer

# 初始化
w = webanalyzer.WebAnalyzer()

# 设置自定义 headers
w.headers = {
    "User-Agent": "custom ua",
    "header-key": "header-value"
}

# 是否允许跳转
w.allow_redirect = True

# aggression 模式级别
w.aggression = 0

# 设置 requests timeout 时间
w.timeout = 30

# 设置 rules 路径
w.rule_dir = "rules"

# 下载或更新某个路径下的 rules
if w.update_rules():
    print("update rules successful")

# 重新加载 rules
n = w.reload_rules()
print("reload %d rules" % n)

# 获取所有 rules
r = w.list_rules()
print("list %d rules" % n)

# 使用某个 rule 进行检测
r = w.test_rule("http://blog.fatezero.org", "rules/wappalyzer/hexo.json")
print(r)

# 使用所有 rules 进行检测，默认会重新 reload rules
r = w.start("http://blog.fatezero.org", reload=False)
print(r)
```

## Q & A

* 和 WhatWeb、Wappalyzer 的区别？

WhatWeb 的规则使用 ruby 编写，在规则方面，其他编程语言很难复用，也只能通过子进程的方式调用 WhatWeb。
Wappalyzer 更多的作为一个浏览器插件使用。

* 为什么只支持 Python3.6 以及以上的 Python 版本？

因为有些正则规则使用了 `(?-flag:...)` 这样的写法，然而在
[https://docs.python.org/3/whatsnew/3.6.html#re](https://docs.python.org/3/whatsnew/3.6.html#re)
才开始支持。

## 引用

* [rules](https://github.com/webanalyzer/rules)
* [webanalyzer.go](https://github.com/webanalyzer/webanalyzer.go)
