<template>
  <div class="page-bg">
    <div class="gallery-page">
      <div class="page-header fade-in-up">
        <div class="page-header-info">
          <h1 class="gradient-text">{{ $t('gallery.title') }}</h1>
          <p class="page-subtitle">{{ $t('gallery.subtitle') }}</p>
        </div>
      </div>

      <div class="gallery-tabs fade-in-up" style="animation-delay: 0.1s">
        <n-tabs v-model:value="activeTab" type="segment" size="large">
          <n-tab-pane name="cgs" :tab="$t('galleryExtra.cgCollection')">
            <!-- 图鉴列表 -->
            <n-spin :show="loadingCollections" v-if="!activeCollection">
              <div class="cg-grid">
                <div v-for="col in collections" :key="col.id" class="cg-card glass-card" @click="openCollection(col)">
                  <div class="cg-thumbnail">
                    <img v-if="col.cover_url" :src="col.cover_url" class="cg-cover-img" />
                    <div v-else class="cg-placeholder">
                      <span class="cg-emoji">🎨</span>
                    </div>
                    <div class="cg-progress-badge">{{ col.items_unlocked }}/{{ col.items_count }}</div>
                  </div>
                  <div class="cg-info">
                    <div class="cg-name">{{ col.name }}</div>
                    <div class="cg-script">{{ col.description || '' }}</div>
                    <n-progress type="line" :percentage="Math.round(col.items_unlocked / col.items_count * 100)" :height="4" :show-indicator="false" :color="'#86efac'" rail-color="rgba(167,139,250,0.08)" style="margin-top:6px" />
                  </div>
                </div>
              </div>
              <n-empty v-if="!loadingCollections && collections.length === 0" :description="$t('gallery.noCollections')" />
            </n-spin>
            <!-- 图鉴子项 -->
            <div v-else>
              <n-button text @click="activeCollection = null" class="back-to-collections">← 返回图鉴列表</n-button>
              <h3 class="cg-collection-title">{{ activeCollection.name }}</h3>
              <p class="cg-collection-desc">{{ activeCollection.description }}</p>
              <n-spin :show="loadingCGItems">
                <div class="cg-items-grid">
                  <div v-for="item in cgItems" :key="item.id" class="cg-item-card glass-card" :class="{ locked: item.unlock_status === 'locked' }" @click="item.unlock_status === 'unlocked' ? previewCG(item) : null">
                    <div class="cg-item-thumb">
                      <img :src="item.thumbnail_url" class="cg-item-img" />
                      <div v-if="item.unlock_status === 'locked'" class="cg-lock-overlay">
                        <span class="cg-lock-icon">🔒</span>
                        <span class="cg-lock-hint">{{ item.unlock_condition }}</span>
                      </div>
                    </div>
                    <div class="cg-item-info">
                      <div class="cg-item-name">{{ item.title }}</div>
                      <div class="cg-item-script">{{ item.script_name }}</div>
                    </div>
                  </div>
                </div>
                <n-empty v-if="!loadingCGItems && cgItems.length === 0" description="暂无CG" />
              </n-spin>
            </div>
            <div v-if="collections.length > 0 && !activeCollection" class="gallery-stats">
              {{ $t('galleryExtra.totalCollections', { n: collections.length }) }}
            </div>
          </n-tab-pane>

          <n-tab-pane name="characters" :tab="$t('galleryExtra.characterGuide')">
            <n-spin :show="loadingAffections">
              <div class="character-grid">
                <div v-for="char in characters" :key="char.character_id" class="char-card glass-card">
                  <div class="char-avatar">
                    <span class="char-avatar-text">{{ getInitial(char.character_name || char.character_id) }}</span>
                  </div>
                  <div class="char-info">
                    <h3 class="char-name">{{ char.character_name || char.character_id.slice(0, 8) }}</h3>
                    <div class="char-affection">
                      <n-progress type="line" :percentage="char.value" :height="6" :border-radius="3"
                        :color="affectionColor(char.value)" rail-color="rgba(167, 139, 250, 0.1)" />
                      <div class="affection-label">
                        {{ affectionLabel(char.value) }} · {{ char.value }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <n-empty v-if="!loadingAffections && characters.length === 0" :description="$t('gallery.noCharacters')" />
            </n-spin>
          </n-tab-pane>

          <n-tab-pane name="achievements" :tab="$t('galleryExtra.achievementWall')">
            <n-spin :show="loadingAchievements">
              <!-- 成就统计 -->
              <div v-if="achievements.length > 0" class="achievement-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ achievements.filter(a => a.is_unlocked).length }}</div>
                  <div class="stat-label">已解锁</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ achievements.length }}</div>
                  <div class="stat-label">总成就</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ Math.round(achievements.filter(a => a.is_unlocked).length / achievements.length * 100) }}%</div>
                  <div class="stat-label">完成度</div>
                </div>
              </div>
              
              <!-- 成就卡片网格 -->
              <div class="achievement-grid">
                <div v-for="ach in achievements" :key="ach.id" class="achievement-card glass-card"
                  :class="{ 'ach-unlocked': ach.is_unlocked, 'ach-locked': !ach.is_unlocked }">
                  <div class="ach-header">
                    <div class="ach-icon">{{ ach.is_unlocked ? '🏆' : '🔒' }}</div>
                    <div v-if="ach.reward && ach.reward.amount" class="ach-reward">💎 {{ ach.reward.amount }}</div>
                  </div>
                  <div class="ach-body">
                    <div class="ach-name">{{ ach.name || ach.id.slice(0, 8) }}</div>
                    <div class="ach-desc">{{ ach.description || '' }}</div>
                    <!-- 进度条 -->
                    <div v-if="ach.progress && ach.progress.percentage !== undefined" class="ach-progress">
                      <n-progress 
                        type="line" 
                        :percentage="ach.progress.percentage" 
                        :height="4" 
                        :show-indicator="false"
                        :color="ach.is_unlocked ? '#86efac' : '#a78bfa'"
                        rail-color="rgba(167,139,250,0.1)"
                      />
                      <div class="progress-text">{{ ach.progress.current }}/{{ ach.progress.target }}</div>
                    </div>
                    <div v-if="ach.unlocked_at" class="ach-date">
                      <span class="date-icon">📅</span>
                      {{ formatDate(ach.unlocked_at) }}
                    </div>
                  </div>
                </div>
              </div>
              <n-empty v-if="!loadingAchievements && achievements.length === 0" :description="$t('galleryExtra.noAchievements')" />
            </n-spin>
          </n-tab-pane>
        </n-tabs>
      </div>

      <n-modal v-model:show="showCGModal" preset="card" :title="selectedCG?.title" style="max-width: 640px">
        <div v-if="selectedCG" class="cg-detail">
          <div class="cg-detail-image">
            <img :src="selectedCG.thumbnail_url" class="cg-full-img" />
          </div>
          <div class="cg-detail-meta">
            <span class="cg-detail-script">{{ selectedCG.script_name }}</span>
            <span class="cg-detail-condition">解锁条件：{{ selectedCG.unlock_condition }}</span>
          </div>
        </div>
      </n-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { api } from '@/api/http';

