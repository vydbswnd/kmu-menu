# -*- coding: utf-8 -*-
"""
일회성 마이그레이션: 기존 menus.json에 쌓인 데이터를 월별 archive/YYYY-MM.json으로 옮긴다.
데이터 유실이 없는지(아이템 수/날짜 집합 일치) 검증한다. menus.json 자체는 건드리지 않는다.
(이후 크롤러가 archive에서 menus.json을 최근 3주치로 재생성한다.)

실행: python migrate_to_archive.py
"""

import kmu_crawler as k


def count_items(restaurants):
    return sum(len(m["items"]) for r in restaurants for m in r["menus"])


def date_set(restaurants):
    return {m["date"] for r in restaurants for m in r["menus"]}


def main():
    before = k.load_existing_restaurants(k.MENUS_FILE)
    if not before:
        print("menus.json에 데이터가 없어 마이그레이션할 것이 없습니다.")
        return

    before_items = count_items(before)
    before_dates = date_set(before)
    lo, hi = min(before_dates), max(before_dates)
    print(f"[전] menus.json: 아이템 {before_items}개, 날짜 {len(before_dates)}일 ({lo}~{hi})")

    touched = k.merge_into_archives(before)

    # 검증: 옮긴 뒤 archive들의 합집합이 원본을 온전히 담고 있는지
    after_dates = set()
    after_items = 0
    for ym in sorted(touched):
        rs = k.load_archive(ym)
        after_items += count_items(rs)
        after_dates |= date_set(rs)
    print(f"[후] archive {sorted(touched)}: 아이템 {after_items}개, 날짜 {len(after_dates)}일")

    assert before_dates <= after_dates, "날짜 유실 발생!"
    assert after_items == before_items, f"아이템 수 불일치! {before_items} != {after_items}"
    print("✅ 무손실 마이그레이션 확인 (아이템 수 일치, 날짜 집합 보존)")


if __name__ == "__main__":
    main()
