from intcode import IntCodeProgram
import time
import queue
from threading import Thread

class IntCodeNetwork:
    def __init__(self, program, nodes):
        self.program = program
        self.nodes = nodes
        self._nodes = []
        self._started = False
        self._killed = False
        self._node_queues = {}
        self._global_queue = queue.Queue()

    def start(self):
        assert not self._started
        for node in range(self.nodes):
            t = Thread(target=self._node_loop, args=(node,))
            t.daemon = True
            self._node_queues[node] = queue.Queue()
            t.start()
            self._nodes.append(t)

    def stop(self):
        self._killed = True
        for node in self._nodes:
            node.join()

    def _node_loop(self, node_addr):
        process = self.program.process()
        process.send(node_addr)
        input_queue = self._node_queues[node_addr]
        output_queue = self._global_queue
        while not self._killed:
            process.step_until_interrupt()
            if process.waiting_for_input():
                try:
                    _, x, y = input_queue.get(timeout=0.001)
                    process.send(x)
                    process.send(y)
                except queue.Empty:
                    process.send(-1)
            elif process.waiting_for_output():
                addr = process.recv()
                x = process.recv()
                y = process.recv()
                output_queue.put((addr, x, y))
            time.sleep(0)

    def run(self):
        self.start()
        try:
            while True:
                packet = self._global_queue.get()
                yield packet
                to_node = packet[0]
                if to_node < self.nodes:
                    self._node_queues[to_node].put(packet)
        finally:
            self.stop()


with open("input.txt", "r") as f:
    program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
network = IntCodeNetwork(program, 50)
for packet in network.run():
    print(packet)
    if packet[0] == 255:
        break
