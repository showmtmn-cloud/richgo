# PoE2DB Base Item Scraper

poe2db.tw에서 베이스 아이템 데이터를 수집하여 DB에 저장하는 스크래퍼입니다.

## ������ 파일 구조

```
poe2db_scraper/
├── scrape_poe2db.py    # 메인 스크래퍼 (이것만 사용)
├── import_to_db.py     # DB 임포트 스크립트
├── requirements.txt    # 필수 패키지
├── README.md           # 이 파일
└── data/
    └── scraped_bases.json  # 스크래핑 결과 (자동 생성)
```

## ������ 빠른 시작

### 1. 서버에 파일 업로드

```bash
# SSH 접속
ssh ubuntu@15.134.156.210

# 프로젝트 디렉토리로 이동
cd ~/poe2-profit-optimizer

# 스크래퍼 디렉토리 생성
mkdir -p scrapers/poe2db_scraper
cd scrapers/poe2db_scraper

# 파일 업로드 후 (SCP 또는 복사/붙여넣기)
```

### 2. 의존성 설치

```bash
# 가상환경 활성화
source ~/poe2-profit-optimizer/venv/bin/activate

# 패키지 설치
pip install requests beautifulsoup4 lxml sqlalchemy
```

### 3. 스크래핑 실행

```bash
# 테스트 (Body Armour INT만)
python scrape_poe2db.py --test

# 전체 방어구 + 장신구 스크래핑
python scrape_poe2db.py

# 무기 포함 전체 스크래핑
python scrape_poe2db.py --weapons
```

### 4. DB 임포트

```bash
# 스크래핑 데이터를 DB에 저장
python import_to_db.py

# 기존 데이터 삭제 후 새로 임포트
python import_to_db.py --clear
```

## ������ 수집 데이터

### 방어구 (Armour)
- Body Armour (6종: int, str, dex, str_int, str_dex, dex_int)
- Helmet (6종)
- Gloves (6종)
- Boots (6종)
- Shield (6종)

### 장신구 (Accessories)
- Ring
- Amulet
- Belt

### 무기 (Weapons) - 옵션
- One Hand Sword, Axe, Mace
- Dagger, Claw, Wand, Sceptre
- Two Hand Sword, Axe, Mace
- Staff, Warstaff, Bow, Crossbow
- Quiver, Focus

## ������ 출력 형식

`data/scraped_bases.json`:

```json
{
  "metadata": {
    "source": "poe2db.tw",
    "scraped_at": "2025-01-15T12:00:00",
    "total_items": 250,
    "by_type": {
      "Body Armour": 150,
      "Helmet": 100
    }
  },
  "items": [
    {
      "name": "Vile Robe",
      "item_type": "Body Armour",
      "item_class": "int",
      "required_level": 65,
      "required_int": 121,
      "energy_shield": 184,
      "implicit_mod": null,
      "poe2db_url": "https://poe2db.tw/us/Vile_Robe"
    }
  ]
}
```

## ⚠️ 주의사항

1. **Rate Limiting**: 스크래퍼는 0.3초 간격으로 요청합니다. 더 빠르게 하면 차단될 수 있습니다.

2. **HTML 구조 변경**: poe2db.tw의 HTML 구조가 변경되면 스크래퍼 수정이 필요할 수 있습니다.

3. **중복 체크**: DB 임포트 시 이름 기준으로 중복을 확인합니다.

## ������ 문제 해결

### 아이템이 수집되지 않는 경우

1. poe2db.tw 접속 확인
2. HTML 구조 변경 확인
3. `--test` 옵션으로 단일 페이지 테스트

### DB 임포트 오류

1. DB 경로 확인 (`poe2_profit_optimizer.db`)
2. SQLAlchemy 버전 확인
3. `--clear` 옵션으로 초기화 후 재시도

## ������ 수정 방법

아이템 이름 키워드 추가/수정:
```python
# scrape_poe2db.py의 _is_valid_item_name() 메서드
keywords = {
    "Body Armour": ["Robe", "Raiment", ...],
    ...
}
```

새 카테고리 추가:
```python
# scrape_poe2db.py의 ARMOUR_PAGES 또는 WEAPON_PAGES
ARMOUR_PAGES = {
    "New Type|class": "/New_Type_url",
    ...
}
```

## ������ 업데이트 주기

권장: 매주 1회 또는 게임 패치 후

```bash
# cron 설정 예시 (매주 월요일 새벽 3시)
0 3 * * 1 cd ~/poe2-profit-optimizer/scrapers/poe2db_scraper && python scrape_poe2db.py && python import_to_db.py --clear
```
