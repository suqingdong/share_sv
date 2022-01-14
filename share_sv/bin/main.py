"""
    Share SV/CNV
"""
import json
import click

from share_sv import version_info
from share_sv.core import sv_share


__epilog__ = click.style('''examples:

\b
    share_sv *.SV.xls -o share_sv.xls
    share_sv *.CNV.xls -o share_cnv.xls -f 0.7
    share_sv *.SV.xls -o share_sv.xls -f 0.7 -d 250

contact: {author} <{author_email}
'''.format(**version_info), fg='green')


@click.command(
    help=click.style(__doc__, fg='blue', bold=True),
    epilog=__epilog__,
    no_args_is_help=True,
)
@click.argument('infiles', nargs=-1)
@click.option('-o', '--outfile', help='the output filename', default='share_sv.xls', show_default=True)
@click.option('-f', '--fraction', help='the fraction of overlapping', type=float, default=0.5, show_default=True)
@click.option('-d', '--distance', help='the distance of breakpoints', type=int, default=300, show_default=True)
def main(**kwargs):
    click.secho('input arguments: {}'.format(
        json.dumps(kwargs, indent=2)), fg='yellow', err=True)

    if not kwargs['infiles']:
        click.secho('please input two or more files', fg='yellow')
        exit(1)

    sv_share(kwargs['infiles'], kwargs['outfile'],
             fraction=kwargs['fraction'], distance=kwargs['distance'])


if __name__ == '__main__':
    main()
