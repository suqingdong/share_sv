from email import contentmanager
import os


def safe_open(filename, mode='r'):

    if 'w' in mode:
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    if filename.endswith('.gz'):
        import gzip
        return gzip.open(filename, mode=mode)

    return open(filename, mode=mode)


def parse_sv(filename):
    with safe_open(filename) as f:
        for line in f:
            linelist = line.strip().split('\t')
            if linelist[0] in ('Chr', 'Priority'):
                headerlist = linelist
                continue
            context = dict(zip(headerlist, linelist))
            svtype = context.get('SVType') or context.get('CNVType')
            if svtype == 'breakpoint':
                continue

            chrom = context['Chr']
            tchrom = context['TCHR']
            start = int(context['Start'])
            end = int(context['End'])

            if len(chrom) > 5 or len(tchrom) > 5:
                continue

            if svtype.lower() in ('ctx', 'itx', 'inv'):
                
                if tchrom == 'na':
                    tchrom = context['Chr']
                    tstart = int(context['Start'])
                else:
                    tstart = int(context['TSTART'])

                key = (chrom, start, tchrom, tstart)
            else:
                key = (chrom, start, end)

            yield svtype, key, line, headerlist

            # ITX/CTX：染色体内(间)异位比较特殊，成对出现
            # 需要关注CHR, START, TCHR, TSTART
            # CTX的TCHR还可能出现特殊染色体，如GL000220.1
