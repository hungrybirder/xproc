# [xproc](https://github.com/hungrybirder/xproc)

## Install

```bash
pip install -U xproc
```

## Support commands

*   `xproc mem` or `xproc meiw`

```bash
xproc mem
        TIME       KERNEL         USER      MemFree     MemTotal
    21:19:37    1345876kB   13143712kB   10079620kB   24624680kB
    21:19:38    1345964kB   13143796kB   10079612kB   24624680kB
    21:19:39    1345964kB   13143804kB   10079612kB   24624680kB
    21:19:40    1345964kB   13143808kB   10079644kB   24624680kB
    21:19:41    1345964kB   13143808kB   10079580kB   24624680kB
```

```bash
xproc mem -e "Active,Inactive,Active(anon),Inactive(anon),Active(file),Inactive(file)"
        TIME       Active     Inactive Active(anon) Inactive(anon) Active(file) Inactive(file)
    21:21:19    4397264kB    8727816kB     173164kB          128kB    4224100kB      8727688kB
    21:21:21    4397404kB    8727816kB     173300kB          128kB    4224104kB      8727688kB
    21:21:23    4397404kB    8727816kB     173300kB          128kB    4224104kB      8727688kB
    21:21:25    4397404kB    8727816kB     173300kB          128kB    4224104kB      8727688kB
    21:21:27    4397404kB    8727816kB     173300kB          128kB    4224104kB      8727688kB
```
