<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl m-0">编辑角色: {{ character?.name || characterId }}</h1>
      <a-button @click="$router.push('/isekai/characters')">返回列表</a-button>
    </div>

    <a-card title="基本信息" class="mb-4" v-if="character">
      <a-descriptions :column="1" bordered>
        <a-descriptions-item label="ID">{{ character.id }}</a-descriptions-item>
        <a-descriptions-item label="名称">{{ character.name }}</a-descriptions-item>
        <a-descriptions-item label="描述">{{ character.description || '无' }}</a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-card title="内在驱动 (Inner Drive)">
      <a-form :model="form" layout="vertical" v-if="character">
        <a-form-item label="渴望 (Desire)">
          <a-textarea
            v-model:value="form.desire"
            placeholder="角色的内在渴望"
            :rows="2"
          />
        </a-form-item>
        <a-form-item label="恐惧 (Fear)">
          <a-textarea
            v-model:value="form.fear"
            placeholder="角色的深层恐惧"
            :rows="2"
          />
        </a-form-item>
        <a-form-item label="秘密 (Secret)">
          <a-textarea
            v-model:value="form.secret"
            placeholder="角色的隐藏秘密"
            :rows="2"
          />
          <span style="color: #f0a020">⚠️ 敏感信息，请谨慎填写</span>
        </a-form-item>
        <a-space>
          <a-button type="primary" :loading="saving" @click="handleSave">保存</a-button>
        </a-space>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import { Card, Button, Form, Input, Space, Descriptions } from 'ant-design-vue';
  import { useMessage } from '@/hooks/web/useMessage';
  import { characterApi, type Character } from '@/api/isekai/character';

  const ACard = Card;
  const AButton = Button;
  const AForm = Form;
  const AFormItem = Form.Item;
  const ATextarea = Input.TextArea;
  const ASpace = Space;
  const ADescriptions = Descriptions;
  const ADescriptionsItem = Descriptions.Item;

  const route = useRoute();
  const { createMessage } = useMessage();

  const characterId = route.params.id as string;
  const character = ref<Character | null>(null);
  const saving = ref(false);

  const form = reactive({
    desire: '',
    fear: '',
    secret: '',
  });

  async function loadCharacter() {
    try {
      const res = await characterApi.get(characterId);
      character.value = res;
      form.desire = res.desire || '';
      form.fear = res.fear || '';
      form.secret = res.secret || '';
    } catch (err: any) {
      createMessage.error(err?.message || '加载角色失败');
    }
  }

  async function handleSave() {
    saving.value = true;
    try {
      await characterApi.updateInnerDrive(characterId, {
        desire: form.desire || null,
        fear: form.fear || null,
        secret: form.secret || null,
      });
      createMessage.success('保存成功');
    } catch (err: any) {
      createMessage.error(err?.message || '保存失败');
    } finally {
      saving.value = false;
    }
  }

  onMounted(() => {
    loadCharacter();
  });
</script>
