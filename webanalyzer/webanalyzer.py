#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import urllib3
import hashlib
import logging
import requests
import urllib.parse
from lxml import etree
from .condition import Condition
from . import __version__

urllib3.disable_warnings()


class WebAnalyzer(object):
    rules = {}
    plugin_types = set()
    plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')

    def __init__(self):
        self.aggression = False
        self.url = None
        self.targets = {}
        self.headers = {
            'user-agent': 'webanalyzer/%s' % __version__
        }
        self.cond_parser = Condition()
        self.allow_redirect = True
        self.logger = logging.getLogger(__file__)

    def load_plugins(self):
        new_plugins = set()
        for plugin_type in os.listdir(self.plugin_dir):
            self.plugin_types.add(plugin_type)
            plugin_type_dir = os.path.join(self.plugin_dir, plugin_type)
            for i in os.listdir(plugin_type_dir):
                if not i.endswith('.json'):
                    continue

                with open(os.path.join(plugin_type_dir, i)) as fd:
                    try:
                        data = json.load(fd)
                        new_plugins.add(data['name'])
                        for match in data['matches']:
                            for key in match:
                                if key == 'regexp':
                                    match[key] = re.compile(match[key], re.I | re.DOTALL)

                            if 'certainty' not in match:
                                match['certainty'] = 100
    
                        data['origin'] = plugin_type
                        key = '%s_%s' % (plugin_type, data['name'])
                        self.rules[key] = data
                        new_plugins.add(key)
                    except Exception as e:
                        self.logger.error('parse %s failed, error: %s' % (i, e))

        # disable rules
        disabled_rules = set(self.rules.keys()) - new_plugins
        for rule in disabled_rules:
            self.rules.pop(rule)

    def request(self, url):
        try:
            rp = requests.get(url, headers=self.headers, verify=False, allow_redirects=self.allow_redirect)
        except Exception as e:
            self.logger.error("request error: %s" % str(e))
            return

        script = []
        meta = {}

        p = etree.HTML(rp.text)

        if p is not None:
            for data in p.xpath("//script"):
                script_src = data.get("src")
                if script_src:
                    script.append(script_src)

            for data in p.xpath("//meta"):
                meta_name = data.get("name")
                meta_content = data.get("content")
                if meta_name or meta_content:
                    meta[meta_name] = meta_content

        raw_headers = '\n'.join('{}: {}'.format(k, v) for k, v in rp.headers.items())
        self.targets[url] = {
            "url": url,
            "body": rp.text,
            "headers": rp.headers,
            "status": rp.status_code,
            "script": script,
            "meta": meta,
            "cookies": rp.cookies,
            "raw_cookies": rp.headers.get("set-cookie", ""),
            "raw_response": raw_headers + rp.text,
            "raw_headers": raw_headers,
            "md5": hashlib.md5(rp.content).hexdigest(),
        }

        return self.targets[url]

    def check_match(self, match, aggression=False):
        s = {'regexp', 'text', 'md5', 'status'}
        if not s.intersection(list(match.keys())):
            return False

        target = self.targets[self.url]
        if 'url' in match:
            full_url = urllib.parse.urljoin(self.url, match['url'])
            if match['url'] == '/':  # 优化处理
                pass
            elif full_url in self.targets:
                target = self.targets[full_url]
            elif aggression:
                target = self.request(full_url)
            else:
                self.logger.debug("match has url(%s) field, but aggression is false" % match['url'])
                return False

        # parse search
        search_context = target['body']
        if 'search' in match:
            if match['search'] == 'all':
                search_context = target['raw_response']
            elif match['search'] == 'headers':
                search_context = target['raw_headers']
            elif match['search'] == 'script':
                search_context = target['script']
            elif match['search'] == 'cookies':
                search_context = target['raw_cookies']
            elif match['search'].endswith(']'):
                for i in ('headers', 'meta', 'cookies'):
                    if not match['search'].startswith('%s[' % i):
                        continue

                    key = match['search'][len('%s[' % i):-1]
                    if key not in target[i]:
                        return
                    search_context = target[i][key]

            match.pop('search')

        version = None
        for key in list(match.keys()):
            if key == 'status':
                if match[key] != target[key]:
                    return False

            if key == 'md5':
                if target['md5'] != match['md5']:
                    return False

            if key == 'text':
                search_contexts = search_context
                if isinstance(search_context, str):
                    search_contexts = [search_context]

                for search_context in search_contexts:
                    if match[key] not in search_context:
                        continue
                    break
                else:
                    return False

            if key == 'regexp':
                search_contexts = search_context
                if isinstance(search_context, str):
                    search_contexts = [search_context]

                for search_context in search_contexts:
                    result = match[key].findall(search_context)
                    if not result:
                        continue

                    if 'offset' in match:
                        if isinstance(result[0], str):
                            version = result[0]
                        elif isinstance(result[0], tuple):
                            if len(result[0]) > match['offset']:
                                version = result[0][match['offset']]
                            else:
                                version = ''.join(result[0])
                    break
                else:
                    return False

        return version if version else True

    def check_rule(self, rule):
        matches = rule['matches']

        cond_map = {}
        result = {
            'name': rule['name'],
            'origin': rule['origin']
        }

        for index, match in enumerate(matches):
            aggression = False
            if self.aggression == 2:
                aggression = True
            elif self.aggression == 1 and rule['origin'] == 'custom':
                aggression = True

            r = self.check_match(match, aggression=aggression)
            if r:
                cond_map[str(index)] = True
                if not isinstance(r, bool):
                    result['version'] = r
            else:
                cond_map[str(index)] = False

        # default or
        if 'condition' not in rule:
            if any(cond_map.values()):
                return result
            return

        if self.cond_parser.parse(rule['condition'], cond_map):
            return result

    def start(self, url):
        self.logger.debug("process %s" % url)
        self.url = url
        results = []
        implies = set()
        excludes = set()

        if not self.request(url):
            self.logger.info("request %s failed" % url)
            return

        self.request(urllib.parse.urljoin(url, '/favicon.ico'))

        self.load_plugins()
        for name, rule in self.rules.items():
            r = self.check_rule(rule)
            if r:
                results.append(r)

                if 'implies' in rule:
                    if isinstance(rule['implies'], str):
                        implies.add(rule['implies'])
                    else:
                        implies.update(rule['implies'])

                if 'excludes' in rule:
                    if isinstance(rule['excludes'], str):
                        excludes.add(rule['excludes'])
                    else:
                        excludes.update(rule['excludes'])

        i = 0
        while i < len(results):
            if results[i]['name'] in excludes:
                results.pop(i)
                continue
            i += 1

        i = 0
        implies = list(implies)
        while i < len(implies):
            results.append({
                'name': implies[i],
                "origin": 'implies'
            })

            for plugin_type in self.plugin_types:
                plugin_name = '%s_%s' % (plugin_type, implies[i])
                if plugin_name not in self.rules:
                    continue

                rule = self.rules[plugin_name]
                if 'implies' in rule:
                    if isinstance(rule['implies'], str) and \
                            rule['implies'] not in excludes and \
                            rule['implies'] not in implies:
                        implies.append(rule['implies'])
                    else:
                        for im in rule['implies']:
                            if im not in excludes and im not in implies:
                                implies.append(im)

                if 'excludes' in rule:
                    if isinstance(rule['excludes'], str):
                        excludes.add(rule['excludes'])
                    else:
                        excludes.update(rule['excludes'])

            i += 1

        i = 0
        while i < len(results):
            if results[i]['name'] in excludes:
                results.pop(i)
                continue
            i += 1

        return results


if __name__ == '__main__':
    from pprint import pprint

    w = WebAnalyzer()
    wr = w.start("https://www.fatezero.org")
    pprint(wr)
