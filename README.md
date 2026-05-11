# ml-service-cicd

ML-сервис классификации Iris с автоматическим Blue-Green развёртыванием через CI/CD

**Автор:** Кузнецова Полина Глебовна
**Курс:** Развёртывание ML моделей, ДЗ 7 — Сборка конвейера CI/CD

## Стек

- FastAPI + scikit-learn (RandomForestClassifier на датасете Iris)
- Docker, docker-compose, nginx (Blue-Green + Canary через `split_clients`)
- GitLab CI / Gitea Actions / GitHub Actions

## Структура проекта

```
.
├── app.py                          # FastAPI с /health и /predict
├── ml_pipeline.py                  # обучение и сериализация модели
├── Dockerfile                      # python:3.11-slim, healthcheck
├── requirements.txt
├── VERSION                         # версия модели/образа
├── docker-compose.blue.yml         # v1.0.0
├── docker-compose.green.yml        # v1.1.0
├── nginx.conf                      # балансировщик Blue-Green
├── .gitlab-ci.yml                  # CI/CD для GitLab
├── .gitea/workflows/deploy.yml     # CI/CD для Gitea
├── .github/workflows/deploy.yml    # CI/CD для GitHub
└── docs/adr/0001-deploy-strategy.md
```

## Стратегия развёртывания

Выбрана **Blue-Green**: две независимых среды (`blue` = v1.0.0, `green` = v1.1.0) за nginx, мгновенное переключение и откат. Обоснование и сравнение с Canary/Rolling/Shadow — в `docs/adr/0001-deploy-strategy.md`

## Локальный запуск

```bash
docker compose -f docker-compose.blue.yml up -d --build
```

Проверка эндпоинтов:

```bash
curl http://localhost/health
# {"status":"ok","version":"v1.0.0"}

curl -X POST http://localhost/predict \
     -H "Content-Type: application/json" \
     -d '{"x":[5.1,3.5,1.4,0.2]}'
# {"prediction":0,"version":"v1.0.0"}
```

## Деплой green-версии и переключение трафика

```bash
docker compose -f docker-compose.green.yml up -d --build
curl http://green-host/health      # smoke-тест перед переключением
sed -i 's|proxy_pass http://ml_blue;|proxy_pass http://ml_green;|' nginx.conf
docker exec nginx nginx -s reload
```

## Rollback

```bash
sed -i 's|proxy_pass http://ml_green;|proxy_pass http://ml_blue;|' nginx.conf
docker exec nginx nginx -s reload
docker compose -f docker-compose.green.yml down
```

## A/B-тестирование

Расчёт минимального объёма выборки (p_A=0.92, MDE=0.02, α=0.05, power=0.8) и z-test пропорций — в ноутбуке `HW7_CICD_Кузнецова_Полина.ipynb`, секция 4

## CI/CD пайплайны

- **GitLab:** `.gitlab-ci.yml` — build → test → package → deploy
- **Gitea:** `.gitea/workflows/deploy.yml`
- **GitHub Actions:** `.github/workflows/deploy.yml`

Все три пайплайна содержат шаг **Make pipeline reproducible** (фиксация версий, генерация `requirements.lock`, тегирование образа по `sha` и версии модели)
