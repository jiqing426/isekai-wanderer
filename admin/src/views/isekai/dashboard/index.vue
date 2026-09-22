<template>
  <div class="p-4">
    <a-card title="CR-027 叙事引擎管理" class="mb-4">
      <a-space>
        <a-button type="primary" @click="goTo('/isekai/lorebook')">Lorebook 管理</a-button>
        <a-button @click="goTo('/isekai/scene')">场景配置</a-button>
        <a-button @click="goTo('/isekai/characters')">角色管理</a-button>
      </a-space>
    </a-card>
    <a-card title="系统信息">
      <a-descriptions :column="1" bordered>
        <a-descriptions-item label="版本">CR-027</a-descriptions-item>
        <a-descriptions-item label="功能">分层 Prompt 叙事引擎</a-descriptions-item>
        <a-descriptions-item label="管理模块">Lorebook / 场景配置 / NPC 内在驱动</a-descriptions-item>
      </a-descriptions>
    </a-card>
  </div>
</template>

<script setup lang="ts">
  import { useRouter } from 'vue-router';
  import { Card, Button, Space, Descriptions } from 'ant-design-vue';

  const router = useRouter();

  const ACard = Card;
  const AButton = Button;
  const ASpace = Space;
  const ADescriptions = Descriptions;
  const ADescriptionsItem = Descriptions.Item;

  function goTo(path: string) {
    router.push(path);
  }
</script>
