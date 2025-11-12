#Project by : Brian Lee
#2025.09.16
#Project Purpose : 학원의 월별 테스트 채점을 편하게 하기 위한 툴



LEVELS = {
    "초급": {
        "LC": [("파트1", 6, 3.0), ("파트2", 12, 3.0), ("파트3", 10, 3.0),
               ("파트4", 8, 4.0), ("파트5", 4, 4.0)],
        "RC": [("파트6", 5, 4.0), ("파트7", 5, 4.0)],
        "BASE": {"LC": 4.0, "RC": 4.0},  # 초급만 기본점수 +4
    },
    "중급": {
        "LC": [("파트1", 6, 2.0), ("파트2", 10, 2.0), ("파트3", 8, 3.0),
               ("파트4", 5, 3.0), ("파트5", 6, 3.5)],
        "RC": [("파트6", 6, 4.0), ("파트7", 6, 4.0), ("파트8", 8, 5.0)],
        "BASE": {"LC": 0.0, "RC": 0.0},
    },
    "고급": {
        "LC": [("파트1", 6, 2.0), ("파트2", 10, 2.0), ("파트3", 6, 3.0),
               ("파트4", 8, 3.0), ("파트5", 5, 3.5)],
        "RC": [("파트6", 8, 3.0), ("파트7", 7, 3.5), ("파트8", 10, 4.0)],
        "BASE": {"LC": 0.0, "RC": 0.0},
    },
}

# ====== 여기만 채워두면 됨: 정답 키 ======
ANSWER_KEYS = {
    "초급": {
        "LC": {
              "파트1": ["2","3","3","2","1","1"],
              "파트2": ["1","3","2","2","1","2","1","2","1","1","3","3"],
              "파트3": ["1","2","3","1","3","1","2","3","1","2"],
              "파트4": ["3","2","3","3","2","2","3","3"],
              "파트5": ["3","1","3","3"],
        },
        "RC": {
              "파트6": ["2","2","3","3","1"],
              "파트7": ["1","2","3","1","3"],
        },
    },
    "중급": {
        "LC": {
            "파트1": ["3", "3", "1", "1", "2", "2"],
            "파트2": ["1", "1", "2", "3", "3", "1", "1", "2", "3", "2"],
            "파트3": ["2", "1", "2", "1", "1", "3", "2", "1"],
            "파트4": ["1", "2", "3", "2", "1"],
            "파트5": ["3", "1", "1", "2", "3", "1"]
        },
        "RC": {
            "파트6": ["2", "1", "3", "1", "3", "3"],
            "파트7": ["2", "1", "3", "2", "1", "3"],
            "파트8": ["2", "2", "1", "1", "2", "1", "3", "3"]
        }
    },    
    "고급": {
        "LC": {
            "파트1": ["1","2","1","2","3","3"],
            "파트2": ["1","1","2","3","1","3","2","2","1","2"],
            "파트3": ["1","2","3","3","2","1"],
            "파트4": ["1","3","2","1","2","3","1","3"],
            "파트5": ["1","2","3","1","1"]
        },
        "RC": {
            "파트6": ["2","1","3","3","1","2","1","3"],
            "파트7": ["1","2","3","1","2","3","3"],
            "파트8": ["2","1","3","1","1","3","1","2","2","3"]
        }
    }
}
# ======================================

def parse_answers(raw, need_len):
    """공백 구분 또는 붙여쓰기 모두 허용."""
    raw = raw.strip()
    tokens = [t.upper() for t in raw.split()] if " " in raw else [ch.upper() for ch in raw if ch.isalpha()]
    return tokens if len(tokens) == need_len else None

def check_key_lengths():
    """정답 키 길이가 문항수와 맞는지 사전 점검."""
    for level, cfg in LEVELS.items():
        if level not in ANSWER_KEYS: 
            raise ValueError(f"{level} 정답 키 없음")
        for grp in ("LC", "RC"):
            for name, n, _ in cfg[grp]:
                key = ANSWER_KEYS[level][grp].get(name, None)
                if not isinstance(key, list) or len(key) != n:
                    raise ValueError(f"{level}/{grp}/{name} 정답 키 길이 오류: {len(key) if key else 0}개(필요 {n}개)")

def grade_group(cfg_points, answer_map, group_label):
    """
    한 그룹(LC/RC) 채점:
    - 학생 답 입력 → 파트별 맞힌 개수(got)를 계산
    - 그룹 점수(score)와 파트별 요약 리스트 반환
    """
    score = 0.0
    part_summaries = []  # [(파트명, got, 총문항), ...]
    for name, n, w in cfg_points:
        while True:
            s = input(f"{group_label} {name} 학생답({n}): ")
            if s.lower() in ("q","quit","exit"):
                return None, None
            stu = parse_answers(s, n)
            if stu is None:
                print("❗ 문항 수와 맞게 다시 입력")
                continue
            correct = answer_map[name]
            got = sum(1 for c, a in zip(correct, stu) if c == a)
            score += got * w
            part_summaries.append((name, got, n))
            break
    return score, part_summaries

def max_score(cfg):
    lc_max = cfg["BASE"]["LC"] + sum(n*w for _, n, w in cfg["LC"])
    rc_max = cfg["BASE"]["RC"] + sum(n*w for _, n, w in cfg["RC"])
    return lc_max, rc_max, lc_max + rc_max

def fmt(x):  # .0이면 정수처럼 표시
    return int(x) if abs(x - int(x)) < 1e-9 else round(x, 1)

def print_part_summary(group_label, parts):
    # parts: [(name, got, n), ...]
    if not parts:
        return
    joined = " | ".join(f"{name}: {got}/{n}" for name, got, n in parts)
    print(f"{group_label} 세부 → {joined}")

def main():
    print("=== 교사용 다단계 채점 툴 === (종료: q)")
    # 정답 키 길이 사전 점검
    try:
        check_key_lengths()
    except ValueError as e:
        print("⚠️ 정답 키 오류:", e)
        print("→ ANSWER_KEYS 상단에 파트별 정답을 문항수만큼 미리 채워주세요.")
        return

    while True:
        level = input("레벨 선택 (초급/중급/고급): ").strip()
        if level.lower() in ("q","quit","exit"): return
        if level not in LEVELS:
            print("❗ '초급/중급/고급' 중에서 선택"); continue

        cfg = LEVELS[level]
        keys = ANSWER_KEYS[level]
        lc_max, rc_max, total_max = max_score(cfg)

        print(f"\n[{level}] 채점 시작 — 같은 정답 키로 여러 학생 반복 채점 (종료: q)")
        while True:
            # LC
            lc = cfg["BASE"]["LC"]
            res_score, res_parts = grade_group(cfg["LC"], keys["LC"], "LC")
            if res_score is None:
                print("채점 종료\n"); break
            lc += res_score

            # RC
            rc = cfg["BASE"]["RC"]
            res_score, res_parts_rc = grade_group(cfg["RC"], keys["RC"], "RC")
            if res_score is None:
                print("채점 종료\n"); break
            rc += res_score

            total = lc + rc
            # 출력
            print("\n[결과]")
            print(f"LC: {fmt(lc)}/{fmt(lc_max)} | RC: {fmt(rc)}/{fmt(rc_max)} | 총점: {fmt(total)}/{fmt(total_max)}")
            # 파트별 정답 개수 요약
            print_part_summary("LC", res_parts)
            print_part_summary("RC", res_parts_rc)
            print()  # 빈 줄

if __name__ == "__main__":
    main()
