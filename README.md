# webanalyzer

[![PyPI](https://img.shields.io/pypi/v/webanalyzer.svg)](https://pypi.python.org/pypi/webanalyzer)


## 安装

```sh
pip install -U webanalyzer
```

## 使用

### 命令行

```sh
webanalyzer -u "http://www.fatezero.org"
```

usage:

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
  -v, --verbose INTEGER           Verbose level
  --help                          Show this message and exit.
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

## 规则编写

### 基础信息

例子:

```json
{
    "name": "wordpress",
    "author": "fate0",
    "version": "0.1.0",
    "description": "wordpress 是世界上最为广泛使用的博客系统",
    "website": "http://www.wordpress.org/",
    "matches": [],
    "condition": "0 and 1 and not 2",
    "implies": "PHP",
    "excludes": "Apache"
}
```

描述:

| FIELD       | TYPE   | DESCRIPTION  | EXAMPLE                                    | REQUIRED |
|-------------|--------|--------------|--------------------------------------------|----------|
| name        | string | 组件名称     | `wordpress`                                | true     |
| author      | string | 作者名       | `fate0`                                    | false    |
| version     | string | 插件版本     | `0.1.0`                                    | false    |
| description | string | 组件描述     | `wordpress 是世界上最为广泛使用的博客系统` | false    |
| website     | string | 组件网站     | `http://www.wordpress.org/`                | false    |
| matches     | array  | 规则         | `[{"regexp": "wordpress"}]`                | true     |
| condition   | string | 规则组合条件 | `0 and 1 and not 2`                        | false    |
| implies     | string/array | 依赖的其他组件 | `PHP`                               | false    |
| excludes    | string/array | 肯定不依赖的其他组件 | `Apache`                       | false    |


### 规则信息

例子:

```
[
    {
        "name": "rule name"
        "search": "all",
        "text": "wordpress"
    }
]
```

描述:

| FIELD      | TYPE   | DESCRIPTION                                                             | EXAMPLE                            |
|------------|--------|-------------------------------------------------------------------------|------------------------------------|
| name       | string | 规则名称                                                                | `rulename`                         |
| search     | string | 搜索的位置，可选值为 `all`, `headers`, `body`, `script`, `cookies`, `headers[key]`, `meta[key]`, `cookies[key]`| `body`                              |
| regexp     | string | 正则表达式                                                              | `wordpress.*`                      |
| text       | string | 明文搜索                                                                | `wordpress`                        |
| version    | string | 匹配的版本号                                                            | `0.1`                              |
| offset     | int    | regexp 中版本搜索的偏移                                                  | `1`                                |
| certainty  | int    | 确信度                                                                  | `75`                               |
| md5        | string | 目标文件的 md5 hash 值                                                  | `beb816a701a4cee3c2f586171458ceec` |
| url        | string | 需要请求的 url                                                          | `/properties/aboutprinter.html`    |
| status     | int    | 请求 url 的返回状态码，默认是 200                                       | `400`                              |


## 返回信息

例子:

```
[
    {
        "name": "4images",
        "version": "1.1",
        "certainty": 100,
        "origin": "custom"
    }
]
```

描述:

| FIELD       | TYPE   | DESCRIPTION  | EXAMPLE                                    | REQUIRED |
|-------------|--------|--------------|--------------------------------------------|----------|
| name        | string | 组件名称     | `wordpress`                                | true     |
| version     | string | 插件版本     | `0.1.0`                                    | false    |
| certainty     | int  | 确信度         | `75`                | false     |
| origin     | string | 插件来源     | `custom`                | false    |


## 检测逻辑

* 如果 match 中存在 url 字段，plugin 是属于 custom 类型且 `aggression` 开启，则请求 url 获取相关信息
* 根据 search 字段选取搜索位置
* 根据 regexp/text 进行文本匹配，或者 status 匹配状态码，或者 md5 匹配 body 的 hash 值
* 如果 match 中存在 version 就表明规则直接出对应版本，如果存在 offset 就表明需要从 regexp 中匹配出版本
* 如果 rule 中存在 condition，则根据 condition 判断规则是否匹配，默认每个 match 之间的关系为 `or`

## Q & A

* WhatWeb 的规则如何转换成 webanalyzer 的规则？

可以看下 [tools/whatweb.rb](tools/whatweb.rb) 代码，实际上我这并没有成功转换全部规则，依旧有部分 passive, aggressive 函数规则以及其他规则并没去转换，
不过成功转换比例占大多数。

* Wappalyzer 的规则如何转换成 webanalyzer 的规则？

可以看下 [tools/wappalyzer.py](tools/wappalyzer.py) 代码，因为 Wappalyzer 的规则本来就是 json 格式，所以比较容易转换，但是依旧有部分字段我没有保留在我的规则中。

* 为什么使用 json 作为规则格式？

更通用，即便更换编程语言，也可以继续复用本来的规则。

* 和 WhatWeb、Wappalyzer 的区别？

WhatWeb 的规则使用 ruby 编写，在规则方面，其他编程语言很难复用，也只能通过子进程的方式调用 WhatWeb。
Wappalyzer 更多的作为一个浏览器插件使用。


* 如何同步 WhatWeb、Wappalyzer 的规则？

可以看下 [.travis.yml](https://github.com/fate0/webanalyzer/blob/build/.travis.yml)，通过 travis-ci 达到每天自动同步规则，每月自动同步至 pypi 。

* 为什么只支持 Python3.6 以及以上的 Python 版本？

因为有些正则规则使用了 `(?-flag:...)` 这样的写法，然而在
[https://docs.python.org/3/whatsnew/3.6.html#re](https://docs.python.org/3/whatsnew/3.6.html#re)
才开始支持。

* License 为什么是 GPL-2.0 ？

因为 WhatWeb 就是 GPL-2.0，虽然我没有抄代码，但是规则是通过 WhatWeb 转换过来的，虽然不确定会不会传染，
为了保险起见就设置成和 WhatWeb 一样的 License 。


## 引用

* [WhatWeb](https://github.com/urbanadventurer/WhatWeb)
* [Wappalyzer](https://github.com/AliasIO/Wappalyzer)