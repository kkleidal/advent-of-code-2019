import numpy as np

def cache(fn):
    _cache = {}
    def wrap(*args):
        args = tuple(args)
        if args not in _cache:
            _cache[args] = fn(*args)
        return _cache[args]
    return wrap

@cache
def make_matrix(N, offset):
    mat = np.zeros([N, N], dtype=np.int32)
    pattern = [0, 1, 0, -1]
    for i in range(N):
        for j in range(N):
            idx = (j + 1) // (i + 1) + 1 + offset
            idx -= 1
            idx %= 4
            mat[i, j] = pattern[idx]
    return mat

@cache
def make_phase_freq(N):
    return np.fft.fft(np.array([0, 1, 0, -1]), n=N)

def naieve_fft_phase(inputs, offset=0):
    mat = make_matrix(len(inputs), offset)
    out = np.squeeze(np.abs(mat @ np.expand_dims(inputs, 1)) % 10, 1)
    return out

def naieve_fft(inputs, phases):
    signal = np.array(inputs)
    for _ in range(phases):
        signal = naieve_fft_phase(signal)
    return signal

def recurse(indices, inputs, offset=0):
    if indices.shape[0] == 4:
        [0, 1, 0, -1]
        return naieve_fft_phase(inputs, offset)
    even_indices = indices[::2]
    even = inputs[::2]
    odd_indices = indices[1::2]
    odd = inputs[1::2]
    print(even, odd)
    even_results = recurse(even_indices, even, offset=offset)
    odd_results = recurse(odd_indices, odd, offset=offset+1)
    print(even_results, odd_results)
    import pdb
    pdb.set_trace()
    raise NotImplementedError

def adapt(x):
    return np.abs(x) % 10

class SmartSummer:
    def __init__(self, inputs):
        self.inputs = inputs
        self.N = inputs.shape[0]
        self.cache = {}

    def _sum(self, offset, period):
        if offset >= self.N:
            return 0
        if period >= self.N >> 3:
            return self.inputs[offset::period].sum()
        else:
            #current = self.inputs[offset]
            #current += self.sum(offset + period, 2 * period)
            current = self.sum(offset, 2 * period)
            current += self.sum(offset + period, 2 * period)
            return current

    def sum(self, offset, period):
        if (offset, period) in self.cache:
            return self.cache[(offset, period)]
        out = self._sum(offset, period)
        self.cache[(offset, period)] = out
        return out

def smart_fft_phase(inputs):
    s = SmartSummer(inputs)
    N = inputs.shape[0]
    out_signal = np.zeros(N, dtype=inputs.dtype)
    for level in range(N):
        print(level)
        out = 0
        period = (level + 1) * 4
        for i in range(level+1):
            out += s.sum(level + i, period) - s.sum(3 * level + 2 + i, period)
        out_signal[level] = adapt(out)
    return out_signal

def smart_fft(inputs, phases):
    signal = np.array(inputs)
    for i in range(phases):
        print(i)
        signal = smart_fft_phase(signal)
    return signal

def run_part2(input_string):
    input_string = input_string * 10000
    input_sequence = np.array([int(c) for c in input_string])
    answer_offset = "".join(map(str, input_sequence[:7].tolist()))
    signal = smart_fft(input_sequence, 100)
    return "".join(map(str, signal[answer_offset:answer_offset+8].tolist()))
