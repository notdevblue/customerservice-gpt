# Player.Point 테이블

## 개요

포인트 정보 가진 테이블

## 테이블

이름 | 형식 | 태그 | 설명
---|--|--|--
Id | int64 | PK | 유저 고유 ID
Num | int | | 포인트 넘버
AccAmount | int64 | | 총 획득 수량
Amount | int | | 보유 수량
Flags | int64 | | 플레그
CreateTime | datetime | | 생성일
UpdateTime | datetime | | 수정일

## 테이블 예시

Id | Num | AccAmount | Amount | Flags | CreateTime | UpdateTime
--|--|--|--|--|--|-- 
1001 | 102 | 1000 | 300 | 0 | 2024-02-25 03:12:43 | 2024-05-25 04:32:41
1001 | 103 | 2000 | 400 | 0 | 2024-02-25 03:12:43 | 2024-05-25 03:32:41
1002 | 102 | 1000 | 300 | 0 | 2024-02-25 03:12:43 | 2024-05-25 04:32:41
