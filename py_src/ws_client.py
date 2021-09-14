# coding:utf-8
import json
import sys
import threading
import time  # 引入time模块
import logging
from ws4py.client.threadedclient import WebSocketClient

send_one_block_data_len_seconds = 0.02  # 发送一个block，该block所占用的时长。
send_one_block_wait_seconds = 0.02  # 每次发送一个时间片段后需要等待的时间

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s %(filename)s %(levelname)s %(message)s',
    datefmt='%a %d %b %Y %H:%M:%S')

if "2.7" in str(sys.version):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    import Queue
else:
    from queue import Queue


def rate_limited(minInterval):
    # minInterval = 发送一个请求需要等待的秒数

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.clock()
            return ret

        return rate_limited_function

    return decorate


class WSClient(WebSocketClient):
    def __init__(self, args,
                 audiofile,
                 url,
                 lang="en",
                 booked_words="",
                 protocols=None,
                 extensions=None,
                 stream_mode="full",
                 heartbeat_freq=None,
                 byterate=32000,
                 save_adaptation_state_filename=None,
                 send_adaptation_state_filename=None):
        super(WSClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.args = args
        self.audiofile = audiofile
        self.audio_enc_type = args.audio_enc_type
        self.vad_head_sil = args.vad_head_sil
        self.vad_tail_sil = args.vad_tail_sil
        self.opus_sample_rate = args.opus_sample_rate
        self.had_wav_header = args.had_wav_header
        self.rescore = args.rescore
        self.byterate = byterate  # 是字节数，kaldi中的16k是采样率，2个字节是一个采样率
        self.lang = lang
        self.stream_mode = stream_mode
        self.final_hyp_queue = Queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.semp = threading.Semaphore(30)
        self.result = []
        self.booked_words = booked_words
        self.output_time = float("%.2f" % time.time())
        self.bad_case = False
        self.sended_byte_sum = 0
        self.send_thread = None
        self.started_lock = threading.Lock()

    @rate_limited(send_one_block_wait_seconds)
    def send_data(self, data):
        if not self.terminated and not self.sock is None:
            self.send(data, binary=True)
            self.sended_byte_sum += len(data)
            # logging.info('data sent = {}'.format(len(data)))

    def _write(self, b):
        """
        Trying to prevent a write operation
        on an already closed websocket stream.

        This cannot be bullet proof but hopefully
        will catch almost all use cases.
        """
        if self.terminated or self.sock is None:
            return
        self.sock.sendall(b)

    def opened(self):
        self.started_lock.acquire()

        # print "Socket opened!"
        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                print >> sys.stderr, "Sending adaptation state from %s" % self.send_adaptation_state_filename
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    print >> sys.stderr, "Failed to send adaptation state: ", e
            options = "audio_enc_type=%s,had_wav_header=%s,opus_sample_rate=%s,rescore=%s,noitn=%s,nopunc=%s" % (
                self.audio_enc_type, self.had_wav_header, self.opus_sample_rate,
                self.rescore, self.args.noitn, self.args.nopunc)
            header = """{"lang":"%s","booked_words":"%s","options":"%s","vad_head_sil":"%s","vad_tail_sil":"%s"}""" % (
                self.lang, self.booked_words, options, self.vad_head_sil, self.vad_tail_sil)
            # print("header=", header)
            self.send(header)
            # print("begin sleep 30s")
            # time.sleep(30)
            # print('sending header: header= ', header)
            counter = 0
            tmp_block = 0
            sleep_time = 30
            with open(self.audiofile, "rb") as audiostream:
                send_block_size = int(self.byterate * send_one_block_data_len_seconds)
                if self.audio_enc_type == "opus":
                    send_block_size /= 8
                # send_block_size = 100
                for block in iter(lambda: audiostream.read(send_block_size), ""):
                    # print('%d sending size = %d'%(counter,len(block)))
                    if self.terminated:
                        break
                    self.send_data(block)
                    # print("begin sleep {}s".format(sleep_time))
                    # sleep_time += 1
                    # time.sleep(sleep_time)
                    # send_block_size = 6400
                    counter += 1
                    tmp_block = block
                    # sys.exit(0)
            # print >> sys.stderr, "Audio sent, now sending YOUDAO_ASR_EOS"
            if not self.terminated and not self.sock is None:
                self.send("YOUDAO_ASR_EOS")
                # print("had sent YOUDAO_ASR_EOS")
            # self.send(tmp_block, binary=True)

        self.send_thread = threading.Thread(target=send_data_to_ws)
        self.send_thread.start()
        self.started_lock.release()

    def received_message(self, m):
        delta_time = float("%.2f" % time.time()) - self.output_time
        self.output_time = float("%.2f" % time.time())
        if delta_time > 20:
            self.bad_case = True
        self.result.append(str(m))
        if self.stream_mode == "pass":
            pass
        elif self.stream_mode == "full":
            res_data = json.loads(str(m))
            result = json.dumps(res_data, ensure_ascii=False, encoding='utf-8')
            logging.info(str(result))
        elif self.stream_mode == "clear" or self.stream_mode == "clear1":
            res_data = json.loads(str(m))
            if not 'text' in res_data: print(res_data)
            res_data.update({"text": json.loads(res_data.get("text", "{}"))})
            text = res_data.get("text", {})
            for i in range(len(text)):
                item = text[i]
                # if "True" == str(item.get("partial")): return
                if len(item.get('words', [])) == 0:
                    continue
                st = item.get('word_timestamps', [-1])[0]
                end = item.get('word_timestamps', [-1])[-1]
                if self.lang == "cn":
                    result = " ".join(item.get('words', []))
                else:
                    result = " ".join(item.get('words', []))
                result = {"sentence": result}
                partial = item.get("partial", True)
                if partial == False and self.stream_mode == "clear":
                    result = json.dumps(result, ensure_ascii=False, encoding='utf-8')
                    logging.info("concat words: partial={} {}:{} {}".format(partial, str(st), str(end), str(result)))
                elif self.stream_mode == "clear1":
                    result = json.dumps(result, ensure_ascii=False, encoding='utf-8')
                    logging.info("concat words: partial={} {}:{} {}".format(partial, str(st), str(end), str(result)))

    def wait_wsclose(self, timeout=6000):
        self.final_hyp_queue.get(timeout)
        return self.result

    def closed(self, code, reason=None):
        #logging.info("sended_byte_sum={}".format(self.sended_byte_sum))
        # print "Websocket closed() called"
        # print >> sys.stderr
        self.final_hyp_queue.put(" ".join(self.final_hyps))
