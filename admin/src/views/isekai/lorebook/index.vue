<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl m-0">Lorebook 管理</h1>
      <a-button type="primary" @click="openCreate">+ 新建条目</a-button>
    </div>

    <!-- Filter -->
    <div class="mb-4 flex gap-2">
      <a-input
        v-model:value="filterTag"
        placeholder="按标签筛选"
        allow-clear
        style="width: 200px"
        @press-enter="loadData"
        @change="onFilterChange"
      />
      <a-button @click="loadData">筛选</a-button>
    </div>

    <!-- Table -->
    <a-card>
      <a-table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :row-key="rowKey"
        :pagination="pagination"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'tags'">
            <a-tag v-for="tag in record.tags" :key="tag" color="blue">{{ tag }}</a-tag>
          </template>
          <template v-if="column.key === 'updated_at'">
            {{ formatDate(record.updated_at) }}
          </template>
          <template v-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" @click="openEdit(record)">编辑</a-button>
              <a-button size="small" danger @click="handleDelete(record)">删除</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Modal -->
    <a-modal
      v-model:open="showModal"
      :title="editingId ? '编辑条目' : '新建条目'"
      width="600px"
      :confirm-loading="saving"
      @ok="handleSave"
      @cancel="showModal = false"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="标题">
          <a-input v-model:value="form.title" placeholder="条目标题" :maxlength="200" />
        </a-form-item>
        <a-form-item label="内容">
          <a-textarea
            v-model:value="form.content"
            placeholder="条目内容"
            :rows="6"
            :maxlength="5000"
          />
        </a-form-item>
        <a-form-item label="标签">
          <div>
            <a-tag
              v-for="(tag, index) in form.tags"
              :key="tag"
              closable
              @close="removeTag(index)"
            >
              {{ tag }}
            </a-tag>
            <a-input
              v-if="tagInputVisible"
              ref="tagInputRef"
              v-model:value="tagInputValue"
              size="small"
              style="width: 120px"
              @press-enter="addTag"
              @blur="addTag"
            />
            <a-button v-else size="small" @click="showTagInput">+ 添加标签</a-button>
          </div>
        </a-form-item>
        <a-form-item label="优先级">
          <a-input-number v-model:value="form.priority" :min="0" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted, nextTick } from 'vue';
  import { Card, Button, Table, Input, Modal, Form, Tag, Space, InputNumber } from 'ant-design-vue';
  import { useMessage } from '@/hooks/web/useMessage';
  import { lorebookApi, type LorebookListItem } from '@/api/isekai/lorebook';

  const ACard = Card;
  const AButton = Button;
  const ATable = Table;
  const AInput = Input;
  const ATextarea = Input.TextArea;
  const AModal = Modal;
  const AForm = Form;
  const AFormItem = Form.Item;
  const ATag = Tag;
  const ASpace = Space;
  const AInputNumber = InputNumber;

  const { createMessage, createConfirm } = useMessage();

  const data = ref<LorebookListItem[]>([]);
  const loading = ref(false);
  const showModal = ref(false);
  const saving = ref(false);
  const editingId = ref<string | null>(null);
  const filterTag = ref('');

  const pagination = reactive({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    pageSizeOptions: ['10', '20', '50'],
  });

  const form = reactive({
    title: '',
    content: '',
    tags: [] as string[],
    priority: 0,
  });

  // Tag input management
  const tagInputVisible = ref(false);
  const tagInputValue = ref('');
  const tagInputRef = ref();

  function showTagInput() {
    tagInputVisible.value = true;
    nextTick(() => {
      tagInputRef.value?.focus();
    });
  }

  function addTag() {
    const val = tagInputValue.value.trim();
    if (val && !form.tags.includes(val)) {
      form.tags.push(val);
    }
    tagInputValue.value = '';
    tagInputVisible.value = false;
  }

  function removeTag(index: number) {
    form.tags.splice(index, 1);
  }

  const columns = [
    { title: '标题', dataIndex: 'title', ellipsis: true },
    { title: '标签', key: 'tags', width: 300 },
    { title: '优先级', dataIndex: 'priority', width: 80 },
    { title: '更新时间', key: 'updated_at', width: 180 },
    { title: '操作', key: 'actions', width: 160 },
  ];

  function rowKey(record: LorebookListItem) {
    return record.id;
  }

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString();
  }

  function handleTableChange(pag: any) {
    pagination.current = pag.current;
    pagination.pageSize = pag.pageSize;
    loadData();
  }

  function onFilterChange(e: any) {
    // Handle clear button
    if (e?.target?.value === '' || e === '') {
      loadData();
    }
  }

  async function loadData() {
    loading.value = true;
    try {
      const res = await lorebookApi.list(
        pagination.current,
        pagination.pageSize,
        filterTag.value || undefined,
      );
      data.value = res.items;
      pagination.total = res.total;
    } catch (err: any) {
      createMessage.error(err?.message || '加载失败');
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
      createMessage.error(err?.message || '加载详情失败');
    }
  }

  async function handleSave() {
    if (!form.title.trim()) {
      createMessage.warning('请填写标题');
      return;
    }
    if (!form.content.trim()) {
      createMessage.warning('请填写内容');
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
        createMessage.success('更新成功');
      } else {
        await lorebookApi.create({
          title: form.title,
          content: form.content,
          tags: form.tags,
          priority: form.priority,
        });
        createMessage.success('创建成功');
      }
      showModal.value = false;
      loadData();
    } catch (err: any) {
      createMessage.error(err?.message || '保存失败');
    } finally {
      saving.value = false;
    }
  }

  function handleDelete(row: LorebookListItem) {
    createConfirm({
      iconType: 'warning',
      title: '确认删除',
      content: `确定要删除「${row.title}」吗？此操作为软删除。`,
      okText: '删除',
      cancelText: '取消',
      onOk: async () => {
        try {
          await lorebookApi.delete(row.id);
          createMessage.success('删除成功');
          loadData();
        } catch (err: any) {
          createMessage.error(err?.message || '删除失败');
        }
      },
    });
  }

  onMounted(() => {
    loadData();
  });
</script>
