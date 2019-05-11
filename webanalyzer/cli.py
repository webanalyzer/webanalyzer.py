# -*- coding: utf-8 -*-

"""Console script for webanalyzer."""

import json
import click
import logging
from .webanalyzer import WebAnalyzer


@click.command()
@click.option('-u', '--url', required=True, type=click.STRING, help='Target')
@click.option('-a', '--aggression', type=click.IntRange(0, 2), default=0,
              help='Aggression mode, 1 enable custom plugins aggression mode, 2 enable all plugins aggression mode')
@click.option('-U', '--user-agent', type=click.STRING, help='Custom user agent')
@click.option('-H', '--header', multiple=True, help='Pass custom header LINE to serve')
@click.option('-r', '--disallow-redirect', is_flag=True, default=False, help='Disallow redirect')
@click.option('-l', '--list-plugins', is_flag=True, default=False, help='List the plugins')
@click.option('-v', '--verbose', type=click.IntRange(0, 5), default=2, help='Verbose level')
@click.option('-p', '--plugin', type=click.STRING, help="Specify plugin")
def main(url, aggression, user_agent, header, disallow_redirect, list_plugins, verbose, plugin):
    w = WebAnalyzer()

    if False and list_plugins:
        w.load_plugins()
        for i in w.rules.values():
            if i.get('desc'):
                print('%s - %s - %s' % (i['name'], i['origin'], i['desc']))
            else:
                print('%s - %s' % (i['name'], i['origin']))

        return

    if aggression:
        w.aggression = aggression

    if user_agent:
        w.headers['user-agent'] = user_agent

    if header:
        for i in header:
            if ':' not in i:
                continue

            key, value = i.split(':', 1)
            w.headers[key] = value

    if disallow_redirect:
        w.allow_redirect = not disallow_redirect

    logging.basicConfig(format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    w.logger.setLevel((5-verbose)*10)

    if plugin:
        r = w.test_plugin(plugin, url)
        print(json.dumps(r, indent=4))
        return

    r = w.start(url)
    print(json.dumps(r, indent=4))


if __name__ == "__main__":
    main()
