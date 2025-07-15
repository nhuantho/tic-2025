# Test APIs for APITestGen

Bộ test APIs để demo APITestGen với 2 microservices có inter-service communication.

## Cấu trúc

```
test-apis/
├── helmfile.yaml          # Helmfile để deploy
├── values.yaml.gotmpl     # Cấu hình values
├── chart/                 # Helm chart từ repository gốc
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/         # Kubernetes manifests
└── README.md
```

## APIs

### 1. User Management API
- **Port:** 8001
- **URL:** https://user-api.lab.tekodata.com
- **Documentation:** https://user-api.lab.tekodata.com/docs
- **OpenAPI Spec:** https://user-api.lab.tekodata.com/openapi.json

**Features:**
- User registration and authentication
- JWT-based authentication
- User CRUD operations
- User activation/deactivation
- Role-based access control

### 2. E-commerce API
- **Port:** 8002
- **URL:** https://ecommerce-api.lab.tekodata.com
- **Documentation:** https://ecommerce-api.lab.tekodata.com/docs
- **OpenAPI Spec:** https://ecommerce-api.lab.tekodata.com/openapi.json

**Features:**
- Product catalog management
- Category management
- Order processing with user validation
- Stock management
- Order status tracking
- **Inter-service communication** with User API

## Deploy

```bash
# Deploy test-apis
helmfile -f lab.platform/test-apis/helmfile.yaml apply

# Hoặc deploy từ root
helmfile -f lab.platform/helmfile.yaml apply
```

## Inter-Service Communication

E-commerce API gọi User API để:
- Validate user khi tạo order
- Lấy thông tin user cho order
- Xử lý lỗi network và timeout

## Testing với APITestGen

1. Import OpenAPI specs từ:
   - `user-api-openapi.json`
   - `ecommerce-api-openapi.json`

2. Test các scenarios:
   - Authentication flows
   - CRUD operations
   - Inter-service communication
   - Error handling

## Source

Chart được lấy từ: https://github.com/nhuantho/tic-2025/tree/main/test-apis 