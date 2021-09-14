# coding:utf-8
__author__ = 'tanel'

import json
import sys
import threading
import time
from ws4py.client.threadedclient import WebSocketClient

if "2.7" in str(sys.version):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    import Queue
else:
    from queue import Queue


def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

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
        self.audiofile = audiofile
        self.byterate = byterate
        self.lang = lang
        self.stream_mode = stream_mode
        self.final_hyp_queue = Queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.semp = threading.Semaphore(30)
        self.result = []
        self.booked_words = booked_words

    @rate_limited(5)
    def send_data(self, data):
        # self.semp.acquire()
        self.send(data, binary=True)
        # print('datasent', len(data))
        sys.stdout.flush()

    def opened(self):
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
            header = '{"lang":"%s","booked_words":"%s"}' % (self.lang, self.booked_words)
            # header = '{"lang":"%s"}' % self.lang

            self.send(header)
            # print('sending header: header= ', header)
            with open(self.audiofile, "rb") as audiostream:
                k = 0
                for block in iter(lambda: audiostream.read(self.byterate/5), ""):
                    # print 'sending',self.byterate/20
                    self.send_data(block)
                    # sys.exit(0)
            # print >> sys.stderr, "Audio sent, now sending YOUDAO_ASR_EOS"
            self.send("ASR_EOS")

        t = threading.Thread(target=send_data_to_ws)
        t.start()

    def received_message(self, m):
        self.result.append(str(m))
        if self.stream_mode == "pass":
            pass
        elif self.stream_mode == "full":
            # self.semp.release()
            print >> sys.stderr, 'received', str(m)
        else:
            data = json.loads(str(m))
            if 'text' in data:
                s = data['text']
                if len(s) == 0: return
                a = json.loads(s)
                if len(a) == 0: return
                if 'partial' in a[0] and a[0]['partial'] is False:
                    st = a[0]['word_timestamps'][0]
                    et = a[0]['word_timestamps_eds'][-1]
                    if self.lang == "en":
                        result = " ".join(a[0]['words'])
                    else:
                        result = "".join(a[0]['words'])
                    print >> sys.stderr, "sentence: ", str(st) + ':' + str(et), a[0]['sentence']
                    print >> sys.stderr, "concat words: ", str(st) + ':' + str(et), result

    def get_full_hyp(self, timeout=60):
        self.final_hyp_queue.get(timeout)
        return self.result

    def closed(self, code, reason=None):
        # print "Websocket closed() called"
        # print >> sys.stderr
        self.final_hyp_queue.put(" ".join(self.final_hyps))