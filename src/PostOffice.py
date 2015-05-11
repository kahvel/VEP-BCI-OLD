__author__ = 'Anti'

import random
import numpy as np
import constants as c
from connections import MasterConnection, ConnectionPostOfficeEnd
import winsound


class PostOffice(object):
    def __init__(self):
        self.main_connection = ConnectionPostOfficeEnd.MainConnection()
        self.connections = MasterConnection.MasterConnection()
        self.options = None
        self.results = None
        self.resetResults()
        self.standby_state = None
        self.standby_freq = None
        self.no_standby = None
        self.recorded_signals = [None for _ in range(7)]
        self.prev_results = []
        self.waitConnections()

    def waitConnections(self):
        setup_successful = False
        message = None
        while True:
            if message is not None:
                if message == c.START_MESSAGE:
                    if setup_successful:
                        message = self.start()
                        continue
                    else:
                        print("Setup was not successful!")
                elif message == c.SETUP_MESSAGE:
                    if self.setup() == c.SUCCESS_MESSAGE:
                        setup_successful = True
                        print("Setup successful!")
                    else:
                        setup_successful = False
                        print("Setup failed!")
                elif message == c.STOP_MESSAGE:
                    print("Stop PostOffice")
                elif message == "Threshold":
                    self.calculateThreshold()
                elif message == "Record neutral":
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv(), self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
                elif message == "Record target":
                    self.sendMessage(self.psychopy_connection, "Start")
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.psychopy_connection, self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Start")
                    self.recordSignal(self.main_connection.recv(), self.main_connection.recv())
                    self.sendMessage(self.emotiv_connection, "Stop")
                    self.sendMessage(self.psychopy_connection, "Stop")
                elif message == c.RESET_RESULTS_MESSAGE:
                    self.resetResults()
                elif message == c.SHOW_RESULTS_MESSAGE:
                    self.printResults()
                elif message == c.SAVE_RESULTS_MESSAGE:
                    self.saveResults()
                elif message == c.EXIT_MESSAGE:
                    self.exit()
                    return
                else:
                    print("Unknown message in PostOffice: " + str(message))
            message = self.main_connection.receiveMessagePoll(0.1)

    def countFreqs(self, freqs, cca=False):
        result = {}
        for tab in freqs:
            if freqs[tab] not in result:
                result[freqs[tab]] = 1 if cca is False else 8
            else:
                result[freqs[tab]] += 1 if cca is False else 8
        return result

    def countAllFreqs(self, *freqs_dicts):
        result = {}
        for dict in freqs_dicts:
            for freq in dict:
                if round(freq, 2) not in result:
                    result[round(freq, 2)] = dict[freq]
                else:
                    result[round(freq, 2)] += dict[freq]
        return result

    def getResults(self, results, current_target, method):
        wrong = []
        correct = []
        all_results, max_freqs = results[:2]
        if max_freqs != {}:
            freq = max_freqs.values()[0]
            if freq == current_target:
                correct.append((method, freq))
            else:
                wrong.append((method, freq))
        return correct, wrong

    def getSumPsdaResults(self, results, current_target, method):
        return {key: self.getResults(results[key], current_target, method) for key in results}

    def getPsdaResults(self, results, current_target, method):
        return {key: self.getSumPsdaResults(results[key], current_target, method) for key in results}

    def findCorrectResults(self, results, target_freqs):
        result = self.countAllFreqs(
            self.countFreqs(results[c.CCA][1], cca=True),
            self.countFreqs(results[c.SUM_PSDA][1][1] if 1 in results[c.SUM_PSDA] else {}),
            self.countFreqs(results[c.SUM_PSDA][2][1] if 2 in results[c.SUM_PSDA] else {}),
            self.countFreqs(results[c.SUM_PSDA][3][1] if 3 in results[c.SUM_PSDA] else {}),
            self.countFreqs(results[c.SUM_PSDA][c.RESULT_SUM][1] if c.RESULT_SUM in results[c.SUM_PSDA] else {}),
            self.countFreqs(results[c.PSDA]["O1"][1][1] if "O1" in results[c.PSDA] and 1 in results[c.PSDA]["O1"] else {}),
            self.countFreqs(results[c.PSDA]["O1"][2][1] if "O1" in results[c.PSDA] and 2 in results[c.PSDA]["O1"] else {}),
            self.countFreqs(results[c.PSDA]["O1"][3][1] if "O1" in results[c.PSDA] and 3 in results[c.PSDA]["O1"] else {}),
            self.countFreqs(results[c.PSDA]["O1"][c.RESULT_SUM][1] if "O1" in results[c.PSDA] and c.RESULT_SUM in results[c.PSDA]["O1"] else {}),
            self.countFreqs(results[c.PSDA]["O2"][1][1] if "O2" in results[c.PSDA] and 1 in results[c.PSDA]["O2"] else {}),
            self.countFreqs(results[c.PSDA]["O2"][2][1] if "O2" in results[c.PSDA] and 2 in results[c.PSDA]["O2"] else {}),
            self.countFreqs(results[c.PSDA]["O2"][3][1] if "O2" in results[c.PSDA] and 3 in results[c.PSDA]["O2"] else {}),
            self.countFreqs(results[c.PSDA]["O2"][c.RESULT_SUM][1] if "O2" in results[c.PSDA] and c.RESULT_SUM in results[c.PSDA]["O2"] else {}),
            self.countFreqs(results[c.PSDA][c.RESULT_SUM][1][1] if c.RESULT_SUM in results[c.PSDA] and 1 in results[c.PSDA][c.RESULT_SUM] else {}),
            self.countFreqs(results[c.PSDA][c.RESULT_SUM][2][1] if c.RESULT_SUM in results[c.PSDA] and 2 in results[c.PSDA][c.RESULT_SUM] else {}),
            self.countFreqs(results[c.PSDA][c.RESULT_SUM][3][1] if c.RESULT_SUM in results[c.PSDA] and 3 in results[c.PSDA][c.RESULT_SUM] else {}),
            self.countFreqs(results[c.PSDA][c.RESULT_SUM][c.RESULT_SUM][1] if c.RESULT_SUM in results[c.PSDA] and c.RESULT_SUM in results[c.PSDA][c.RESULT_SUM] else {}),
        )
        for freq in target_freqs:
            if round(freq, 2) not in result:
                result[round(freq, 2)] = 0
        return result

    def handleFreqMessages(self, message, target_freqs, current_target):
        results = message
        rounded_target_freqs = tuple(round(freq, 2) for freq in target_freqs)
        if results is not None:
            counted_freqs = self.findCorrectResults(results, target_freqs)
            max_freq_rounded, max_count = max(counted_freqs.items(), key=lambda x: x[1])
            max_freq = target_freqs[rounded_target_freqs.index(max_freq_rounded)]
            self.prev_results.append(max_freq)
            if len(self.prev_results) > 4:
                del self.prev_results[0]
            print(counted_freqs, max_freq_rounded, max_count, self.prev_results)
            if self.prev_results.count(self.prev_results[0]) == 4:
                if max_freq == self.standby_freq:
                    # self.connections.sendPlotMessage(self.standby_state and not self.no_standby)
                    self.standby_state = not self.standby_state
                    self.connections.sendTargetMessage(self.standby_state)
                    winsound.Beep(2500, 100)
                    self.prev_results = []
                if not self.standby_state or self.no_standby:
                    self.connections.sendTargetMessage(max_freq)
                    # self.connections.sendGameMessage(max_freq)

    def resetResults(self):
        self.results = {name: {} for name in c.EXTRACTION_METHOD_NAMES}

    def saveResults(self):
        pass

    def setupResults(self, target_freqs):
        for key in self.results:
            if str(target_freqs) not in self.results[key]:
                self.results[key][str(target_freqs)] = \
                    {i+1: {freq: 0 for freq in target_freqs} for i in range(len(target_freqs))}
                self.results[key][str(target_freqs)]["None"] = {freq: 0 for freq in target_freqs}

    def printResults(self):
        for method in self.results:
            print method
            for freqs in self.results[method]:
                print freqs
                for row in sorted(self.results[method][freqs]):
                    print row, self.results[method][freqs][row]

    def getTargetTime(self, time, unlimited, is_random, min, max):
        if is_random:
            return random.randint(min, max)
        else:
            return self.getTotalTime(unlimited, time)

    def getTotalTime(self, unlimited, test_time):
        return float("inf") if unlimited else test_time

    def getTarget(self, test_target, target_count):
        if self.isRandom(test_target):
            return random.randint(1, target_count)
        elif test_target != c.TEST_NONE:
            return test_target
        else:
            return None

    def isRandom(self, test_target):
        return test_target == c.TEST_RANDOM

    def targetChangingLoop(self, options, target_freqs):
        count = 0
        target_count = len(target_freqs)
        total_time = self.getTotalTime(options[c.TEST_UNLIMITED], options[c.TEST_TIME])
        while count < total_time:
            target = self.getTarget(options[c.TEST_TARGET], target_count)
            time = self.getTargetTime(
                options[c.TEST_TIME],
                options[c.TEST_UNLIMITED],
                self.isRandom(options[c.TEST_TARGET]),
                options[c.TEST_MIN],
                options[c.TEST_MAX]
            )
            if count+time > total_time:
                time = total_time-count
            count += time
            print(time, target, total_time)
            if target is not None:
                self.connections.sendTargetMessage(target)
            message = self.startPacketSending(time, target_freqs, target)
            if message is not None:
                return message
        self.main_connection.sendMessage(c.STOP_MESSAGE)

    def setStandby(self, options):
        if self.isStandby(options[c.DATA_TEST][c.TEST_STANDBY]):
            self.no_standby = False
            self.standby_freq = options[c.DATA_FREQS][options[c.DATA_TEST][c.TEST_STANDBY]-1]
        else:
            self.no_standby = True
        self.standby_state = False

    def setup(self):
        self.options = self.main_connection.receiveMessageBlock()
        self.connections.setup(self.options)
        self.setStandby(self.options)
        if self.connections.setupSuccessful():
            self.setupResults(self.options[c.DATA_FREQS])
            return c.SUCCESS_MESSAGE
        else:
            return c.FAIL_MESSAGE

    def exit(self):
        self.connections.close()
        self.main_connection.close()

    def isStandby(self, standby):
        if standby == c.TEST_NONE:
            return False
        else:
            return True

    def start(self):
        self.connections.sendStartMessage()
        message = self.targetChangingLoop(
            self.options[c.DATA_TEST],
            self.options[c.DATA_FREQS],
        )
        self.connections.sendStopMessage()
        return message

    def handleEmotivMessages(self, target_freqs, current_target):
        message = self.connections.receiveEmotivMessage()
        if message is not None:
            self.connections.sendExtractionMessage(message)
            self.connections.sendPlotMessage(message)
            self.handleFreqMessages(
                self.connections.receiveExtractionMessage(),
                target_freqs,
                current_target
            )
            if not self.standby_state:
                return 1
        return 0

    def startPacketSending(self, length, target_freqs, current_target):
        count = 0
        while count < length:
            main_message = self.main_connection.receiveMessageInstant()
            if main_message is not None:
                return main_message
            count += self.handleEmotivMessages(target_freqs, current_target)
        # Wait for the last result
        # self.handleFreqMessages(
        #     self.connections[c.CONNECTION_EXTRACTION].receiveMessageBlock(),
        #     target_freqs,
        #     current_target
        # )


    # The following code currently does not work

    def calculateThreshold(self):
        target_freqs = self.main_connection.recv()
        all_results = []
        for signal in self.recorded_signals:
            if signal is not None:
                self.sendMessage(self.extraction_connection, "Start")
                self.sendMessage(self.extraction_connection, target_freqs)
                for packet in signal:
                    self.sendMessage(self.extraction_connection, packet)
                self.sendMessage(self.extraction_connection, "Stop")
                self.sendMessage(self.extraction_connection, "Results")
                while True:
                    if "Results" in self.getMessages(self.extraction_connection, "Extraction", poll=lambda connection: True):
                        break
                all_results.append(self.getMessages(self.extraction_connection, "Extraction", poll=lambda connection: True))
            else:
                all_results.append(None)
        shaped_results = []
        print "results", all_results
        index = 0
        for i in range(len(all_results)):  # target
            if all_results[i] is not None:
                for window in range(len(all_results[i])):  # window
                    if len(shaped_results) != len(all_results[i]):
                        shaped_results.append({})
                    for method in all_results[i][window]:  # method
                        print method
                        transposed_result = np.transpose(all_results[i][window][method])
                        if method not in shaped_results[window]:
                            shaped_results[window][method] = {True:  [[] for _ in range(len(transposed_result))],
                                                  False: [[] for _ in range(len(transposed_result))]}
                        for target in range(len(transposed_result)):  # target
                            if index == 0:
                                shaped_results[window][method][False][target] = np.append(shaped_results[window][method][False][target], transposed_result[target][16:], 1)
                            elif index-1 == target:
                                shaped_results[window][method][True][target] = np.append(shaped_results[window][method][True][target], transposed_result[target][16:], 1)
                            else:
                                shaped_results[window][method][False][target] = np.append(shaped_results[window][method][False][target], transposed_result[target][16:], 1)
                            print transposed_result[target]
                index += 1
        print shaped_results
        thresholds = []
        for window in shaped_results:
            thresholds.append({})
            for method in window:
                thresholds[-1][method] = {}
                for boolean in window[method]:
                    thresholds[-1][method][boolean] = []
                    for target in window[method][boolean]:
                        thresholds[-1][method][boolean].append([])
                        if len(target) != 0:
                            thresholds[-1][method][boolean][-1].append(min(target))
                            thresholds[-1][method][boolean][-1].append(sum(target)/len(target))
                            thresholds[-1][method][boolean][-1].append(max(target))
        print thresholds

    def recordSignal(self, length, target_n):
        signal = []
        while len(signal) < length:
            if self.main_connection.poll():
                message = self.main_connection.recv()
                return message
            if self.emotiv_connection[0].poll():
                message = self.emotiv_connection[0].recv()
                signal.append(message)
        self.recorded_signals[target_n] = signal

    def getMessages(self, connections, name, poll=lambda connection: connection.poll()):
        ret = []
        for i in range(len(connections)-1, -1, -1):
            if poll(connections[i]):
                message = connections[i].recv()
                if message == "Close":
                    print name, "pipe closed"
                    connections[i].close()
                    del connections[i]
                elif isinstance(message, tuple):  # elif name == "Extraction" and isinstance(message, float):
                    ret.append(message)
                else:  # elif isinstanse(message, list)
                    ret.append(message)
        return ret