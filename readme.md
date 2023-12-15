# Design and Implementation of a Speech Recognition-based Speech Training Tool
This is a Speech Training Tool Based on XFYUN cloud speech recongnition.

It helps to train your abilities of doing presentation.

Including: Grammar Correctness, Speech Evaluation, Manuscript Editing, Freely Practice.

(This is my undergraduate graduation thesis project, inspired from my experience of doing presentation during many contests. Congratulation to my bachelor's degree of computer science, and thanks to NENU.)

# 基于语音识别的演讲训练工具
是一个使用讯飞开放平台 API 进行语音识别的演讲训练工具。
能够尝试帮助您提高演讲能力，
提供自动语法纠错、语音评价、撰稿功能等多种功能。


## 主要功能
### 撰稿功能
根据用户的幻灯片或章节需求，帮助用户编写对应的提示稿或台词稿。支持导出花脸稿版本的 PDF 文件。

### 对稿演练功能
提供一个界面，帮助用户进行计时演练。展示当前幻灯片页面、下一幻灯片页面、稿件内容。支持录音和实时语音纠正。

### 自由演练功能
用户进行 60 秒的自由录音演讲。除了不使用任何稿件之外，其余功能与“对稿演练功能”一致。

### 模拟训练功能
用户使用提供的预设稿件内容进行模拟演讲。演讲过程与“对稿演练功能”一致。


### doc ref
讯飞开放平台(xunfei open platform):https://www.xfyun.cn/doc/

## 已知问题BUGS

### 2023/4/12
1. 运行稳定性问题，在语音识别结束时，小概率会崩溃。
2. 稿件导出pdf依然是随机彩色，并没有特定格式
3. audio player 滑条无效，界面奇怪
4. 语音评价没有“标点符号长度”、“建议提供”功能
5. UI设计不够友好，并且标题栏不太好看，按钮功能不够显著
