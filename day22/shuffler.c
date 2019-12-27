#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define OP_DEAL_INTO (1)
#define OP_CUT       (2)
#define OP_DEAL_INCR (3)

typedef uint64_t card_t;

typedef struct {
  int16_t arg;
  uint8_t  op;
} Instruction;

typedef struct {
  size_t N;
  Instruction instructions[0];
} Instructions;

typedef struct {
  size_t N;
  card_t cards[0];
} Deck;

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

static Deck* Deck_new(size_t N) {
  Deck* deck = (Deck*) malloc(sizeof(Deck) + sizeof(card_t) * N);
  if (deck == 0) {
    printf("Not enough memory, malloc failed :(\n");
    exit(1);
  }
  deck->N = N;
  for (size_t i = 0; i < N; ++i) {
    deck->cards[i] = i;
  }
  return deck;
}

static void Deck_print(Deck* deck) {
  for (size_t i = 0; i < deck->N; ++i) {
    printf("%lu ", deck->cards[i]);
  }
  printf("\n");
}

static inline void Deck_free(Deck* deck) {
  free(deck);
}

static void card_reverse(card_t* left, card_t* right) {
  card_t temp;
  for (; left < right; ++left, --right) {
    temp = *left;
    *left = *right;
    *right = temp;
  }
}

static inline void Deck_reverse(Deck* deck) {
  card_reverse(deck->cards, deck->cards + deck->N - 1);
}

static void Deck_cut(Deck* deck, int16_t cut) {
  if (cut < 0) {
    cut = deck->N + cut;
  }

  card_t* left = deck->cards;
  card_t* mid = deck->cards + cut;
  card_t* right = deck->cards + deck->N - 1;

  card_reverse(left, mid - 1);
  card_reverse(mid, right);
  card_reverse(left, right);
}

static void Deck_copy_into(const Deck* restrict deck, Deck* restrict temp_deck) {
  memcpy(temp_deck->cards, deck->cards, sizeof(card_t) * deck->N);
}

static void Deck_deal_with_increment(Deck* restrict deck, card_t incr, Deck* restrict temp_deck) {
  Deck_copy_into(deck, temp_deck);
  size_t pos_new = 0;
  size_t N = deck->N;
  size_t pos_old;

  card_t* old_deck = temp_deck->cards;
  card_t* new_deck = deck->cards;

  for (pos_old = 0; pos_old < N; ++pos_old) {
    new_deck[pos_new] = old_deck[pos_old];
    pos_new = (pos_new + incr) % N;
  }
}

static void Instructions_shuffle(const Instructions* instructions, Deck* deck, size_t times) {
  const Instruction* instr;
  Deck* temp_deck = Deck_new(deck->N);
  for (size_t t = 0; t < times; ++t) {
    printf("%lu / %lu times\n", t, times);
    instr = instructions->instructions;
    for (size_t i = 0; i < instructions->N; ++i, ++instr) {
      switch (instr->op) {
        case OP_DEAL_INTO:
          Deck_reverse(deck);
          break;
        case OP_CUT:
          Deck_cut(deck, instr->arg);
          break;
        case OP_DEAL_INCR:
          Deck_deal_with_increment(deck, instr->arg, temp_deck);
          break;
      }
    }
  }
  Deck_free(temp_deck);
}

int main(int argc, const char** argv) {
  FILE* fp = fopen(argv[1], "r");
  size_t deck_size = atoi(argv[2]);
  size_t times = atoi(argv[3]);
  Deck* deck = Deck_new(deck_size);
  Instructions* instructions = Instructions_parse(fp);
  if (deck_size < 10000) {
    Deck_print(deck);
  }
  Instructions_print(instructions);

  // TODO: shuffle
  Instructions_shuffle(instructions, deck, times);

  if (deck_size < 10000) {
    Deck_print(deck);
  }

  if (deck->N >= 10007) {
    for (size_t i = 0; i < deck->N; ++i) {
      if (deck->cards[i] == 2019) {
        printf("Card 2019 is located at position %lu\n", i);
      }
      if (deck->cards[i] == 2020) {
        printf("Card 2020 is located at position %lu\n", i);
      }
    }
  }
  Instructions_free(instructions);
  Deck_free(deck);
  fclose(fp);
}
