# [xproc](https://github.com/hungrybirder/xproc)

## Install

```bash
pip install -U xproc
```

## Support commands

*   `xproc mem` or `xproc memory`

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

*   `xproc vmstat`

```bash
xproc vmstat 1 5
        TIME allocstall_movable allocstall_normal compact_fail compact_free_scanned compact_isolated compact_migrate_scanned compact_stall compact_success
    10:15:01              40908                55            0               108344            75443                   43462            56              56
    10:15:02              40908                55            0               108344            75443                   43462            56              56
    10:15:03              40908                55            0               108344            75443                   43462            56              56
    10:15:04              40908                55            0               108344            75443                   43462            56              56
    10:15:05              40908                55            0               108344            75443                   43462            56              56
```

*   `xproc load`

```bash
xproc load 1 3
        TIME   LOAD_1_MIN   LOAD_5_MIN  LOAD_15_MIN   NR_RUNNING     NR_TOTAL     LAST_PID
    14:28:34         0.07         0.18         0.15            1          316      2073102
    14:28:35         0.07         0.18         0.15            1          316      2073102
    14:28:36         0.07         0.18         0.15            1          316      2073102
```