const { t } = useI18n();

interface Collection { id: string; name: string; description?: string; items_count: number; items_unlocked: number; cover_url: string; }
interface CGItem { id: string; collection_id: string; title: string; thumbnail_url: string; script_name: string; unlock_status: string; unlock_condition: string; }
interface Character { character_id: string; character_name?: string; value: number; }
interface Achievement { 
  id: string; 
  name?: string; 
  description?: string; 
  is_unlocked: boolean; 
  unlocked_at?: string;
  reward?: { type: string; amount: number; claimed: boolean };
  progress?: { current: number; target: number; percentage: number };
}

const message = useMessage();
const activeTab = ref('cgs');
const showCGModal = ref(false);
const selectedCG = ref<CGItem | null>(null);
const collections = ref<Collection[]>([]);
const cgItems = ref<CGItem[]>([]);
const activeCollection = ref<Collection | null>(null);
const loadingCGItems = ref(false);
const characters = ref<Character[]>([]);
const achievements = ref<Achievement[]>([]);
const loadingCollections = ref(false);
const loadingAffections = ref(false);
const loadingAchievements = ref(false);

function getInitial(name: string): string { return name.charAt(0).toUpperCase(); }
function formatDate(iso: string): string { return new Date(iso).toLocaleDateString(); }
function previewCG(cg: CGItem) { selectedCG.value = cg; showCGModal.value = true; }

