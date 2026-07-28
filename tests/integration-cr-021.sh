#!/bin/bash
# CR-021 集成测试脚本

API_BASE="http://localhost:8000/api/v1"
CHARACTER_ID="00000000-0000-0000-0000-000000000001"

echo "=== CR-021 集成测试开始 ==="
echo ""

# 1. 测试健康检查
echo "1. 测试健康检查..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/health")
if [ "$HEALTH" = "200" ]; then
    echo "   ✅ 健康检查通过: $HEALTH"
else
    echo "   ❌ 健康检查失败: $HEALTH"
fi

# 2. 测试聊天消息 API（无认证）
echo ""
echo "2. 测试聊天消息 API（无认证）..."
MESSAGES=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/character-chat/$CHARACTER_ID/messages")
if [ "$MESSAGES" = "401" ]; then
    echo "   ⚠️  需要认证（预期行为）: $MESSAGES"
else
    echo "   状态码: $MESSAGES"
fi

# 3. 测试推荐话题 API（无认证）
echo ""
echo "3. 测试推荐话题 API（无认证）..."
TOPICS=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/character-chat/$CHARACTER_ID/topics")
if [ "$TOPICS" = "401" ]; then
    echo "   ⚠️  需要认证（预期行为）: $TOPICS"
else
    echo "   状态码: $TOPICS"
fi

# 4. 测试发送消息 API（无认证）
echo ""
echo "4. 测试发送消息 API（无认证）..."
SEND=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE/character-chat/$CHARACTER_ID/messages" \
    -H "Content-Type: application/json" \
    -d '{"content":"测试消息"}')
if [ "$SEND" = "401" ]; then
    echo "   ⚠️  需要认证（预期行为）: $SEND"
else
    echo "   状态码: $SEND"
fi

# 5. 测试前端路由
echo ""
echo "5. 测试前端路由..."
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8081/character-chat")
if [ "$FRONTEND" = "200" ]; then
    echo "   ✅ 前端页面可访问: $FRONTEND"
else
    echo "   ❌ 前端页面访问失败: $FRONTEND"
fi

echo ""
echo "=== 集成测试完成 ==="
