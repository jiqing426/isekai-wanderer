<template>
  <div>
    <h1>管理后台首页</h1>
    <n-space vertical :size="16">
      <n-card title="CR-027 叙事引擎管理">
        <n-space>
          <n-button type="primary" @click="$router.push('/lorebook')">Lorebook 管理</n-button>
          <n-button @click="$router.push('/scene-config')">场景配置</n-button>
          <n-button @click="$router.push('/characters')">角色管理</n-button>
        </n-space>
      </n-card>
      <n-card title="系统信息">
        <n-descriptions :column="1" bordered>
          <n-descriptions-item label="版本">CR-027</n-descriptions-item>
          <n-descriptions-item label="功能">分层 Prompt 叙事引擎</n-descriptions-item>
          <n-descriptions-item label="管理模块">Lorebook / 场景配置 / NPC 内在驱动</n-descriptions-item>
        </n-descriptions>
      </n-card>
    </n-space>
  </div>
</template>
