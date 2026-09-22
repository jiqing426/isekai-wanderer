<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl m-0">场景配置管理</h1>
      <a-button type="primary" @click="openCreate">+ 新建配置</a-button>
    </div>

    <!-- Filters -->
    <div class="mb-4 flex gap-2">
      <a-input
        v-model:value="filterScriptId"
        placeholder="Script ID"
        allow-clear
        style="width: 200px"
      />
      <a-input
        v-model:value="filterRouteId"
        placeholder="Route ID"
        allow-clear
        style="width: 200px"
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
        :pagination="false"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'tags'">
            <a-tag v-for="tag in record.tags" :key="tag" color="green">{{ tag }}</a-tag>
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
      :title="editingNodeId ? '编辑配置' : '新建配置'"
      width="600px"
      :confirm-loading="saving"
      @ok="handleSave"
      @cancel="showModal = false"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="Node ID">
          <a-input
            v-model:value="form.nodeId"
            placeholder="Node UUID"
            :disabled="!!editingNodeId"
          />
        </a-form-item>
        <a-form-item label="场景名称">
          <a-input v-model:value="form.sceneName" placeholder="场景名称" :maxlength="200" />
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
        <a-form-item label="描述">
          <a-textarea
            v-model:value="form.description"
            placeholder="场景描述"
            :rows="4"
            :maxlength="5000"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted, nextTick } from 'vue';
  import { Card, Button, Table, Input, Modal, Form, Tag, Space } from 'ant-design-vue';
  import { useMessage } from '@/hooks/web/useMessage';
  import { sceneConfigApi, type SceneConfig } from '@/api/isekai/sceneConfig';

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

  const { createMessage, createConfirm } = useMessage();

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
    { title: 'Node ID', dataIndex: 'node_id', width: 280, ellipsis: true },
    { title: '场景名称', dataIndex: 'scene_name', ellipsis: true },
    { title: '标签', key: 'tags', width: 250 },
    { title: '描述', dataIndex: 'description', ellipsis: true },
    { title: '更新时间', key: 'updated_at', width: 180 },
    { title: '操作', key: 'actions', width: 160 },
  ];

  function rowKey(record: SceneConfig) {
    return record.id;
  }

  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString();
  }

  async function loadData() {
    loading.value = true;
    try {
      const res = await sceneConfigApi.list(
        filterScriptId.value || undefined,
        filterRouteId.value || undefined,
      );
      data.value = res;
    } catch (err: any) {
      createMessage.error(err?.message || '加载失败');
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
      createMessage.warning('请填写 Node ID');
      return;
    }
    if (!form.sceneName.trim()) {
      createMessage.warning('请填写场景名称');
      return;
    }
    saving.value = true;
    try {
      await sceneConfigApi.upsert(form.nodeId, {
        scene_name: form.sceneName,
        tags: form.tags,
        description: form.description || undefined,
      });
      createMessage.success(editingNodeId.value ? '更新成功' : '创建成功');
      showModal.value = false;
      loadData();
    } catch (err: any) {
      createMessage.error(err?.message || '保存失败');
    } finally {
      saving.value = false;
    }
  }

  function handleDelete(row: SceneConfig) {
    createConfirm({
      iconType: 'warning',
      title: '确认删除',
      content: `确定要删除 Node「${row.node_id}」的场景配置吗？`,
      okText: '删除',
      cancelText: '取消',
      onOk: async () => {
        try {
          await sceneConfigApi.delete(row.node_id);
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
