# CI/CD Pipeline

Этот проект использует GitHub Actions для автоматизации тестирования и развертывания.

## Workflows

### 🧪 CI Pipeline (`.github/workflows/ci.yml`)

Автоматически запускается при каждом push и pull request в ветки `main` и `develop`.

**Включает:**

1. **Test** - Тестирование на Python 3.9, 3.10, 3.11
   - Установка зависимостей
   - Загрузка spaCy модели
   - Lint с flake8
   - Запуск unit tests
   - Coverage отчеты (Codecov)

2. **Docker Build** - Сборка Docker образов
   - API image (FastAPI)
   - UI image (Streamlit)
   - Проверка docker-compose конфигурации

3. **Code Quality** - Проверка качества кода
   - Black (форматирование)
   - isort (сортировка импортов)
   - mypy (type checking)

4. **Security** - Проверка безопасности
   - Safety (уязвимости в зависимостях)
   - Bandit (security linter)

### 🚀 Deploy Pipeline (`.github/workflows/deploy.yml`)

Автоматически запускается при создании release или вручную.

**Включает:**

1. **Docker Deployment**
   - Build и push Docker images в Docker Hub
   - Versioning (tag из release или `latest`)
   - Build cache для ускорения

2. **Notifications**
   - Статус деплоя
   - Deployment summary

## Badges

Добавьте в README.md:

```markdown
![CI Pipeline](https://github.com/AdvancedBeka/ai-recruiting-agent/workflows/CI%20Pipeline/badge.svg)
![Deploy](https://github.com/AdvancedBeka/ai-recruiting-agent/workflows/Deploy%20to%20Production/badge.svg)
```

## Настройка Secrets

Для полноценной работы CI/CD добавьте следующие secrets в настройках репозитория:

**Settings → Secrets and variables → Actions → New repository secret**

### Обязательные:
- `OPENAI_API_KEY` - для тестирования LLM matcher

### Опциональные (для deploy):
- `DOCKER_USERNAME` - логин Docker Hub
- `DOCKER_PASSWORD` - пароль или token Docker Hub

## Локальный запуск тестов

```bash
# Установить зависимости для тестирования
pip install pytest pytest-cov flake8 black isort mypy safety bandit

# Запустить все тесты
pytest tests/ -v

# С coverage
pytest tests/ -v --cov=src --cov-report=html

# Проверить код quality
black --check src/
isort --check-only src/
flake8 src/

# Security scan
safety check
bandit -r src/
```

## Continuous Deployment

При создании release на GitHub:

1. CI pipeline проверит код
2. Deploy pipeline соберет Docker images
3. Images будут загружены в Docker Hub с версией из tag
4. Можно развернуть на любом сервере:

```bash
docker pull <username>/ai-recruiting-api:v1.0.0
docker pull <username>/ai-recruiting-ui:v1.0.0
docker-compose up -d
```

## Manual Deployment

Можно запустить deploy вручную:

1. Перейти в **Actions** → **Deploy to Production**
2. Нажать **Run workflow**
3. Выбрать ветку
4. **Run workflow**

---

**Статус CI/CD:** Production Ready ✅
