<template>
  <div>
    <h1>角色管理</h1>
    <n-data-table
      :columns="columns"
      :data="data"
      :loading="loading"
      :row-key="(row: Character) => row.id"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue';
import { useMessage, NButton } from 'naive-ui';
import { useRouter } from 'vue-router';
import { characterApi, type Character } from '@/api/character';

const router = useRouter();
const message = useMessage();

const data = ref<Character[]>([]);
const loading = ref(false);

const columns = [
  { title: 'ID', key: 'id', width: 280, ellipsis: { tooltip: true } },
  { title: '名称', key: 'name' },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  {
    title: '内在驱动',
    key: 'inner_drive',
    render(row: Character) {
      const parts = [];
      if (row.desire) parts.push(`渴望: ${row.desire}`);
      if (row.fear) parts.push(`恐惧: ${row.fear}`);
      if (row.secret) parts.push(`秘密: ${row.secret}`);
      return parts.length > 0 ? parts.join(' | ') : '未配置';
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render(row: Character) {
      return h(NButton, { size: 'small', onClick: () => router.push(`/characters/${row.id}`) }, { default: () => '编辑' });
    },
  },
];

async function loadData() {
  loading.value = true;
  try {
    const res = await characterApi.list();
    data.value = res;
  } catch (err: any) {
    message.error(err.message || '加载失败');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>
