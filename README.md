<h1 align="center">openctp-ctp-channels </h1>

<div>
    <a href="#"><img src="https://flat.badgen.net/badge/os/windows-x86/cyan?icon=windows" /></a>
    <a href="#"><img src="https://flat.badgen.net/badge/os/windows-x86_64/cyan?icon=windows" /></a>
    <a href="#"><img src="https://img.shields.io/badge/os-linux_x86_64-white?style=flat-square&logo=linux&logoColor=white&color=rgb(35%2C189%2C204)" /></a>
    <a href="#"><img src="https://flat.badgen.net/badge/python/>=3.7/blue" /></a>
    <a href="#" ><img src="https://flat.badgen.net/badge/license/BSD-3/blue?" /></a>
    <a href="https://pypi.org/project/openctp-ctp-channels/" >
      <img src="https://flat.badgen.net/badge/pypi/v0.1.0/blue?" />
    </a>

</div>
<br>

[openctp](https://github.com/openctp/openctp)
提供了兼容各大柜台的统一 CTPAPI 兼容接口库，[openctp-ctp](https://github.com/openctp/openctp-ctp-python) 也继承了这个能力。

**openctp-ctp-channels** 简化了替换兼容接口库的过程，可以快速上手体验，连接不同的柜台环境。

## 快速使用

- 安装

  ```shell
  pip install openctp-ctp-channels -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host=pypi.tuna.tsinghua.edu.cn
  ```
- 展示所有通道
  ```shell
  $ openctp-channels show 
  Support channels:
        ctp - 官方实现
        tts - openctp TTS
        qq - 腾讯财经
        sina - 新浪财经
  ```
- 展示当前通道
  ```shell
  $ openctp-channels check
  Current channel: ctp
  ```
- 切换通道
  ```shell
  $ openctp-channels switch tts
  Switch to tts channel.
  
  $ openctp-channels check
  Current channel: tts
  ```
  切换通道 **tts** 成功后，即可使用 openctp-ctp
  库连接 [TTS 环境](http://openctp.cn/report/openctp%A3%A8TTS%A3%A97x24%BB%B7%BE%B3process%BD%BB%D2%D7.html)

## 支持通道

- [x] TTS
- [x] 新浪财经  
  只能查询行情，不可以交易，[详情见](https://github.com/openctp/openctp/blob/master/ctp2Sina/readme.md)
- [x] 腾讯财经  
  只能查询行情，不可以交易，[详情见](https://github.com/openctp/openctp/blob/master/ctp2QQ/readme.md)
- [ ] 中泰XTP
- [ ] 华鑫TORA
- [ ] 易盛
- [ ] 易达
- [ ] 东方证券OST
- [ ] 量投QDP
- [ ] 东方财富EMT

## 代码示例

todo...

## 注意

- openctp-ctp 在被使用中时，无法切换通道
- 如果开启了网络代理，切换通道可能失败，关闭代理重试
