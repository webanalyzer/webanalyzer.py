# -*- coding: utf-8 -*-

"""Console script for webanalyzer."""

import json
import click
from .webanalyzer import WebAnalyzer


@click.command()
@click.option('-u', '--url', required=True, type=click.STRING, help='Target')
@click.option('-a', '--aggression', type=click.IntRange(0, 2), default=0,
              help='Aggression mode, 1 enable custom plugins aggression mode, 2 enable all plugins aggression mode')
@click.option('-U', '--user-agent', type=click.STRING, help='Custom user agent')
@click.option('-H', '--header', multiple=True, help='Pass custom header LINE to serve')
@click.option('-r', '--disallow-redirect', is_flag=True, default=False, help='Disallow redirect')
@click.option('-l', '--list-plugins', is_flag=True, default=False, help='List the plugins')
@click.option('-v', '--verbose', type=click.INT, default=0, help='Verbose level')
def main(url, aggression, user_agent, header, disallow_redirect, list_plugins, verbose):
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

    if verbose:
        w.verbose = verbose

    r = w.start(url)
    print(json.dumps(r, indent=4))


if __name__ == "__main__":
    main()
