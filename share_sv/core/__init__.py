import os
from collections import defaultdict

import click

from share_sv.util import parse_sv, safe_open


def sv_sort(item):
    """sort SV by chrom and region
    """
    key = item['key']
    chroms = [str(i) for i in range(1, 23)] + ['x', 'y', 'm', 'mt']
    if len(key) == 3:
        return chroms.index(key[0].strip('chr').lower()), key[1], key[2]
    else:
        return chroms.index(key[0].strip('chr').lower()), key[1], chroms.index(key[2].strip('chr').lower()), key[3]


def sv_compare(sv1, sv2, svtype, fraction=0.5, distance=300):
    """compare two SVs
    """
    if svtype.lower() in ('ctx', 'itx', 'inv'):
        if sv1[0] == sv2[0] and sv1[2] == sv2[2] \
                            and abs(sv1[1] - sv2[1]) <= distance \
                            and abs(sv1[3] - sv2[3]) <= distance:
            return sv1[0], sv1[1], sv1[2], sv1[3]
    elif sv1[0] == sv2[0]:
        o_start = max(sv1[1], sv2[1]) 
        o_end = min(sv1[2], sv2[2]) 
        overlap = float(o_end - o_start)
        if overlap / (sv1[2] - sv1[1]) >= fraction and overlap / (sv2[2] - sv2[1]) >= fraction:
            return sv1[0], o_start, o_end


def sv_share(infiles, outfile, fraction=0.5, distance=300):
    """generate the shared SVs
    """
    sv_all = defaultdict(list)
    origin_lines = defaultdict(dict)

    for filename in infiles:
        sample = os.path.basename(filename).split('.')[0]
        for svtype, key, line, headerlist in parse_sv(filename):

            if svtype in ('ctx', 'itx', 'inv'):
                if (key[2], key[3], key[0], key[1]) in sv_all[svtype]:
                    continue

            sv_all[svtype].append({
                'key': key,
                'members': [sample + '__' + '_'.join(map(str, key))],
            })

            origin_lines[svtype][sample + '__' + '_'.join(map(str, key))] = line


    # - sort all SVs by coordinate
    # - compare two adjacent SVs
    share_sv_all = {2: defaultdict(list)}
    for svtype, items in sv_all.items():

        last_item = None
        for item in sorted(items, key=sv_sort):
            if last_item is None:
                last_item = item
                continue
            res = sv_compare(last_item['key'], item['key'], svtype, fraction=fraction, distance=distance)
            if res:
                # print(res)
                # print(svtype, last_item, item)
                share_sv_all[2][svtype].append({
                    'key': res,
                    'members': last_item['members'] + item['members']
                })
            last_item = item

    # similar for more samples share
    n = 2
    while True:
        if n not in share_sv_all:
            break
        for svtype in share_sv_all[n]:
            last_item = None
            for item in share_sv_all[n][svtype]:
                if last_item is None:
                    last_item = item
                    continue
                
                res = sv_compare(last_item['key'], item['key'], svtype, fraction=fraction, distance=distance)
                if res:
                    if n + 1 not in share_sv_all:
                        share_sv_all[n + 1] = defaultdict(list)
                    share_sv_all[n + 1][svtype].append({
                        'key': res,
                        'members': list(set(last_item['members'] + item['members']))
                    })
            last_item = item
        n += 1

    # output with additional columns
    with safe_open(outfile, 'w') as out:

        if 'CNVType' in headerlist:
            typ = 'ShareCNV'
        else:
            typ = 'ShareSV'

        out.write('\t'.join([typ, 'ShareCount', 'ShareMembers', 'MemberDetail'] + headerlist) + '\n')

        filter_key = {}

        for n in sorted(share_sv_all, reverse=True):
            for svtype in share_sv_all[n]:
                for item in share_sv_all[n][svtype]:
                    key = '{}({})'.format(svtype, '_'.join(map(str, item['key'])))

                    if key in filter_key:
                        continue
                    filter_key[key] = True

                    members = ','.join([each.split('__')[0] for each in item['members']])

                    for member in item['members']:
                        origin_line = origin_lines[svtype][member]
                        out.write(f'{key}\t{n}\t{members}\t{member}\t{origin_line}')

    click.secho('save file: {}'.format(outfile), fg='green')
