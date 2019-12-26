#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

typedef int64_t int_t;

typedef struct {
  size_t size;
  int_t data[0];
} Signal;

static inline Signal* Signal_empty(size_t N) {
  Signal* signal = (Signal*) malloc(sizeof(Signal) + sizeof(int_t) * N);
  signal->size = N;
  return signal;
}

static Signal* Signal_parse(FILE* file) {
  fseek(file, 0L, SEEK_END);
  size_t size = ftell(file);
  fseek(file, 0L, 0L);

  Signal* signal = Signal_empty(size);
  signal->size = 0;
  char c;
  while (1) {
    c = (char)fgetc(file);
    if (c == EOF) {
      break;
    } else if (c >= '0' && c <= '9') {
      signal->data[signal->size++] = (int_t)(c - '0');
    } else {
      continue;
    }
  }
  return signal;
}

static inline Signal* Signal_zeros(size_t N) {
  Signal* signal = Signal_empty(N);
  memset((void*) signal->data, 0, sizeof(int_t) * N);
  return signal;
}

static Signal* Signal_repeat(const Signal* original, size_t repetitions) {
  size_t Nold = original->size;
  size_t Nnew = Nold * repetitions;
  Signal* new_signal = Signal_empty(Nnew);
  for (size_t i = 0; i < Nnew; i += Nold) {
    memcpy((void*)(new_signal->data + i), (void*)original->data, Nold * sizeof(int_t));
  }
  return new_signal;
}

static uint64_t Signal_slice_as_integer(const Signal* signal, size_t offset, size_t length) {
  const int_t* data = signal->data;

  uint64_t value = 0;
  for (size_t i = offset; i < offset + length; ++i) {
    value = (value * 10) + (uint64_t)data[i];
  }
  return value;
}

static int Signal_cumsum(const Signal* restrict src, Signal* restrict dest) {
  if (src->size != dest->size) {
    return 0;
  }

  size_t N = src->size;
  const int_t* src_buf = src->data;
  int_t* dest_buf = dest->data;

  int_t cumsum = 0;
  for (size_t i = 0; i < N; ++i) {
    cumsum = cumsum + src_buf[i];
    dest_buf[i] = cumsum;
  }
  return 1;
}

static inline void Signal_free(Signal* signal) {
  free(signal);
}

static void Signal_print(const Signal* signal, int commas) {
  for (size_t i = 0; i < signal->size; ++i) {
    if (commas && i > 0) {
      printf(",");
    }
    printf("%lld", (long long int)signal->data[i]);
  }
}

int_t sum_periodic_ones(Signal* cumsum, size_t offset, size_t run_length, size_t period) {
  size_t N = cumsum->size;
  size_t pos = offset;
  int_t sum = 0;
  if (pos == 0) {
    sum = cumsum->data[pos + run_length - 1];
    pos += period;
  }
  for (; pos + run_length <= N; pos += period) {
    sum += cumsum->data[pos + run_length - 1] - cumsum->data[pos - 1];
  }
  if (pos < N) {
    sum += cumsum->data[N - 1] - cumsum->data[pos - 1];
  }
  return sum;
}

static inline int_t one_digit(int_t x) {
  if (x < 0) {
    x = -x;
  }
  return x % 10;
}

static void my_fft_phase(Signal* signal, Signal* cumsum) {
  Signal_cumsum(signal, cumsum);
  size_t N = signal->size;

  for (size_t level = 0; level < N; ++level) {
    size_t offset = -1;
    size_t run_length = level + 1;
    size_t period = run_length * 4;

    // TODO: only ones digit
    signal->data[level] = one_digit(
        sum_periodic_ones(cumsum, offset + run_length, run_length, period)
        - sum_periodic_ones(cumsum, offset + 3 * run_length, run_length, period));
  }
}

static void my_fft(Signal* signal, size_t phases, int verbose) {
  Signal* cumsum = Signal_empty(signal->size);
  for (size_t phase = 0; phase < phases; ++phase) {
    if (verbose) {
      printf("Phase: %ld / %ld\n", phase, phases);
    }
    my_fft_phase(signal, cumsum);
  }
}

typedef struct {
  size_t rounds;
  const char* filepath;
  int flags;
} args_t;

#define FLAG_REPEAT_INPUT (0x1)
#define FLAG_VERBOSE (0x2)

static void print_usage(int argc, const char** argv) {
  fprintf(stderr, "Usage: %s [-t ROUNDS] [-r] [-v] INPUT_FILE\n"
                  "  INPUT_FILE: path to the input file containing the initial signal\n"
                  "  Options:\n"
                  "    -r : Repeat the input 10,000 times\n"
                  "    -t ROUNDS : Perform FFT ROUNDS times\n"
                  "    -v : verbose\n",
                  argv[0]);
}

static int parse_args(int argc, const char** argv, args_t* args) {
  args->rounds = 100;
  args->filepath = NULL;
  args->flags = 0;
  
  const char** pos = argv + 1;
  const char** end = argv + argc;
  const char* current;
  while (pos != end) {
    current = *pos;
    switch (current[0]) {
      case '-':
        switch (current[1]) {
          case 't':
            if (pos + 1 == end) {
              return 0;
            }
            args->rounds = (size_t) atoi(*(pos+1));
            pos++;
            break;
          case 'r':
            args->flags |= FLAG_REPEAT_INPUT;
            break;
          case 'v':
            args->flags |= FLAG_VERBOSE;
            break;
          default:
            return 0;
        }
        break;
      default:
        args->filepath = current;
        break;
    }
    pos++;
  }
  if (args->filepath == NULL) {
    return 0;
  }
  return 1;
}

int main(int argc, const char** argv) {
  args_t args;
  if (!parse_args(argc, argv, &args)) {
    print_usage(argc, argv);
    return 1;
  }
  FILE* file = fopen(args.filepath, "r");
  if (!file) {
    fprintf(stderr, "File %s does not exist\n", args.filepath);
    return 1;
  }
  Signal* signal = Signal_parse(file);
  fclose(file);

  if (args.flags & FLAG_REPEAT_INPUT) {
    Signal* long_signal = Signal_repeat(signal, 10000);
    size_t offset = (size_t) Signal_slice_as_integer(long_signal, 0, 7);
    if (args.flags & FLAG_VERBOSE) {
      printf("Offset: %zu\n", offset);
    }
    if (offset >= long_signal->size) {
      fprintf(stderr, "ERROR: offset is too large for signal.\n");
      Signal_free(long_signal);
      Signal_free(signal);
      return 1;
    }
    my_fft(long_signal, args.rounds, args.flags & FLAG_VERBOSE);
    uint64_t result = Signal_slice_as_integer(long_signal, offset, 8);
    Signal_free(long_signal);
    printf("%lu\n", result);
  } else {
    my_fft(signal, args.rounds, args.flags & FLAG_VERBOSE);
    Signal_print(signal, 0);
    printf("\n");
  }

  Signal_free(signal);
}
