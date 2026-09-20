<template>
  <div>
    <n-space justify="space-between" align="center" style="margin-bottom: 16px">
      <h1 style="margin: 0">Lorebook 管理</h1>
      <n-button type="primary" @click="openCreate">+ 新建条目</n-button>
    </n-space>

    <!-- Filter -->
    <n-space style="margin-bottom: 16px">
      <n-input v-model:value="filterTag" placeholder="按标签筛选" clearable style="width: 200px" @clear="loadData" @keyup.enter="loadData" />
      <n-button @click="loadData">筛选</n-button>
    </n-space>

    <!-- Table -->
    <n-data-table
      :columns="columns"
      :data="data"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row: LorebookListItem) => row.id"
    />

    <!-- Modal -->
    <n-modal v-model:show="showModal" preset="dialog" :title="editingId ? '编辑条目' : '新建条目'" style="width: 600px">
      <n-form :model="form">
        <n-form-item label="标题">
          <n-input v-model:value="form.title" placeholder="条目标题" maxlength="200" />
        </n-form-item>
        <n-form-item label="内容">
          <n-input v-model:value="form.content" type="textarea" placeholder="条目内容" :rows="6" maxlength="5000" />
        </n-form-item>
        <n-form-item label="标签">
          <n-dynamic-tags v-model:value="form.tags" />
        </n-form-item>
        <n-form-item label="优先级">
          <n-input-number v-model:value="form.priority" :min="0" />
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
import { lorebookApi, type LorebookListItem } from '@/api/lorebook';

const message = useMessage();
const dialog = useDialog();

const data = ref<LorebookListItem[]>([]);
const loading = ref(false);
const showModal = ref(false);
const saving = ref(false);
const editingId = ref<string | null>(null);
const filterTag = ref('');

const pagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => {
    pagination.page = page;
    loadData();
  },
  onUpdatePageSize: (size: number) => {
    pagination.pageSize = size;
    pagination.page = 1;
    loadData();
  },
});

const form = reactive({
  title: '',
  content: '',
  tags: [] as string[],
  priority: 0,
});

const columns = [
  { title: '标题', key: 'title', ellipsis: { tooltip: true } },
  {
    title: '标签',
    key: 'tags',
    width: 300,
    render(row: LorebookListItem) {
      return h(NSpace, null, {
        default: () => row.tags.map((tag: string) => h(NTag, { size: 'small', key: tag }, { default: () => tag })),
      });
    },
  },
  { title: '优先级', key: 'priority', width: 80 },
  { title: '更新时间', key: 'updated_at', width: 180, render: (row: LorebookListItem) => new Date(row.updated_at).toLocaleString() },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    render(row: LorebookListItem) {
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
    const res = await lorebookApi.list(pagination.page, pagination.pageSize, filterTag.value || undefined);
    data.value = res.items;
    pagination.itemCount = res.total;
  } catch (err: any) {
    message.error(err.message || '加载失败');
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingId.value = null;
  form.title = '';
  form.content = '';
  form.tags = [];
  form.priority = 0;
  showModal.value = true;
}

async function openEdit(row: LorebookListItem) {
  editingId.value = row.id;
  try {
    const entry = await lorebookApi.get(row.id);
    form.title = entry.title;
    form.content = entry.content;
    form.tags = [...entry.tags];
    form.priority = entry.priority;
    showModal.value = true;
  } catch (err: any) {
    message.error(err.message || '加载详情失败');
  }
}

async function handleSave() {
  if (!form.title.trim()) {
    message.warning('请填写标题');
    return;
  }
  if (!form.content.trim()) {
    message.warning('请填写内容');
    return;
  }
  saving.value = true;
  try {
    if (editingId.value) {
      await lorebookApi.update(editingId.value, {
        title: form.title,
        content: form.content,
        tags: form.tags,
        priority: form.priority,
      });
      message.success('更新成功');
    } else {
      await lorebookApi.create({
        title: form.title,
        content: form.content,
        tags: form.tags,
        priority: form.priority,
      });
      message.success('创建成功');
    }
    showModal.value = false;
    loadData();
  } catch (err: any) {
    message.error(err.message || '保存失败');
  } finally {
    saving.value = false;
  }
}

function handleDelete(row: LorebookListItem) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除「${row.title}」吗？此操作为软删除。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await lorebookApi.delete(row.id);
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
