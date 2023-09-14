# LLM Project

## Installation

### docker-compose 실행

```bash
docker-compose -f ops/docker-compose.yaml up --build
```

## 사전 작업

**데이터베이스 구축과 데이터 수집**
  - 한국은행 OpenAPI를 이용하여 거시 경제 데이터를 수집합니다.
  - 수집한 데이터는 `docker-compose`에서 선언한 PostgreSQL 데이터베이스에 dump합니다.
  - 이 부분은 `jupyter notebook`을 참고해주세요.
<br>

**환경변수 설정**
  - .env 파일을 생성합니다.
  - 필요한 키와 값들을 .env 파일에 입력합니다.

<br>

## 기능 설명

### MRC (Machine Reading Comprehension)

- **목적**: 주어진 `question`과 `context`를 바탕으로 `context` 내에서 정답을 찾습니다.
  
  ```
  예시: 
  Question: "누가 햄릿 저자야?"
  Context: "햄릿은 셰익스피어에 의해 쓰여진 비극적인 소설이다."
  Answer: "셰익스피어"
  ```

### QA + SQL (Question Answering)
- **목적**: DB에 저장된 거시 경제 데이터를 이용하여 question을 SQL 쿼리로 변환 후 결과를 반환합니다.
  
  ```
  예시: 
  Question: "경제심리지수는 2015년 1월 대비 2015년 9월에 얼마나 올랐어?"
  Answer: "경제심리지수는 2015년 1월 대비 9월에 1.5 포인트 하락했습니다."
  ```

### QA + Search (Question Answering)
- **목적**: Google Search API를 이용하여 데이터를 수집하고 결과를 반환합니다. 
- **추가 기능**: Langchain의 메모리 기능과 LLM Chain을 연결하여 이전 대화를 참조하여 답변을 제공합니다.

  
  ```
  예시: 
  Question: "대한민국의 현재 대통령은 누구야?"
  Answer: "현재 대한민국 대통령은 윤석열입니다."
  ```
  > :warning: **<span style="color:red">주의:</span>** 아직 완벽하게 구현된 것이 아니고 수정이 필요합니다.
  
<br>

## API 명세

### MRC
- **Endpoint**: `POST http://{IP}:80/wrtn/chat/mrc`

- **Request Body**: JSON payload

```json
{
    "question": "Your question here",
    "context": "Your context here",
    "session_id": 2
}
```

### QA + SQL
- **Endpoint**: `POST http://{IP}:80/wrtn/chat/qa`

- **Request Body**: JSON payload


```json
{
    "question": "Your question here",
    "task_type": "sql"
    "session_id": 2
}
```

### QA + Google Search
- **Endpoint**: `POST http://{IP}:80/wrtn/chat/qa`

- **Request Body**: JSON payload


```json
{
    "question": "Your question here",
    "task_type": "search"
    "session_id": 2
}
```

### Task 상태 확인
- **Endpoint**: `GET http://{IP}:80/wrtn/chat/state`
- **Request Parameters**: log_id

### Task 결과 
- **Endpoint**: `GET http://{IP}:80/wrtn/chat/result`
- **Request Parameters**: log_id

<br>

## 서버 아키텍쳐 
<p align="left">
  <img src="https://github.com/okpo65/wrtn_project/assets/20599796/64b1bae7-f323-4897-a2f7-3eaf8b601d3f">
</p>

1. **Client**: 서버에 테스크를 요청합니다.
2. **Server**: LLM Task를 생성하고, 이를 Redis Queue에 저장합니다. 이후 Celery를 실행합니다.
3. **Server → Client**: 생성된 LLM log id를 클라이언트에게 전달합니다.

---
<p align="left">
  <img src="https://github.com/okpo65/wrtn_project/assets/20599796/a1790bae-c30c-4f9c-842f-85955c06b505">
</p>

1. **Client**: 이전 과정에서 받은 log id를 서버에 전송합니다.
2. **Server**: log id를 통해 task의 현재 상태를 확인합니다.

   - 이 과정은 클라이언트에서 polling 방식으로 여러 번 요청됩니다.

---
<p align="left">
  <img src="https://github.com/okpo65/wrtn_project/assets/20599796/d164e691-b61d-4209-a11a-c48309a2f149">
</p>

1. **Celery**: 작업이 완료되면, 그 결과를 서버에 전달하여 task 상태를 업데이트합니다.
2. **Client**: 작업 결과를 서버에 요청합니다.
3. **Server**: 작업 결과를 클라이언트에게 전달합니다.
