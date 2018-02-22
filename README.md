# Surveys using Flask

帮助实验室写的问卷系统，因为各种原因，拖了很久，最终总算写完了。基本功能可以使用。但是好像实验室懒得用了，所以决定放在这里。使用Flask开发。

## 基本功能

用户分为管理员（admin）、督导师、咨询师和来访者四种。督导师可以给咨询师分发问卷，咨询师给来访者分发问卷。针对来访者的问卷结果咨询师可以给出反馈。督导师可以查看来访者问卷的结果和咨询师的反馈并给予评论。

## 问卷格式

问卷使用Yaml格式创建，例如：

```
option1: &option1
  - 
    - 0
    - 从未
  - 
    - 1
    - 很少
  - 
    - 2
    - 有时
  - 
    - 3
    - 经常
  - 
    - 4
    - 几乎总是
pages:
  -
    style: info
    info: 
    items:
    - id: age
      title: 年龄
      type: input
    - id: gender
      title: 性别
      type: radio
      value: 
        - 
          - 1
          - 男
        - 
          - 0
          - 女
    - id: uuid
      title: 编号
      type: input
    - id: count
      title: 会谈次数
      type: input
    - id: date
      title: 日期
      type: input
    - id: agree
      title: 同意用户协议
      type: check
      value: 
        - 
          - 1
          - 是
  -
    style: survey
    info: 作答说明：以下题目是用来了解您上周（包括今天）的感受。请仔细阅读每个题目，并在最符合您目前状况的方框内打勾。该问卷中的“工作”是指职业、家务、志愿工作等。
    items:
    - id: q01
      title: 1. 我与他人相处融洽。
      type: radio
      value: *option1
```

问卷也可以定义维度，比如：

```
D0: q01+q02+q03+q04+q05
D1: q02+q03+q05
D2: q01+q04
```

这些会在下载、查看结果的时候有显示

## 其他

想起来再补充吧