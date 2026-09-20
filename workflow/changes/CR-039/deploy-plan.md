# Deploy Plan: CR-039 — Corvus 玩家选项功能

## 部署步骤

1. 后端：`docker compose restart backend`（volume 挂载，无需 rebuild）
2. 前端：`cd frontend && npm run build` → dist 已更新
3. Corvus：`systemctl restart corvus-story`（GM prompt 已更新）
4. DB 迁移：`ALTER TABLE corvus_game_sessions ADD COLUMN IF NOT EXISTS character_id UUID REFERENCES characters(id);`（已执行）

## 回滚方案

```bash
# 后端
cd /root/isekai-wanderer && git checkout -- backend/app/services/corvus_adapter.py backend/app/api/v1/game.py backend/app/models/corvus.py
docker compose restart backend

# 前端
cd /root/isekai-wanderer/frontend && git checkout -- src/stores/game.ts src/views/GameView.vue src/components/StoryPanel.vue src/components/FreeChatInput.vue
npm run build

# Corvus
cd /root/code/Corvus-Story-Core && git checkout -- server/services/gameMaster.ts
systemctl restart corvus-story
```

## 健康检查

```bash
curl -s http://localhost:8000/api/v1/health
curl -s http://127.0.0.1:8082/api/health
docker compose ps
```

## 监控

- 后端日志：`docker logs -f isekai-wanderer-backend-1`
- Corvus 日志：`journalctl -u corvus-story -f`
- 前端：http://localhost:8081
