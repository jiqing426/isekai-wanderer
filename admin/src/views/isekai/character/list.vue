<template>
  <div class="p-4">
    <a-card title="角色管理">
      <a-table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :row-key="rowKey"
        :pagination="false"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'inner_drive'">
            {{ formatInnerDrive(record) }}
          </template>
          <template v-if="column.key === 'actions'">
            <a-button size="small" @click="goEdit(record.id)">编辑</a-button>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { Card, Table, Button } from 'ant-design-vue';
  import { useMessage } from '@/hooks/web/useMessage';
  import { characterApi, type Character } from '@/api/isekai/character';

  const ACard = Card;
  const ATable = Table;
  const AButton = Button;

  const router = useRouter();
  const { createMessage } = useMessage();

  const data = ref<Character[]>([]);
  const loading = ref(false);

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 280, ellipsis: true },
    { title: '名称', dataIndex: 'name' },
    { title: '描述', dataIndex: 'description', ellipsis: true },
    { title: '内在驱动', key: 'inner_drive' },
    { title: '操作', key: 'actions', width: 100 },
  ];

  function rowKey(record: Character) {
    return record.id;
  }

  function formatInnerDrive(record: Character): string {
    const parts: string[] = [];
    if (record.desire) parts.push(`渴望: ${record.desire}`);
    if (record.fear) parts.push(`恐惧: ${record.fear}`);
    if (record.secret) parts.push(`秘密: ${record.secret}`);
    return parts.length > 0 ? parts.join(' | ') : '未配置';
  }

  function goEdit(id: string) {
    router.push(`/isekai/characters/${id}/edit`);
  }

  async function loadData() {
    loading.value = true;
    try {
      const res = await characterApi.list();
      data.value = res;
    } catch (err: any) {
      createMessage.error(err?.message || '加载失败');
    } finally {
      loading.value = false;
    }
  }

  onMounted(() => {
    loadData();
  });
</script>
