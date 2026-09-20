<template>
  <div>
    <n-space justify="space-between" align="center" style="margin-bottom: 16px">
      <h1 style="margin: 0">场景配置管理</h1>
      <n-button type="primary" @click="openCreate">+ 新建配置</n-button>
    </n-space>

    <!-- Filters -->
    <n-space style="margin-bottom: 16px">
      <n-input v-model:value="filterScriptId" placeholder="Script ID" clearable style="width: 200px" />
      <n-input v-model:value="filterRouteId" placeholder="Route ID" clearable style="width: 200px" />
      <n-button @click="loadData">筛选</n-button>
    </n-space>

    <!-- Table -->
    <n-data-table
      :columns="columns"
      :data="data"
      :loading="loading"
      :row-key="(row: SceneConfig) => row.id"
    />

    <!-- Modal -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editingNodeId ? '编辑配置' : '新建配置'" style="width: 600px">
      <n-form :model="form">
        <n-form-item label="Node ID">
          <n-input v-model:value="form.nodeId" placeholder="Node UUID" :disabled="!!editingNodeId" />
        </n-form-item>
        <n-form-item label="场景名称">
          <n-input v-model:value="form.sceneName" placeholder="场景名称" maxlength="200" />
        </n-form-item>
        <n-form-item label="标签">
          <n-dynamic-tags v-model:value="form.tags" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="form.description" type="textarea" placeholder="场景描述" :rows="4" maxlength="5000" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showModal = false">取消</n-button>
        <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue';
import { useMessage, useDialog, NButton, NTag, NSpace } from 'naive-ui';
import { sceneConfigApi, type SceneConfig } from '@/api/sceneConfig';

const message = useMessage();
const dialog = useDialog();

const data = ref<SceneConfig[]>([]);
const loading = ref(false);
const showModal = ref(false);
const saving = ref(false);
const editingNodeId = ref<string | null>(null);
const filterScriptId = ref('');
const filterRouteId = ref('');

const form = reactive({
  nodeId: '',
  sceneName: '',
  tags: [] as string[],
  description: '',
});

const columns = [
  { title: 'Node ID', key: 'node_id', width: 280, ellipsis: { tooltip: true } },
  { title: '场景名称', key: 'scene_name', ellipsis: { tooltip: true } },
  {
    title: '标签',
    key: 'tags',
    width: 250,
    render(row: SceneConfig) {
      return h(NSpace, null, {
        default: () => row.tags.map((tag: string) => h(NTag, { size: 'small', key: tag }, { default: () => tag })),
      });
    },
  },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '更新时间', key: 'updated_at', width: 180, render: (row: SceneConfig) => new Date(row.updated_at).toLocaleString() },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    render(row: SceneConfig) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openEdit(row) }, { default: () => '编辑' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, { default: () => '删除' }),
        ],
      });
    },
  },
];

async function loadData() {
  loading.value = true;
  try {
    const res = await sceneConfigApi.list(
      filterScriptId.value || undefined,
      filterRouteId.value || undefined
    );
    data.value = res;
  } catch (err: any) {
    message.error(err.message || '加载失败');
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingNodeId.value = null;
  form.nodeId = '';
  form.sceneName = '';
  form.tags = [];
  form.description = '';
  showModal.value = true;
}

function openEdit(row: SceneConfig) {
  editingNodeId.value = row.node_id;
  form.nodeId = row.node_id;
  form.sceneName = row.scene_name;
  form.tags = [...row.tags];
  form.description = row.description || '';
  showModal.value = true;
}

async function handleSave() {
  if (!form.nodeId.trim()) {
    message.warning('请填写 Node ID');
    return;
  }
  if (!form.sceneName.trim()) {
    message.warning('请填写场景名称');
    return;
  }
  saving.value = true;
  try {
    await sceneConfigApi.upsert(form.nodeId, {
      scene_name: form.sceneName,
      tags: form.tags,
      description: form.description || undefined,
    });
    message.success(editingNodeId.value ? '更新成功' : '创建成功');
    showModal.value = false;
    loadData();
  } catch (err: any) {
    message.error(err.message || '保存失败');
  } finally {
    saving.value = false;
  }
}

function handleDelete(row: SceneConfig) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除 Node「${row.node_id}」的场景配置吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await sceneConfigApi.delete(row.node_id);
        message.success('删除成功');
        loadData();
      } catch (err: any) {
        message.error(err.message || '删除失败');
      }
    },
  });
}

onMounted(() => {
  loadData();
});
</script>
