# APITestGen - Automated API Test Generation Tool

APITestGen là công cụ tự động phân tích tài liệu API (OpenAPI/Postman) và sinh test case cũng như mã kiểm thử hoàn toàn tự động.

## Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| ✅ Import Spec | OpenAPI v2/v3 (.yaml/.json), Postman |
| ✅ Sinh CURL | CURL command để test endpoint tự động |
| ✅ Kiểm thử tự động | Status code, error handling, rate limit, auth... |
| ✅ Sinh test case | Manual file + Script code |
| ✅ AI hỗ trợ | Sinh test case với input boundary/edge |
| ✅ Web UI | Xem + chạy test + lưu kết quả |
| ✅ CI/CD | Tích hợp Jenkins, GitHub Action dễ dàng |
| ✅ Export | Test case dạng JSON, CSV, Postman, Python |

## Cấu trúc Project

```
tic-2025/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, database, security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   ├── public/             # Static files
│   └── package.json        # Node dependencies
├── api-docs/               # API Documentation samples
├── logs/                   # Test execution logs
├── docker-compose.yml      # Docker setup
└── README.md              # This file
```

## Công nghệ sử dụng

- **Backend**: Python, FastAPI
- **Frontend**: ReactJS + TypeScript
- **Parsing & Gen**: pydantic, openapi-spec-parser, Jinja2
- **Caching**: Valkey (Redis-compatible)
- **Storage**: PostgreSQL
- **AI Integration**: LLM để sinh boundary cases
- **CI/CD**: Plugin/Postman collection export

## Cài đặt và chạy

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL

### Quick Start

1. **Clone repository**
```bash
git clone <repository-url>
cd tic-2025
```

2. **Chạy với Docker**
```bash
docker-compose up -d
```

3. **Hoặc chạy local**
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## Sử dụng

1. **Import API Spec**: Upload file OpenAPI/Postman vào hệ thống
2. **Validation**: Hệ thống tự động test các endpoint
3. **Generate Tests**: Sinh test case dựa trên spec và response
4. **Run Tests**: Chạy test qua Web UI
5. **Export**: Xuất test case ra nhiều format

## API Endpoints

- `POST /api/import` - Import API specification
- `GET /api/endpoints` - List all endpoints
- `POST /api/validate` - Validate endpoints
- `POST /api/generate-tests` - Generate test cases
- `POST /api/run-tests` - Execute tests
- `GET /api/results` - Get test results

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License 