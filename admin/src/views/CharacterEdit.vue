<template>
  <div>
    <n-space justify="space-between" align="center" style="margin-bottom: 16px">
      <h1 style="margin: 0">编辑角色: {{ character?.name || characterId }}</h1>
      <n-button @click="$router.push('/characters')">返回列表</n-button>
    </n-space>

    <n-card title="基本信息" style="margin-bottom: 16px">
      <n-descriptions :column="1" bordered v-if="character">
        <n-descriptions-item label="ID">{{ character.id }}</n-descriptions-item>
        <n-descriptions-item label="名称">{{ character.name }}</n-descriptions-item>
        <n-descriptions-item label="描述">{{ character.description || '无' }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-card title="内在驱动 (Inner Drive)">
      <n-form :model="form" v-if="character">
        <n-form-item label="渴望 (Desire)">
          <n-input v-model:value="form.desire" type="textarea" placeholder="角色的内在渴望" :rows="2" />
        </n-form-item>
        <n-form-item label="恐惧 (Fear)">
          <n-input v-model:value="form.fear" type="textarea" placeholder="角色的深层恐惧" :rows="2" />
        </n-form-item>
        <n-form-item label="秘密 (Secret)">
          <n-input v-model:value="form.secret" type="textarea" placeholder="角色的隐藏秘密" :rows="2" />
          <template #feedback>
            <span style="color: #f0a020">⚠️ 敏感信息，请谨慎填写</span>
          </template>
        </n-form-item>
        <n-space>
          <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { characterApi, type Character } from '@/api/character';

const route = useRoute();
const message = useMessage();

const characterId = route.params.characterId as string;
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
    message.error(err.message || '加载角色失败');
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
    message.success('保存成功');
  } catch (err: any) {
    message.error(err.message || '保存失败');
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  loadCharacter();
});
</script>
