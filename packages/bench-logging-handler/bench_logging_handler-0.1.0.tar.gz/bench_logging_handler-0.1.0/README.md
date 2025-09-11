# Bench Logging Handler

Python 벤치마킹 로깅 핸들러로, 구조화된 로깅, 성능 측정, 자동 스택 트레이스를 제공합니다.

## 주요 기능

- **내장 벤치마킹**: `logging.benchstart()`와 `logging.benchend()`로 간편한 성능 측정 (현재는 시간 측정만 지원하며, 향후 메모리 사용량, CPU 사용률 등 다양한 벤치마크 지표를 추가할 예정) 
- **구조화된 로깅**: JSON, Line, Box 등 다양한 출력 형식 지원
- **자동 스택 트레이스**: 모든 로그 레벨에서 스택 트레이스 제공 가능
- **시스템 컨텍스트**: 시스템 정보(PID, 호스트명, Python 버전) 자동 포함
- **읽기 쉬운 포맷**: 색상과 포맷팅이 적용된 콘솔 출력
- **Logging 통합**: 표준 Python 로깅의 `handler` 대체

## 설치

```bash
pip install bench-logging-handler
```

## 빠른 시작

```python
import logging
from bench_logging_handler import BenchHandler, ConsoleSink

# 핸들러 설정
handler = BenchHandler(sink=ConsoleSink())
logging.getLogger().addHandler(handler)

# 일반 로깅
logging.info("애플리케이션이 시작되었습니다")

# 벤치마킹
bench_id = logging.benchstart("데이터베이스 쿼리")
# ... 실제 작업 ...
logging.benchend("쿼리 완료", bench_id)
```

## 기본 사용법

### 핸들러 설정

```python
import logging
from bench_logging_handler import BenchHandler, ConsoleSink, BoxFormatter

# 기본 설정
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(BenchHandler(
    trace_levels=("DEBUG", "ERROR", "CRITICAL"),  # 스택 트레이스를 포함할 레벨
    sink=ConsoleSink(formatter=BoxFormatter())
))
```

### 로깅 메서드

| 메서드 | 설명 | 예시 |
|--------|------|------|
| `logging.debug()` | 디버그 메시지 | `logging.debug("변수 값: %s", value)` |
| `logging.info()` | 일반 정보 | `logging.info("사용자 로그인: %s", username)` |
| `logging.warning()` | 경고 메시지 | `logging.warning("메모리 사용량 높음")` |
| `logging.error()` | 오류 메시지 | `logging.error("데이터베이스 연결 실패")` |
| `logging.critical()` | 심각한 오류 | `logging.critical("시스템 종료 중")` |

### 벤치마킹

```python
import logging

# 기본 벤치마킹
bench_id = logging.benchstart("파일 업로드")
# ... 파일 업로드 작업 ...
logging.benchend("업로드 완료", bench_id)

# 사용자 정의 ID와 태스크명
logging.benchstart("API 요청", bench_id="api_001", task_name="user_api")
# ... API 요청 처리 ...
logging.benchend("API 응답 완료", bench_id="api_001")

# 최소 사용법 (자동 ID 생성)
bench_id = logging.benchstart("자동 측정")
# ... 작업 ...
logging.benchend("완료", bench_id)
```

## 출력 형식 - Sink

### ConsoleSink

```python
from bench_logging_handler import BenchHandler, ConsoleSink

handler = BenchHandler(sink=ConsoleSink())
```

### FileSink

```python
from bench_logging_handler import BenchHandler, FileSink, JsonFormatter

handler = BenchHandler(
    sink=FileSink('app.json', formatter=JsonFormatter())
)
```

### BoxFormatter (Pretty Print)

```python
from bench_logging_handler import BenchHandler, ConsoleSink, BoxFormatter

handler = BenchHandler(
    sink=ConsoleSink(formatter=BoxFormatter())
)
```

## 고급 설정

### trace_levels 옵션

스택 트레이스를 표시할 로그 레벨을 지정합니다:

```python
# 특정 레벨만
BenchHandler(trace_levels=("ERROR", "CRITICAL"))

# 모든 레벨
BenchHandler(trace_levels=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"))

# 벤치마크만
BenchHandler(trace_levels=("BENCH",))

# 벤치마크 포함
BenchHandler(trace_levels=("ERROR", "CRITICAL", "BENCH"))
```

### 다중 싱크

```python
from bench_logging_handler import BenchHandler, ConsoleSink, FileSink

# 콘솔과 파일에 동시 출력
console_handler = BenchHandler(sink=ConsoleSink())
file_handler = BenchHandler(sink=FileSink('app.json'))

logging.getLogger().addHandler(console_handler)
logging.getLogger().addHandler(file_handler)
```

### 로거별 다른 설정

```python
import logging
from bench_logging_handler import BenchHandler, ConsoleSink, FileSink, BoxFormatter

# 각 로거별로 다른 핸들러 설정
app_logger = logging.getLogger("app")
db_logger = logging.getLogger("database")
api_logger = logging.getLogger("api")

app_logger.addHandler(BenchHandler(sink=ConsoleSink(formatter=BoxFormatter())))
db_logger.addHandler(BenchHandler(sink=FileSink('database.json')))
api_logger.addHandler(BenchHandler(sink=FileSink('api.json')))
```

## 향후 업데이트 계획

### 벤치마크 지표 추가
- **메모리 사용량 측정**: 프로세스 메모리 사용량 추적
- **CPU 사용률 측정**: CPU 사용률 모니터링
- **네트워크 I/O 측정**: 네트워크 트래픽 측정
- **디스크 I/O 측정**: 파일 시스템 I/O 성능 추적
- **사용자 정의 메트릭**: 커스텀 벤치마크 지표 지원

### Web 기반 대시보드
- **실시간 모니터링**: 라이브 성능 데이터 시각화
- **히스토리컬 데이터**: 과거 성능 데이터 분석 및 차트
- **알림 시스템**: 성능 임계값 초과 시 알림
- **다중 프로젝트 지원**: 여러 애플리케이션 통합 모니터링
- **RESTful API**: 대시보드 데이터 접근용 API 제공

## 요구사항

- Python 3.8+
- psutil (시스템 정보용)

## 라이선스

MIT License