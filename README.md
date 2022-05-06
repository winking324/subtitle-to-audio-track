# 字幕转音轨 Subtitle to Audio Track

给小朋友看纪录片时，大多数都是英文的，所以不得不充当人工翻译，但是人工翻译的效率很低，容易错过一些精彩的内容。 
所以在刚好看到字幕的瞬间，想到了一个不错的想法：把字幕转成语音，替换进去不就好了吗？

# 流程

假设有一个视频为 `A.mkv`，大概的流程如下：
1. 提取 `A.mkv` 的音轨为 `A.mp3`；
2. 使用 [Spleeter](https://github.com/deezer/spleeter) 对 `A.mp3` 进行背景音和配音的分离；
3. 解析字幕，并调用百度语音合成 API，转换为音频段；
4. 把所有音频段和背景音合并起来成为 `B.mp3`；
5. 把 `B.mp3` 合并到 `A.mkv` 中，成为新的音轨；

# 用法

1. 保证视频和字幕在同一位置和名称，例如：
   `/your/path/to/video.mkv`
   `/your/path/to/video.ass`
2. 修改 `helper/speech.py` 中关于百度 API 接口的设置；
3. 执行 `python3 subtitle_to_audio_track.py /your/path/to/video.mkv`；
4. 最终视频文件输出到 `/your/path/to/video.ch.mkv`；

# TODO

1. 目前字幕文件只支持 `.ass` 格式；
2. ~~字幕文件的编码格式需要自动识别（目前为 UTF-16-LE）；~~
3. 通过更好的方式设置百度 API，或者增加阿里等其他 API 的支持；
4. 优化音质的问题；
5. 优化音轨，例如增加音轨名称等；
6. Docker 打包，避免用户安装环境；
7. 复杂格式的 `ass` 字幕适配；
8. 自动增加标点符号，以获取更好的 TTS 效果；
9. 如果语音时长超过字幕时长，调整语速重新生成语音；
10. 使用微软 [TTS](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/) 替换百度；

# 遗留的问题

纪录片一般只有一个角色，所以用一种角色的配音，就可以获得比较好的效果。
另外，纪录片一般采用平铺直述的方式，语言中没有很多情感的波动，所以语音中没有太多情绪特征。
所以如果要给一般的视频转换配音，就需要更高的要求和挑战了，这是该项目目前所不具备的。
