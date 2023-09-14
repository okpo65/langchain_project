# LLM Project

## Installation

### Build the docker-compose image

```bash
docker-compose -f ops/docker-compose.yaml up --build
```

## 사전 작업

DB 구축해서 한국은행 OpenAPI를 통해 거시 경제 데이터 수집. 그 후 docker-compose로 선언된 postgresql에 data dumping 진행


## API Interface

### MRC
- **Endpoint**: `POST http://{IP}:80/wrtn/chat/mrc`

- **Request Body**: JSON payload

```json
{
    "question": "~~",
    "context": "~~",
    "session_id": 2
}
```

### QA + SQL
- **Endpoint**: `POST http://{IP}:80/wrtn/chat/qa`

- **Request Body**: JSON payload


```json
{
    "question": "~~",
    "task_type": "sql"
    "session_id": 2
}
```

### QA + Google Search
- **Endpoint**: `POST http://{IP}:80/wrtn/chat/qa`

- **Request Body**: JSON payload


```json
{
    "question": "~~",
    "task_type": "search"
    "session_id": 2
}
```
## 기능 설명

**MRC**
question과 context가 parameter로 주어지고 context내에서 정답을 찾는 테스크

**QA + SQL**
DB에 저장된 거시 경제 데이터를 기준으로 question을 SQL문으로 변환 후 결과

**QA + Search**
Google Search API와 연동해서 데이터 수집 후 결과 낼 수 있도록 진행. 그리고 langchain의 memory 기능을 LLM Chain에 연결함으로서 예전 대화를 기준으로 답변을 이어나갈수 있도록 구성. (완벽히 구현 못함 - 수정 필요)


## Server Architecture Diagram
<p align="center">
  <img src="https://github.com/okpo65/riiid_project/assets/20599796/f04fdea7-f371-4eee-aab5-21b9c0e32384">
</p>



