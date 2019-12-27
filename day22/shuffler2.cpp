#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <unordered_set>
#include <vector>

using namespace std;

#define OP_DEAL_INTO (1)
#define OP_CUT       (2)
#define OP_DEAL_INCR (3)

typedef int64_t card_t;

typedef struct {
  int16_t arg;
  uint8_t  op;
} Instruction;

typedef struct {
  size_t N;
  Instruction instructions[0];
} Instructions;

static inline int string_startswith(const char *str, const char *pre) {
    return strncmp(pre, str, strlen(pre)) == 0;
}

static Instructions* Instructions_parse(FILE* fp) {
  char line[64];
  char *pos;
  size_t N, i;
  Instructions* instructions;
  char c;

  fseek(fp, 0L, 0L);
  N = 0;
  while (1) {
    c = fgetc(fp);
    switch (c) {
      case EOF:
        goto end_loop1;
      case '\n':
        ++N;
        break;
    }
  }
end_loop1:

  instructions = (Instructions*) malloc(sizeof(Instructions) + N * sizeof(Instruction));
  instructions->N = N;

  fseek(fp, 0L, 0L);
  for (i = 0; i < N; ++i) {
    pos = line;
    while (1) {
      c = fgetc(fp);
      if (c == '\n' || c == EOF) {
        *pos = '\0';
        break;
      } else {
        *(pos++) = c;
      }
    }

    if (string_startswith(line, "deal into")) {
      instructions->instructions[i].op = OP_DEAL_INTO;
      instructions->instructions[i].arg = 0;
    } else if (string_startswith(line, "deal with")) {
      instructions->instructions[i].op = OP_DEAL_INCR;
      instructions->instructions[i].arg = atoi(line + 20);
    } else {
      instructions->instructions[i].op = OP_CUT;
      instructions->instructions[i].arg = atoi(line + 4);
    }
  }

  return instructions;
}

static void Instructions_print(const Instructions* instructions) {
  for (size_t i = 0; i < instructions->N; ++i) {
    uint8_t opcode = instructions->instructions[i].op;
    int16_t arg = instructions->instructions[i].arg;
    switch (opcode) {
      case OP_DEAL_INTO:
        printf("deal into new stack\n");
        break;
      case OP_DEAL_INCR:
        printf("deal with increment %d\n", arg);
        break;
      case OP_CUT:
        printf("cut %d\n", arg);
        break;
      default:
        printf("WARNING: unsupported opcode: %d\n", opcode);
    }
  }
}

static inline void Instructions_free(Instructions* instructions) {
  free(instructions);
}

static inline card_t Deck_reverse(card_t deck_size, card_t card_of_interest) {
  // 4 3 -> 0
  // 4 0 -> 3
  // 4 1 -> 2
  // 4 2 -> 1

  // 5 4 -> 0
  // 5 0 -> 4
  // 5 3 -> 1
  // 5 1 -> 3
  // 5 2 -> 2
  card_t mid = deck_size / 2;
  if (card_of_interest >= mid) {
    return mid - (card_of_interest - mid) - (1 - (deck_size % 2));
  } else {
    return mid + (mid - card_of_interest) - (1 - (deck_size % 2));
  }
}

static inline card_t Deck_cut(card_t deck_size, card_t cut, card_t card_of_interest) {
  if (cut < 0) {
    cut = deck_size + cut;
  }
  
  if (card_of_interest < cut) {
    return card_of_interest - cut + deck_size;
  } else {
    return card_of_interest - cut;
  }
}

static inline card_t Deck_deal_with_increment(card_t deck_size, card_t incr, card_t card_of_interest) {
  return ((incr % deck_size) * (card_of_interest % deck_size)) % deck_size;
}

// 57939487424420
// Expected: 49034037480993

static card_t Instructions_shuffle(const Instructions* instructions, size_t deck_size, size_t times, card_t card_pos) {
  const Instruction* instr;
// #ifdef SHORTCUT
//   unordered_set<size_t> positions;
// #endif
  for (size_t t = 0; t < times; ++t) {
    if (t % 100000 == 0) {
      printf("%lu / %lu times\n", t, times);
    }
    instr = instructions->instructions;
    for (size_t i = 0; i < instructions->N; ++i, ++instr) {
// #ifdef SHORTCUT
//       size_t key = card_pos * instructions->N + i;
//       if (positions.count(key) == 0) {
//         positions.insert(key);
//         // ordered_positions.push_back(card_pos);
//       } else {
//         printf("Repeat at time %lu, instruction %lu\n", t, i);
//         exit(1);
//         // size_t pos = 0;
//         // for (size_t index = 0; index < ordered_positions.size(); ++index) {
//         //   if (ordered_positions[index] == card_pos) {
//         //     pos = index;
//         //     break;
//         //   }
//         // }
//         // size_t offset = pos;
//         // size_t period = t - offset;
//         // size_t T = times;
//         // return ordered_positions[(T - offset) % period + offset];
//       }
// #endif
      switch (instr->op) {
        case OP_DEAL_INTO:
          card_pos = Deck_reverse(deck_size, card_pos);
          break;
        case OP_CUT:
          card_pos = Deck_cut(deck_size, instr->arg, card_pos);
          break;
        case OP_DEAL_INCR:
          card_pos = Deck_deal_with_increment(deck_size, instr->arg, card_pos);
          break;
      }
    }
  }
  return card_pos;
}

int main(int argc, const char** argv) {
  FILE* fp = fopen(argv[1], "r");
  size_t deck_size = atol(argv[2]);
  size_t times = atol(argv[3]);
  printf("Deck size: %lu\n", deck_size);
  printf("Times: %lu\n", times);
  card_t card_of_interest = atol(argv[4]);

  Instructions* instructions = Instructions_parse(fp);
  Instructions_print(instructions);

  card_of_interest = Instructions_shuffle(instructions, deck_size, times, card_of_interest);
  printf("Card position: %lu\n", card_of_interest);

  Instructions_free(instructions);
  fclose(fp);
}
