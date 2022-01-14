# Share SV/CNV

## Installation
```bash
python3 -m pip install share_sv
```

## Usage

> - input: *.SV(CNV).xls -- SV(CNV) files from      `crest`, `lumpy`, `freec` or `conifer`
> - output: add four columns: `ShareSV`, `ShareCount`, `ShareMembers`, `MemberDetail`

```bash

share_sv *.SV.xls -o share_sv.xls

share_sv *.CNV.xls -o share_cnv.xls -f 0.7
      
share_sv *.SV.xls -o share_sv.xls -f 0.7 -d 250
```