async function openCollection(col: Collection) {
  activeCollection.value = col;
  loadingCGItems.value = true;
  try {
    const r = await api.get<{ items: CGItem[] }>(`/gallery/collections/${col.id}`);
    cgItems.value = r.items || [];
  } catch {
    message.error(t('common.error'));
  } finally {
    loadingCGItems.value = false;
  }
}

function affectionColor(value: number): string {
  if (value >= 80) return '#F43F5E';
  if (value >= 60) return '#A78BFA';
  if (value >= 40) return '#38BDF8';
  if (value >= 20) return '#F472B6';
  return '#9CA3AF';
}

function affectionLabel(value: number): string {
  if (value >= 80) return t('game.bestFriend');
  if (value >= 60) return t('game.close');
  if (value >= 40) return t('game.friend');
  if (value >= 20) return t('game.acquaintance');
  return t('game.stranger');
}

async function loadCollections() {
  loadingCollections.value = true;
  try {
    const r = await api.get<{ collections: Collection[] }>('/gallery/collections');
    collections.value = r.collections || [];
  } catch { message.error(t('common.error')); }
  finally { loadingCollections.value = false; }
}
async function loadCharacters() {
  loadingAffections.value = true;
  try { const r = await api.get<{ affections: Character[] }>('/affection'); characters.value = r.affections || []; }
  catch { message.error(t('common.error')); }
  finally { loadingAffections.value = false; }
}
async function loadAchievements() {
  loadingAchievements.value = true;
  try {
    const r = await api.get<{ achievements: Achievement[] }>('/users/me/achievements');
    achievements.value = r.achievements || [];
  } catch { message.error(t('common.error')); }
  finally { loadingAchievements.value = false; }
}

onMounted(() => { loadCollections(); loadCharacters(); loadAchievements(); });
</script>

<style scoped>
.gallery-page { max-width: 900px; margin: 0 auto; padding: 32px 16px 48px; }
.page-header { margin-bottom: 24px; }
.page-header-row { display: flex; align-items: center; margin-bottom: 12px; }
.back-btn { color: var(--text-muted) !important; font-size: 13px !important; padding: 0 !important; }
.page-header-info { display: flex; flex-direction: column; gap: 4px; }
.page-header h1 { font-size: 28px; font-weight: 700; margin: 0; }
.page-subtitle { color: var(--text-muted); font-size: 14px; margin: 0; }
.gallery-tabs { margin-bottom: 24px; }

/* 图鉴列表 */
.cg-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-bottom: 16px; }
.cg-card { cursor: pointer; overflow: hidden; transition: all 0.3s ease; padding: 0; }
.cg-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(139, 92, 246, 0.15); }
.cg-thumbnail { width: 100%; aspect-ratio: 16/9; position: relative; overflow: hidden; }
.cg-cover-img { width: 100%; height: 100%; object-fit: cover; }
.cg-placeholder { width: 100%; height: 100%; background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(249, 168, 212, 0.1)); display: flex; align-items: center; justify-content: center; }
.cg-emoji { font-size: 36px; }
.cg-progress-badge { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.7); color: #86efac; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 8px; backdrop-filter: blur(4px); }
.cg-info { padding: 14px 16px; }
.cg-name { font-size: 15px; font-weight: 700; color: var(--text-main); margin-bottom: 4px; }
.cg-script { font-size: 12px; color: var(--text-muted); line-height: 1.4; }

