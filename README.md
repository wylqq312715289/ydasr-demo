## 测试单条音频输出


### onetime/stream demo

```python
python asr_test.py -type onetime -url 'http://www.*****.com/asr' -lg en -w test.wav
python asr_test.py -type stream  -url 'ws://www.*****.com' -lg en -w test.wav
python asr_test.py -type onetime -url 'http://www.*****.com/asr' -lg cn -w test.wav
python asr_test.py -type stream  -url 'ws://www.*****.com' -lg cn -w test.wav
```


### onetime/stream press demo

```python
python qps_test.py -type onetime -url 'http://www.*****.com/asr' -lg en -w test.wav -n 1000 -pool 50
python qps_test.py -type stream  -url 'ws://www.*****.com' -lg en -w test.wav -n 1000 -pool 50
python qps_test.py -type onetime -url 'http://www.*****.com/asr' -lg cn -w test.wav -n 1000 -pool 50
python qps_test.py -type stream  -url 'ws://www.*****.com' -lg cn -w test.wav -n 1000 -pool 50
```

- pool: 并发的路数
- n: 打多少case
- w: 使用哪个用例打压
- lg: 语种  中文:cn  英文: en
