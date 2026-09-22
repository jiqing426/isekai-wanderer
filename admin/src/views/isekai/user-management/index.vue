<template>
  <div class="p-4">
    <a-card title="用户管理">
      <!-- Search -->
      <div class="mb-4">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索邮箱或显示名"
          style="width: 300px"
          allow-clear
          @search="handleSearch"
        />
      </div>

      <!-- Table -->
      <a-table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :row-key="(record: UserSummary) => record.id"
        :pagination="{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showTotal: (t: number) => `共 ${t} 条`,
        }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'is_admin'">
            <a-switch
              :checked="record.is_admin"
              :loading="togglingId === record.id"
              @change="(checked: boolean) => toggleAdmin(record, checked)"
            />
          </template>
          <template v-if="column.key === 'email_verified'">
            <a-tag :color="record.email_verified ? 'green' : 'orange'">
              {{ record.email_verified ? '已验证' : '未验证' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-if="column.key === 'last_login'">
            {{ record.last_login ? formatDate(record.last_login) : '—' }}
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted } from 'vue';
  import { Card, Table, Input, Switch, Tag } from 'ant-design-vue';
  import { useMessage } from '@/hooks/web/useMessage';
  import {
    userManagementApi,
    type UserSummary,
  } from '@/api/isekai/userManagement';

  const ACard = Card;
  const ATable = Table;
  const AInputSearch = Input.Search;
  const ASwitch = Switch;
  const ATag = Tag;

  const { createMessage } = useMessage();

  const data = ref<UserSummary[]>([]);
  const loading = ref(false);
  const searchText = ref('');
  const page = ref(1);
  const pageSize = ref(20);
  const total = ref(0);
  const togglingId = ref<string>('');

  const columns = [
    { title: '邮箱', dataIndex: 'email', width: 250, ellipsis: true },
    { title: '显示名', dataIndex: 'display_name', ellipsis: true },
    { title: '管理员', key: 'is_admin', width: 100 },
    { title: '邮箱验证', key: 'email_verified', width: 120 },
    { title: '订阅', dataIndex: 'subscription_tier', width: 100 },
    { title: '创建时间', key: 'created_at', width: 180 },
    { title: '最后登录', key: 'last_login', width: 180 },
  ];

  function formatDate(dateStr?: string): string {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString();
  }

  async function loadData() {
    loading.value = true;
    try {
      const res = await userManagementApi.getAll({
        page: page.value,
        page_size: pageSize.value,
        search: searchText.value || undefined,
      });
      data.value = res.items;
      total.value = res.total;
    } catch (err: any) {
      createMessage.error(err?.message || '加载用户列表失败');
    } finally {
      loading.value = false;
    }
  }

  function handleSearch() {
    page.value = 1;
    loadData();
  }

  function handleTableChange(pagination: any) {
    page.value = pagination.current;
    pageSize.value = pagination.pageSize;
    loadData();
  }

  async function toggleAdmin(record: UserSummary, checked: boolean) {
    togglingId.value = record.id;
    try {
      await userManagementApi.update(record.id, { is_admin: checked });
      record.is_admin = checked;
      createMessage.success(
        checked ? '已设为管理员' : '已取消管理员',
      );
    } catch (err: any) {
      createMessage.error(err?.message || '更新失败');
      // Revert will happen naturally since record wasn't updated
    } finally {
      togglingId.value = '';
    }
  }

  onMounted(() => {
    loadData();
  });
</script>
