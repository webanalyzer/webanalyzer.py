# webanalyzer

[![PyPI](https://img.shields.io/pypi/v/webanalyzer.svg)](https://pypi.python.org/pypi/webanalyzer)


## 安装

```sh
pip install -U webanalyzer
```

## 使用

### 命令行


使用方法:

```sh
[*] webanalyzer --help
Usage: webanalyzer [OPTIONS]

Options:
  -u, --url TEXT                  Target  [required]
  -a, --aggression INTEGER RANGE  Aggression mode, 1 enable custom plugins
                                  aggression mode, 2 enable all plugins
                                  aggression mode
  -U, --user-agent TEXT           Custom user agent
  -H, --header TEXT               Pass custom header LINE to serve
  -r, --disallow-redirect         Disallow redirect
  -l, --list-plugins              List the plugins
  -v, --verbose INTEGER RANGE     Verbose level
  -p, --plugin TEXT               Specify plugin
  --help                          Show this message and exit.
```

例子:

```sh
[*] webanalyzer -u "http://blog.fatezero.org"
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

使用名字指定 plugin
``` sh
[*] webanalyzer -u "http://blog.fatezero.org" -p hexo
{
    "name": "Hexo",
    "origin": "test",
    "version": "3.8.0"
}
```

使用绝对路径指定某个 plugin
``` sh
[*] webanalyzer -u "http://blog.fatezero.org" -p /abs/path/to/hexo.json
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

w = webanalyzer.WebAnalyzer()

w.headers = {
    "User-Agent": "custom ua",
    "header-key": "header-value"
}

w.allow_redirect = True
w.aggression = 0
r = w.start("http://www.fatezero.org")

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

* [webanalyzer rules](https://github.com/webanalyzer/rules)
