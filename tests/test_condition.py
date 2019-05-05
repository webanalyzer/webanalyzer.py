# -*- coding: utf-8 -*-

from webanalyzer import Condition
from webanalyzer.condition import ParseException


def test_simple():
    s_tab = {
        "1": True,
        "2": False,
        "3": True,
        "4": False,
        "name1": True,
        "name2": False,
        "name3": True,
        "name4": False
    }

    conds = {
        "1": True,
        "2": False,
        "name1": True,
        "name2": False,
        "((((name1))))": True,
        "name1 and name2": False,
        "name1 and not name2": True,
        "name1 or name2": True,
        "name2 or name1 and name2": False,
        "name1 and not (name1 and name2)": True,
        "(name1 or name2) and (name3 and (1 or 2))": True,
    }

    c = Condition()
    for i, r in conds.items():
        assert c.parse(i, s_tab) is r


def test_invalid():
    s_tab = {
        1: True,
        "include space": False,
        "2": False,
        "name1": True,
        "name2": False,
    }

    conds = {
        '1',
        "include space",
        "name1 name2",
        "name1 or",
        "()",
        "and name1",
        "not_exists_name",
        "name1 or not_exists_name",
        "name1 and not",
        "(name1 and name2"
    }

    c = Condition()
    for i in conds:
        try:
            c.parse(i, s_tab)
            assert False, "never get here"
        except ParseException:
            pass