/* CG 子项 */
.back-to-collections { color: var(--text-muted) !important; font-size: 13px !important; margin-bottom: 12px; }
.cg-collection-title { font-size: 20px; font-weight: 700; color: var(--text-main); margin: 0 0 4px; }
.cg-collection-desc { font-size: 13px; color: var(--text-muted); margin: 0 0 16px; }
.cg-items-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
.cg-item-card { cursor: pointer; overflow: hidden; padding: 0; transition: all 0.3s ease; }
.cg-item-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(139, 92, 246, 0.12); }
.cg-item-card.locked { cursor: default; opacity: 0.7; }
.cg-item-thumb { width: 100%; aspect-ratio: 16/10; position: relative; overflow: hidden; }
.cg-item-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; }
.cg-item-card:hover .cg-item-img { transform: scale(1.05); }
.cg-lock-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(6px); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; }
.cg-lock-icon { font-size: 28px; }
.cg-lock-hint { font-size: 11px; color: rgba(255,255,255,0.8); text-align: center; padding: 0 8px; }
.cg-item-info { padding: 10px 12px; }
.cg-item-name { font-size: 13px; font-weight: 600; color: var(--text-main); margin-bottom: 2px; }
.cg-item-script { font-size: 11px; color: var(--text-muted); }

.gallery-stats { text-align: center; color: var(--text-muted); font-size: 13px; padding: 8px 0; }

/* 角色图鉴 */
.character-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.char-card { padding: 24px; display: flex; gap: 16px; align-items: flex-start; }
.char-avatar { width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, #4F46E5, #818CF8); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.char-avatar-text { color: white; font-size: 24px; font-weight: 700; }
.char-info { flex: 1; min-width: 0; }
.char-name { font-size: 16px; font-weight: 700; margin: 0 0 4px; }
.char-affection { margin-bottom: 8px; }
.affection-label { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

/* 成就墙 */
.achievement-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(167, 139, 250, 0.05);
  border-radius: 12px;
}
.achievement-stats .stat-item {
  text-align: center;
}
.achievement-stats .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-primary, #a78bfa);
  margin-bottom: 4px;
}
.achievement-stats .stat-label {
  font-size: 13px;
  color: var(--text-muted, #9ca3af);
}
.achievement-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 16px; }
.achievement-card { padding: 0; text-align: left; transition: all 0.3s ease; overflow: hidden; }
.achievement-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(139, 92, 246, 0.15); }
.ach-unlocked { border-color: rgba(134, 239, 172, 0.3) !important; }
.ach-locked { opacity: 0.7; }
.ach-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(249, 168, 212, 0.05));
  border-bottom: 1px solid rgba(167, 139, 250, 0.1);
}
.ach-icon { font-size: 36px; }
.ach-reward {
  font-size: 12px;
  font-weight: 600;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
  padding: 4px 8px;
  border-radius: 8px;
}
.ach-body { padding: 16px; }
.ach-name { font-size: 15px; font-weight: 700; margin-bottom: 6px; color: var(--text-main); }
.ach-desc { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; line-height: 1.5; }
.ach-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.ach-progress .progress-text {
  font-size: 11px;
  color: var(--text-muted);
  min-width: 32px;
}
.ach-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
}
.date-icon { font-size: 12px; }

/* CG 详情弹框 */
.cg-detail-image { width: 100%; border-radius: 12px; overflow: hidden; margin-bottom: 12px; }
.cg-full-img { width: 100%; display: block; }
.cg-detail-meta { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); }
.cg-detail-script { font-weight: 600; color: var(--text-main); }
.cg-detail-condition { color: var(--text-muted); }
</style>
