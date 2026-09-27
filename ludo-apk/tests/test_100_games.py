import random

START=[0,13]
SAFE={0,7,13,14,20,26,27,33,39,40,46}
FINISH=57

def legal(pos, die):
    if pos == -1:
        return die == 6
    return pos + die <= FINISH

def play(seed):
    rng=random.Random(seed)
    pos=[[-1]*4 for _ in range(2)]
    turn=0
    rolls=0
    six_chain=0
    while rolls < 20000:
        die=rng.randint(1,6)
        rolls += 1
        legal_moves=[t for t in range(4) if legal(pos[turn][t],die)]
        if not legal_moves:
            if die != 6:
                turn=1-turn
                six_chain=0
            else:
                six_chain += 1
                if six_chain >= 3:
                    turn=1-turn
                    six_chain=0
            continue
        t=legal_moves[(rolls + turn) % len(legal_moves)]
        if pos[turn][t] == -1:
            pos[turn][t]=0
        else:
            pos[turn][t]+=die
        if 0 <= pos[turn][t] < 52:
            idx=(START[turn]+pos[turn][t])%52
            if idx not in SAFE:
                for ot in range(4):
                    op=pos[1-turn][ot]
                    if 0 <= op < 52 and (START[1-turn]+op)%52 == idx:
                        pos[1-turn][ot]=-1
        if all(x == FINISH for x in pos[turn]):
            return rolls, turn
        if die != 6:
            turn=1-turn
            six_chain=0
        else:
            six_chain += 1
            if six_chain >= 3:
                turn=1-turn
                six_chain=0
    raise AssertionError("game did not finish")

results=[play(i) for i in range(100)]
assert len(results)==100
assert all(winner in (0,1) for _,winner in results)
print("100/100 deterministic Ludo games completed successfully")
print("max rolls:", max(r for r,_ in results))
print("min rolls:", min(r for r,_ in results))
