# coding=utf-8
import os
import json

__all__ = ['normalize']


def loadCharMap():
    """
    init chars map
    """
    cmap = {}
    # empty
    for x in range(0x20+1):
        cmap[chr(x)] = u' '
    cmap[chr(0x7F)] = u' '
    for x in range(8198, 8208):
        cmap[chr(x)] = u' '
    for x in range(8232, 8240):
        cmap[chr(x)] = u' '
    for x in range(8287, 8304):
        cmap[chr(x)] = u' '
    for x in range(0xFE00, 0xFE0F + 1):
        cmap[chr(x)] = u' '

    # q2ban
    for x in range(65281, 65374+1):
        cmap[chr(x)] = chr(x-65248)
    cmap[chr(12288)] = chr(32)
    cmap[chr(65533)] = ' '

    # special map
    special = [('“', '"'), ('”', '"'), ('、', ','), ('〜', '~'), ('～', '~'), ('－', '-'), ('–', '-'), ('\r', '\n'),
               ('︳', '|'), ('▎', '|'), ('ⅰ', 'i'), ('丨', '|'), ('│', '|'), ('︱', '|'), ('｜', '|'), ('／', '/'),
               ('『', '《'), ('《', "《"), ('〖', '《'), ('】', '》'), ('〗', "》"), ('【', '《'), ('》', '》'),
               ('』', '》'), ('「', '《'),  ('」', '》'), ('❬', "《"), ('❭', "》"), ('❮', "《"), ("❯", "》"),
               ('❰', '《'), ('❱', '》'), ('〘', '《'), ('〙', '》'), ('〚', '《'), ('〛', '》'), ('〉', '》'), ('《', '《'),
               ('》', '》'), ('「', '《'), ('」', '》'), ('『', '《'), ('』', '》'), ('【', '《'), ('】', '》'), ('〔', '《'),
               ('〕', '》'), ('〖', '《'), ('〗', '》')
               ]
    for k, v in special:
        cmap[k] = v

    unicode_maps = [(u'\uf0b7', ' '), ('\uf0b2', ''), ('\uf064', ''), ('\uf0e0', ''), ('\uf06c', ''),
                    ('\ue6a5', ''), ('\ue6a3', ''), ('\ue6a0', ''), ('\uE77C', ''), ('\uE76E', ''),
                    ('\uf077', ' '), ('\ue710', ''), ('\ue711', ''), ('\ue712', ''), ('\ue713', ''),
                    ('\ue723', ''), ('\ue793', ''), ('\uf06c', ' '), ('\uf0d8', ' '), ('\uf020', ' '),
                    ('\uF0FC', ''), ('\uF0FC', ''), ('\uE755', ''), ('\uE6D2', ''), ('\uE63C', ''),
                    ('\uE734', ''), ('\uF074', ''), ('\uE622', ''), ('\uF241', ''), ('\uE71B', ''),
                    ('\uF148', ''), ('\uE973', ''), ('\uE96E', ''), ('\uE96A', ''), ('\uE97D', ''),
                    ('\uE805', ''), ('\uE70D', ''), ('\uF258', ''), ('\uE7BB', ''), ('\uE806', ''),
                    ('\uE930', ''), ('\uE739', ''), ('\uF0A4', ''), ('\uE6A4', ''), ('\uFEFF', ''),
                    ('\uE69E', ''), ('\uF06E', ''), ('\uF075', ''), ('\uF0B7', ''), ('\u009F', ''),
                    ('\uF0B7', ''), ('\uF076', ''), ('\uF09F', ''), ('\uF0A8', ''), ('\uE69F', ''),
                    ('\uF097', ''), ('\uF0A1', ''), ('\uf034', ''),
                    ]

    for k, v in unicode_maps:
        cmap[k] = v

    # file map
    py_dir = os.path.split(os.path.realpath(__file__))[0]
    with open(os.path.abspath(os.path.join(py_dir, 'confusables.json')), encoding='utf-8') as fd:
        for (k, v) in json.load(fd).items():
            k = k.strip()
            for ch in v:
                cmap[ch] = k

    # check wordmap and fix it
    _TMP = {}
    for k, v in cmap.items():
        if k != v:
            _TMP[k] = v
    ####################################notice#####################
    # '\n' don't replace,\t replace 4 space empty,notice!!!!!!!!!!
    if '\n' in _TMP:
        del _TMP['\n']
    _TMP['\t'] = ' '*4
    if ' ' in _TMP:
        del _TMP[' ']
    ###############################################################
    cmap = _TMP
    for k, v in cmap.items():
        if v in cmap:
            cmap[k] = cmap[v]
    return cmap


_WORD_MAP = loadCharMap()


def normalize(content: str) -> str:
    """
    normalize unicode string
    """
    return "".join(_WORD_MAP.get(c, c) for c in content)
