# APITestGen Deployment

APITestGen là công cụ tự động phân tích tài liệu API (OpenAPI/Postman) và sinh test case cũng như mã kiểm thử hoàn toàn tự động.

## Cấu trúc

```
apitestgen/
├── helmfile.yaml          # Helmfile để deploy
├── values.yaml.gotmpl     # Cấu hình values
├── chart/                 # Helm chart từ repository gốc
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/         # Kubernetes manifests
└── README.md
```

## Tính năng

- **Backend**: FastAPI application với PostgreSQL và Redis
- **Frontend**: React application với TypeScript
- **Ingress**: Nginx ingress với TLS
- **Persistence**: Ceph RBD storage cho database, cache, logs và api-docs
- **Resources**: Resource limits và requests được cấu hình

## URLs

- Frontend: https://apitestgen.lab.tekodata.com
- Backend API: https://apitestgen-api.lab.tekodata.com

## Deploy

```bash
# Deploy to lab cluster
helmfile -f lab.platform/apitestgen/helmfile.yaml apply

# Hoặc deploy từ root
helmfile -f lab.platform/helmfile.yaml apply
```

## Cấu hình

Chỉnh sửa `values.yaml.gotmpl` để thay đổi:

- Image versions
- Resource limits
- Ingress hosts
- Database credentials
- Storage sizes (PostgreSQL, Redis, Logs, API Docs)

## Dependencies

- PostgreSQL 15
- Redis 7
- Nginx Ingress Controller
- Ceph RBD Storage Class

## Source

Chart được lấy từ: https://github.com/nhuantho/tic-2025/tree/main/charts/tic-2025 