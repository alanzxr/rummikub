from collections import Counter
from copy import deepcopy
from functools import lru_cache
from itertools import combinations

COLORS = ['R', 'B', 'K', 'O']
NUMBERS = range(1, 14)
ICON_MAP = {'R': '🔴', 'B': '🔵', 'K': '⚫', 'O': '🟠', 'J': '🤡'}


def parse_tiles(tiles):
    c = Counter()
    for t in tiles:
        if t == 'J':
            c['J'] += 1
        else:
            c[(t[0], int(t[1:]))] += 1
    return c


def counter_key(c):
    return tuple(sorted(c.items(), key=lambda x: (x[0] == 'J', x[0])))


def generate_all_groups():
    groups = []
    for color in COLORS:
        for start in NUMBERS:
            for length in range(3, 14):
                nums = list(range(start, start + length))
                if nums[-1] > 13:
                    break
                g = Counter((color, n) for n in nums)
                groups.append(g)
    for num in NUMBERS:
        for size in (3, 4):
            for cols in combinations(COLORS, size):
                g = Counter((c, num) for c in cols)
                groups.append(g)
    return groups


ALL_GROUPS = generate_all_groups()


def can_subtract(hand, group):
    need_j = 0
    for k, v in group.items():
        if hand[k] < v:
            need_j += v - hand[k]
    return need_j <= hand.get('J', 0)


def subtract(hand, group):
    new = hand.copy()
    joker_used_as = []
    for k, v in group.items():
        have = new.get(k, 0)
        take = min(have, v)
        if take:
            new[k] -= take
            if new[k] == 0:
                del new[k]
        missing = v - take
        if missing > 0:
            new['J'] -= missing
            if new['J'] == 0:
                del new['J']
            joker_used_as.extend([k] * missing)
    return new, joker_used_as


def format_group_with_joker(group, joker_used_as, marked_tiles):
    tmp_marked_tiles = marked_tiles
    temp = Counter(group)
    joker_count = Counter(joker_used_as)
    all_cards = []
    for k, v in temp.items():
        if k == 'J':
            continue
        used_by_joker = joker_count.get(k, 0)
        real_count = v - used_by_joker
        if real_count > 0:
            all_cards.extend([k] * real_count)
    all_cards.extend(joker_used_as)
    all_cards.sort(key=lambda x: (x[1], x[0]))
    out = []
    for c, n in all_cards:
        if (c, n) in joker_used_as:
            if 'J' in tmp_marked_tiles:
                tmp_marked_tiles.remove('J')
                out.append(f"[{ICON_MAP.get('J')}  ]")
            else:
                out.append(f" {ICON_MAP.get('J')}   ")
        else:
            if f"{c}{n}" in tmp_marked_tiles:
                tmp_marked_tiles.remove(f"{c}{n}")
                out.append(f"[{ICON_MAP.get(c)}{n:2d}]")
            else:
                out.append(f" {ICON_MAP.get(c)}{n:2d} ")
    return out, tmp_marked_tiles


def solve_and_print(tiles, raw_tiles):
    hand = parse_tiles(tiles)

    @lru_cache(None)
    def dfs(state):
        hand = Counter(dict(state))
        if not hand:
            return []
        pivot = next(k for k in hand if k != 'J')
        for g in ALL_GROUPS:
            if pivot in g and can_subtract(hand, g):
                rest, jokers = subtract(hand, g)
                res = dfs(counter_key(rest))
                if res is not None:
                    return [(g, jokers)] + res
        return None
    solution = dfs(counter_key(hand))
    if solution is None:
        return False
    print("✅")
    marked_tiles = deepcopy(raw_tiles)
    for i, (g, jokers) in enumerate(solution, 1):
        out, marked_tiles = format_group_with_joker(g, jokers, marked_tiles)
        print(f"{i:2d}: {' '.join(out)}")
    return True


def all_k_subsets(lst):
    tmp_lst = lst
    res = []
    if 'J' in tmp_lst:
        tmp_lst = [x for x in tmp_lst if x != 'J']
    n = len(tmp_lst)
    for k in range(1, min(3, n + 1)):
        res.extend(combinations(tmp_lst, k))
    return res


if __name__ == "__main__":
    raw_tiles = sorted('k12 b12 r12 k4 o4 r4 k8 k9 k10 o9 o11 b6 k6 o6 r6 j j k4 k5 k6 k7 k8 r3 r4 r6 r7 b8 b9 b10 b11 k11 o11 r11 k13 b13 o13 k10 k11 k12 r10 r11 r12 r13'.upper().split())
    raw_hands = 'o4 o5 o6 k5 k7 b4 b6 b10 o1 o8 o8 o10 o10 r1 r1 r2 r5'.upper().split()
    is_valid = solve_and_print(raw_tiles + list(raw_hands), raw_tiles)
    if is_valid:
        print('ALL CLEAR !!!')
    else:
        current_tiles = raw_tiles
        current_hands = raw_hands
        print(len(raw_tiles), len(raw_hands))
        hands_2b_added = []
        while True:
            flag = False
            for selected in all_k_subsets(current_hands):
                is_valid = solve_and_print(current_tiles + list(selected), raw_tiles)
                if is_valid:
                    flag = True
                    current_tiles = current_tiles + list(selected)
                    hands_2b_added.extend(list(selected))
                    print(len(hands_2b_added), hands_2b_added)
                    for i in list(selected):
                        current_hands.remove(i)
                    break
            if flag is False:
                break
