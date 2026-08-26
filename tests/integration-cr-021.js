// CR-021 集成测试 - 角色对话聊天界面
const axios = require('axios');

const API_BASE = 'http://localhost:8000/api/v1';

async function runIntegrationTests() {
  console.log('=== CR-021 集成测试开始 ===\n');

  // 1. 测试健康检查
  console.log('1. 测试健康检查...');
  try {
    const healthRes = await axios.get(`${API_BASE}/health`);
    console.log('   ✅ 健康检查通过:', healthRes.status);
  } catch (err) {
    console.log('   ❌ 健康检查失败:', err.message);
  }

  // 2. 测试聊天消息 API（需要认证）
  console.log('\n2. 测试聊天消息 API...');
  try {
    const characterId = '00000000-0000-0000-0000-000000000001';
    const messagesRes = await axios.get(
      `${API_BASE}/character-chat/${characterId}/messages`,
      {
        headers: {
          'Authorization': 'Bearer test_token' // 测试token
        }
      }
    );
    console.log('   ✅ 聊天消息 API 响应:', messagesRes.status);
    console.log('   消息数量:', messagesRes.data.messages?.length || 0);
  } catch (err) {
    if (err.response?.status === 401) {
      console.log('   ⚠️  需要认证（预期行为）');
    } else {
      console.log('   ❌ API 调用失败:', err.response?.status, err.message);
    }
  }

  // 3. 测试推荐话题 API（需要认证）
  console.log('\n3. 测试推荐话题 API...');
  try {
    const characterId = '00000000-0000-0000-0000-000000000001';
    const topicsRes = await axios.get(
      `${API_BASE}/character-chat/${characterId}/topics`,
      {
        headers: {
          'Authorization': 'Bearer test_token'
        }
      }
    );
    console.log('   ✅ 推荐话题 API 响应:', topicsRes.status);
    console.log('   话题数量:', topicsRes.data.topics?.length || 0);
  } catch (err) {
    if (err.response?.status === 401) {
      console.log('   ⚠️  需要认证（预期行为）');
    } else {
      console.log('   ❌ API 调用失败:', err.response?.status, err.message);
    }
  }

  // 4. 测试发送消息 API（需要认证）
  console.log('\n4. 测试发送消息 API...');
  try {
    const characterId = '00000000-0000-0000-0000-000000000001';
    const sendRes = await axios.post(
      `${API_BASE}/character-chat/${characterId}/messages`,
      { content: '测试消息' },
      {
        headers: {
          'Authorization': 'Bearer test_token',
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('   ✅ 发送消息 API 响应:', sendRes.status);
  } catch (err) {
    if (err.response?.status === 401) {
      console.log('   ⚠️  需要认证（预期行为）');
    } else {
      console.log('   ❌ API 调用失败:', err.response?.status, err.message);
    }
  }

  // 5. 测试前端路由
  console.log('\n5. 测试前端路由...');
  try {
    const frontendRes = await axios.get('http://localhost:3000/character-chat');
    console.log('   ✅ 前端页面可访问:', frontendRes.status);
  } catch (err) {
    console.log('   ❌ 前端页面访问失败:', err.message);
  }

  console.log('\n=== 集成测试完成 ===');
}

runIntegrationTests().catch(console.error);
