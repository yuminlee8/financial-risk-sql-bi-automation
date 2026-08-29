# Lending Club 대출 데이터 SQL 분석

## 사용 데이터
- All Lending Club loan data (Kaggle)
- DuckDB + jupysql로 분석 진행

## Q1. 전체 대출 중 부실률은 몇 %인가?

​```sql
SELECT 
    CAST(SUM(CASE WHEN loan_status IN ('Charged Off', 'Default', ...)
        THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) * 100 AS bad_rate
FROM loan_clean;
​```

**해석**
- 전체 대출 중 11.91%가 부실(Charged Off/Default)로 종결됨
- Lending Club 업계 평균(10~15%)과 비슷한 수준으로, 계산이 합리적임을 확인
- 다음 질문에서 이 부실률이 신용등급별로 어떻게 나뉘는지 확인할 예정

## Q2. 신용등급별 부실률은 어떻게 다른가?

​```sql
SELECT 
    grade,
    CAST(SUM(CASE WHEN loan_status IN ('Charged Off', 'Default', 'Does not meet the credit policy. Status:Charged Off')
            THEN 1 ELSE 0 END) AS DOUBLE)
    / COUNT(*) * 100 AS bad_rate,
    COUNT(*) AS total_cnt
FROM loan
GROUP BY grade
ORDER BY grade;
​```

**해석**
- 신용등급이 낮아질수록 부실률이 높아지는 것으로 확인됨 (A등급의 부실률->3.28%, G등급의 부실률->38.06%)
- 부실률과 반대로 등급별 대출건수는 상위 등급(A~D)일수록 많은 것으로 확인됨 (A~D등급의 대출건수->32만~66만 건, E~G등급의 대출건수->1만~13만 건)

## Q3. 신용등급별 부실률은 대출 실행 시기에 따라 어떻게 변하는가?
​```sql
SELECT grade,
    CAST(SUM(CASE WHEN loan_status IN ('Charged Off', 'Default', 
        'Does not meet the credit policy. Status:Charged Off')
            THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) * 100 AS bad_rate,
    CAST(DATE_TRUNC('month', STRPTIME(issue_d, '%b-%Y')) AS DATE) AS issue_month,
    COUNT(*) AS count_issue
FROM loan_clean
GROUP BY issue_month, grade
ORDER BY grade, issue_month;
​```

쿼리 결과를 pandas로 받아 등급별 시계열 그래프로 시각화:
![등급별 부실률 추이](images/grade_bad_rate_trend.png)

**해석**
- 신용등급이 낮을수록 부실률 추이 불안정성 심화 
- 신용등급이 높을수록 부실률 수준 낮음, 추이도 안정성을 보임: A등급은 10% 안팎, G등급은 20~50%대를 오가는 불안정성 추이
- 2016년 이후 부실률이 하락하는 것처럼 보이나, 이는 실제 리스크 개선이 아니라 **관찰 기간 편향(observation bias)**일 가능성이 높음: 최근에 발행된 대출은 아직 상환 기간(36/60개월)이 끝나지 않아 부실이 발생할 시간 자체가 부족했기 때문. 따라서 최근 코호트의 낮은 부실률을 "리스크가 개선됐다"고 해석하면 안 되며, 상환 기간이 충분히 지난 2007~2015년 코호트끼리만 비교하는 것이 더 정확함
- 2007~2010년 초반 극단값 존재: 건수 자체가 적어서 몇 건의 부실률이 튀게 나타나는 현상일 가능성 존재

## 추후 추가 예정: 퍼널 / 윈도우함수 / RFM