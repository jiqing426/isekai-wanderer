<template>
  <div class="p-4">
    <a-card title="系统配置管理" :loading="loading">
      <!-- Email Config -->
      <template v-for="cat in categories" :key="cat">
        <a-divider v-if="cat === categories[0]" />
        <div :key="cat">
          <h3 class="mb-3 font-bold">{{ categoryLabel(cat) }}</h3>
          <a-form layout="vertical">
            <a-form-item
              v-for="item in groupedConfigs[cat] || []"
              :key="item.key"
              :label="item.description || item.key"
            >
              <a-input-password
                v-if="item.is_secret"
                v-model:value="formValues[item.key]"
                placeholder="••••••••"
                allow-clear
              />
              <a-input
                v-else
                v-model:value="formValues[item.key]"
                :placeholder="item.description || item.key"
                allow-clear
              />
            </a-form-item>
          </a-form>
          <a-space>
            <a-button
              type="primary"
              :loading="savingCat[cat]"
              @click="saveCategory(cat)"
            >
              保存{{ categoryLabel(cat) }}
            </a-button>
          </a-space>
          <a-divider />
        </div>
      </template>
    </a-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted } from 'vue';
  import { Card, Input, InputPassword, Form, Button, Space, Divider } from 'ant-design-vue';
  import { useMessage } from '@/hooks/web/useMessage';
  import { systemConfigApi, type SystemConfigItem } from '@/api/isekai/systemConfig';

  const ACard = Card;
  const AInput = Input;
  const AInputPassword = InputPassword;
  const AForm = Form;
  const AFormItem = Form.Item;
  const AButton = Button;
  const ASpace = Space;
  const ADivider = Divider;

  const { createMessage } = useMessage();

  const loading = ref(false);
  const savingCat = reactive<Record<string, boolean>>({});
  const configs = ref<SystemConfigItem[]>([]);
  const formValues = reactive<Record<string, string>>({});
  const originalValues = reactive<Record<string, string>>({});

  const categories = computed(() => {
    const cats = [...new Set(configs.value.map((c) => c.category || 'general'))];
    // Sort: email, general, security, then others
    const order = ['email', 'general', 'security'];
    cats.sort((a, b) => {
      const ia = order.indexOf(a);
      const ib = order.indexOf(b);
      if (ia !== -1 && ib !== -1) return ia - ib;
      if (ia !== -1) return -1;
      if (ib !== -1) return 1;
      return a.localeCompare(b);
    });
    return cats;
  });

  const groupedConfigs = computed(() => {
    const groups: Record<string, SystemConfigItem[]> = {};
    for (const c of configs.value) {
      const cat = c.category || 'general';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(c);
    }
    return groups;
  });

  function categoryLabel(cat: string): string {
    const labels: Record<string, string> = {
      email: '邮件配置',
      general: '通用配置',
      security: '安全配置',
    };
    return labels[cat] || cat;
  }

  async function loadData() {
    loading.value = true;
    try {
      const res = await systemConfigApi.getAll();
      // The API may return SystemConfigItem[] or SystemConfigResponse[] with is_secret field
      const items = (res as any[]).map((item) => ({
        ...item,
        is_secret: item.is_secret ?? false,
      })) as SystemConfigItem[];
      configs.value = items;
      for (const item of items) {
        const val = item.value || '';
        formValues[item.key] = val;
        originalValues[item.key] = val;
      }
    } catch (err: any) {
      createMessage.error(err?.message || '加载配置失败');
    } finally {
      loading.value = false;
    }
  }

  async function saveCategory(cat: string) {
    savingCat[cat] = true;
    const items = groupedConfigs.value[cat] || [];
    const changed = items.filter(
      (item) => formValues[item.key] !== originalValues[item.key],
    );

    if (changed.length === 0) {
      createMessage.info('没有更改');
      savingCat[cat] = false;
      return;
    }

    try {
      for (const item of changed) {
        const newVal = formValues[item.key] || '';
        await systemConfigApi.update(item.key, newVal);
        originalValues[item.key] = newVal;
      }
      createMessage.success(`${categoryLabel(cat)} 保存成功`);
    } catch (err: any) {
      createMessage.error(err?.message || '保存失败');
    } finally {
      savingCat[cat] = false;
    }
  }

  onMounted(() => {
    loadData();
  });
</script>
