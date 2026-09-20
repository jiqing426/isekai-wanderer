<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- 左侧导航栏 (桌面端) -->
      <aside class="settings-sidebar">
        <h2 class="sidebar-title">{{ $t('settings.title') }}</h2>
        <nav class="sidebar-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="nav-item"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <span class="nav-icon">{{ tab.icon }}</span>
            <span class="nav-label">{{ tab.label }}</span>
          </button>
        </nav>
      </aside>

      <!-- 移动端顶部标签栏 -->
      <div class="mobile-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="mobile-tab"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 右侧内容区 -->
      <main class="settings-content">
        <!-- 个人资料 -->
        <div v-if="activeTab === 'profile'" class="content-panel">
          <h3 class="panel-title">{{ $t('settings.profile') }}</h3>
          
          <div class="avatar-section">
            <div class="avatar-preview">
              <img v-if="userAvatar && !avatarFailed" :src="userAvatar" alt="Avatar" @error="avatarFailed = true" />
              <span v-else class="avatar-placeholder">{{ userInitial }}</span>
            </div>
            <label class="upload-btn">
              <input 
                type="file" 
                accept="image/*" 
                @change="handleAvatarUpload"
                style="display: none"
              />
              📷 更换头像
            </label>
            <span class="upload-hint">最大 5MB</span>
          </div>

          <div class="form-group">
            <label>{{ $t('settings.nickname') }}</label>
            <input 
              v-model="userNickname"
              type="text"
              :placeholder="$t('settings.nicknamePlaceholder')"
              maxlength="20"
            />
            <span class="char-count">{{ userNickname.length }}/20</span>
          </div>

          <div class="form-group">
            <label>{{ $t('settings.signature') }}</label>
            <textarea
              v-model="userSignature"
              :placeholder="$t('settings.signaturePlaceholder')"
              maxlength="200"
              rows="3"
            ></textarea>
            <span class="char-count">{{ userSignature.length }}/200</span>
          </div>

          <div class="form-group">
            <label>{{ $t('settings.email') }}</label>
            <input 
              :value="userEmail"
              type="email"
              disabled
              class="readonly"
            />
          </div>

          <button 
            class="save-btn"
            @click="saveProfile"
            :disabled="savingProfile"
          >
            {{ savingProfile ? $t('common.saving') : $t('common.save') }}
          </button>
        </div>

        <!-- 播放偏好 -->
        <div v-if="activeTab === 'play'" class="content-panel">
          <h3 class="panel-title">{{ $t('settings.playPreferences') }}</h3>

          <div class="setting-group">
            <label>{{ $t('settings.typingSpeed') }}</label>
            <select v-model="playSettings.typing_speed" @change="savePlaySettings">
              <option value="slow">慢速</option>
              <option value="normal">正常</option>
              <option value="fast">快速</option>
              <option value="instant">即时</option>
            </select>
          </div>

          <div class="setting-group">
            <div class="toggle-row">
              <span>{{ $t('settings.autoPlay') }}</span>
              <label class="toggle-switch">
                <input 
                  type="checkbox" 
                  v-model="playSettings.auto_play"
                  @change="savePlaySettings"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-group" v-if="playSettings.auto_play">
            <label>自动播放延迟 ({{ localAutoPlayDelay }}ms)</label>
            <input 
              type="range" 
              v-model.number="localAutoPlayDelay"
              min="1000"
              max="10000"
              step="500"
            />
          </div>

          <div class="setting-group">
            <label>BGM 音量 ({{ localBgmVolume }}%)</label>
            <input 
              type="range" 
              v-model.number="localBgmVolume"
              min="0"
              max="100"
            />
          </div>

          <div class="setting-group">
            <label>音效音量 ({{ localSfxVolume }}%)</label>
            <input 
              type="range" 
              v-model.number="localSfxVolume"
              min="0"
              max="100"
            />
          </div>

          <button 
            class="save-btn"
            @click="savePlaySettings"
            :disabled="savingPlaySettings"
          >
            {{ savingPlaySettings ? $t('common.saving') : $t('common.save') }}
          </button>
        </div>

        <!-- 通知推送 -->
        <div v-if="activeTab === 'notify'" class="content-panel">
          <h3 class="panel-title">{{ $t('settings.notifications') }}</h3>

          <div class="notify-list">
            <div class="notify-item">
              <div class="notify-info">
                <span class="notify-label">版本更新通知</span>
                <span class="notify-desc">当应用有新版本时通知</span>
              </div>
              <label class="toggle-switch">
                <input 
                  type="checkbox" 
                  v-model="notifySettings.update_notify"
                  @change="saveNotifySettings"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div class="notify-item">
              <div class="notify-info">
                <span class="notify-label">活动提醒</span>
                <span class="notify-desc">限时活动开始提醒</span>
              </div>
              <label class="toggle-switch">
                <input 
                  type="checkbox" 
                  v-model="notifySettings.activity_reminder"
                  @change="saveNotifySettings"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div class="notify-item">
              <div class="notify-info">
                <span class="notify-label">签到推送</span>
                <span class="notify-desc">每日签到提醒</span>
              </div>
              <label class="toggle-switch">
                <input 
                  type="checkbox" 
                  v-model="notifySettings.checkin_push"
                  @change="saveNotifySettings"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div class="notify-item">
              <div class="notify-info">
                <span class="notify-label">新剧本上架</span>
                <span class="notify-desc">有新剧本发布时通知</span>
              </div>
              <label class="toggle-switch">
                <input 
                  type="checkbox" 
                  v-model="notifySettings.new_script"
                  @change="saveNotifySettings"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        <!-- 隐私安全 -->
        <div v-if="activeTab === 'privacy'" class="content-panel">
          <h3 class="panel-title">{{ $t('settings.privacySecurity') }}</h3>

          <div class="privacy-section">
            <h4>修改密码</h4>
            <p class="section-desc">定期修改密码可以提高账户安全性</p>
            <button class="action-btn" @click="showPasswordModal = true">
              修改密码
            </button>
          </div>

          <div class="privacy-section">
            <h4>登录设备管理</h4>
            <p class="section-desc">查看和管理已登录的设备</p>
            
            <div class="device-list" v-if="devices.length > 0">
              <div 
                v-for="device in devices" 
                :key="device.id"
                class="device-item"
                :class="{ current: device.is_current }"
              >
                <div class="device-info">
                  <div class="device-name">
                    {{ device.device_name }}
                    <span v-if="device.is_current" class="current-badge">当前设备</span>
                  </div>
                  <div class="device-meta">
                    {{ device.browser }} · {{ device.os }}
                  </div>
                  <div class="device-meta">
                    最后活跃: {{ formatTime(device.last_active_at) }}
                  </div>
                </div>
                <button 
                  v-if="!device.is_current"
                  class="logout-btn"
                  @click="handleLogoutDevice(device.id)"
                  :disabled="loggingOutDevice === device.id"
                >
                  下线
                </button>
              </div>
            </div>
            <div v-else class="empty-state">
              暂无设备信息
            </div>
          </div>
        </div>

        <!-- 会员管理 -->
        <div v-if="activeTab === 'member'" class="content-panel">
          <h3 class="panel-title">{{ $t('settings.membership') }}</h3>

          <div class="member-card">
            <div class="member-header">
              <div class="member-tier">
                <span class="tier-icon">{{ getTierIcon(memberInfo?.tier || authStore.user?.subscription_tier) }}</span>
                <span class="tier-name">{{ getTierName(memberInfo?.tier || authStore.user?.subscription_tier) }}</span>
              </div>
              <span class="member-status" :class="memberInfo?.status">
                {{ getStatusText(memberInfo?.status) }}
              </span>
            </div>

            <div class="member-details">
              <div class="detail-row">
                <span class="detail-label">会员时间</span>
                <span class="detail-value">
                  {{ memberInfo?.member_since ? formatDate(memberInfo.member_since) : '-' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">到期时间</span>
                <span class="detail-value">
                  {{ memberInfo?.expires_at ? formatDate(memberInfo.expires_at) : '-' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">自动续费</span>
                <span class="detail-value">
                  {{ memberInfo?.auto_renew ? '已开启' : '未开启' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">碎片余额</span>
                <span class="detail-value">💎 {{ memberInfo?.fragment_balance || 0 }}</span>
              </div>
            </div>

            <div class="member-benefits" v-if="memberInfo?.benefits && memberInfo.benefits.length > 0">
              <h4>当前权益</h4>
              <div class="benefits-list">
                <div v-for="benefit in memberInfo.benefits" :key="benefit" class="benefit-item">
                  ✓ {{ getBenefitText(benefit) }}
                </div>
              </div>
            </div>

            <div class="member-actions">
              <button class="primary-btn" @click="router.push('/subscription')">
                {{ memberInfo?.tier === 'free' ? '升级会员' : '续费' }}
              </button>
              <button class="secondary-btn" @click="router.push('/fragment')">
                碎片商城
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click="showPasswordModal = false">
      <div class="modal-content" @click.stop>
        <h3>修改密码</h3>
        
        <div class="form-group">
          <label>当前密码</label>
          <input 
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入当前密码"
          />
        </div>

        <div class="form-group">
          <label>新密码</label>
          <input 
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码（至少8位）"
          />
        </div>

        <div class="form-group">
          <label>确认新密码</label>
          <input 
            v-model="passwordConfirm"
            type="password"
            placeholder="请再次输入新密码"
          />
        </div>

        <div class="modal-actions">
          <button class="cancel-btn" @click="showPasswordModal = false">
            取消
          </button>
          <button 
            class="confirm-btn" 
            @click="handleChangePassword"
            :disabled="changingPassword"
          >
            {{ changingPassword ? '提交中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useSubscriptionStore } from '@/stores/subscription';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useMessage } from 'naive-ui';
import { 
  getMe, 
  updateMe, 
  getPlaySetting, 
  updatePlaySetting,
  getNotifySetting,
  updateNotifySetting,
  getDevices,
  logoutDevice,
  getMemberInfo,
  changePassword,
  uploadAvatar
} from '@/api/user';
import type { 
  UserProfile, 
  PlaySetting, 
  NotifySetting, 
  LoginDevice, 
  MemberInfo 
} from '@/types/user';

const router = useRouter();
const { t } = useI18n();
const message = useMessage();

// 当前激活的标签
const activeTab = ref<'profile' | 'play' | 'notify' | 'privacy' | 'member'>('profile');

// 标签配置
const tabs = computed(() => [
  { key: 'profile' as const, icon: '👤', label: t('settings.profile') },
  { key: 'play' as const, icon: '🎮', label: t('settings.playPreferences') },
  { key: 'notify' as const, icon: '🔔', label: t('settings.notifications') },
  { key: 'privacy' as const, icon: '🔒', label: t('settings.privacySecurity') },
  { key: 'member' as const, icon: '💎', label: t('settings.membership') },
]);

// 个人资料
const userProfile = ref<UserProfile | null>(null);
const userAvatar = ref('');
const avatarFailed = ref(false);
const userNickname = ref('');
const userSignature = ref('');
const userEmail = ref('');
const savingProfile = ref(false);
const savingPlaySettings = ref(false);

const userInitial = computed(() => {
  return userNickname.value ? userNickname.value.charAt(0).toUpperCase() : 'U';
});

// 播放设置
const playSettings = ref<PlaySetting>({
  typing_speed: 'normal',
  auto_play: false,
  auto_play_delay_ms: 3000,
  bgm_volume: 80,
  sfx_volume: 100,
});

// 本地状态（用于range input，避免实时更新触发保存）
const localAutoPlayDelay = ref(playSettings.value.auto_play_delay_ms);
const localBgmVolume = ref(playSettings.value.bgm_volume);
const localSfxVolume = ref(playSettings.value.sfx_volume);

// 通知设置
const notifySettings = ref<NotifySetting>({
  update_notify: true,
  activity_reminder: true,
  ending_unlock: true,
  checkin_push: true,
  affection_change: true,
  new_script: false,
});

// 设备列表
const devices = ref<LoginDevice[]>([]);
const loggingOutDevice = ref<string | null>(null);

// 会员信息
const subscriptionStore = useSubscriptionStore();
// authStore for subscription_tier display (may be more recent than memberInfo)
const authStore = useAuthStore();
const memberInfo = ref<MemberInfo | null>(null);

// 修改密码
const showPasswordModal = ref(false);
const changingPassword = ref(false);
const passwordForm = ref({
  old_password: '',
  new_password: '',
});
const passwordConfirm = ref('');

// 加载个人资料
async function loadProfile() {
  try {
    const profile = await getMe();
    userProfile.value = profile;
    userAvatar.value = profile.avatar_url || '';
    userNickname.value = profile.display_name || '';
    userSignature.value = profile.signature || '';
    userEmail.value = profile.email || '';
  } catch (err) {
    console.error('加载个人资料失败:', err);
    message.error('加载个人资料失败');
  }
}

// 保存个人资料
async function saveProfile() {
  savingProfile.value = true;
  try {
    await updateMe({
      display_name: userNickname.value,
      avatar_url: userAvatar.value,
      signature: userSignature.value,
    });
    message.success('保存成功');
  } catch (err) {
    console.error('保存个人资料失败:', err);
    message.error('保存失败');
  } finally {
    savingProfile.value = false;
  }
}

// 处理头像上传
async function handleAvatarUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  // 验证文件大小
  if (file.size > 5 * 1024 * 1024) {
    message.error('头像大小不能超过5MB');
    return;
  }

  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  if (!validTypes.includes(file.type)) {
    message.error('只支持 jpg/png/gif/webp 格式');
    return;
  }

  try {
    // 上传头像
    const result = await uploadAvatar(file);
    userAvatar.value = result.avatar_url;
    message.success('头像上传成功');
  } catch (err: any) {
    console.error('头像上传失败:', err);
    message.error(err?.message || '上传失败，请重试');
  }
}

// 加载播放设置
async function loadPlaySettings() {
  try {
    const settings = await getPlaySetting();
    playSettings.value = settings;
  } catch (err) {
    console.error('加载播放设置失败:', err);
  }
}

// 保存播放设置
async function savePlaySettings() {
  savingPlaySettings.value = true;
  try {
    // 同步本地状态到 playSettings
    playSettings.value.auto_play_delay_ms = localAutoPlayDelay.value;
    playSettings.value.bgm_volume = localBgmVolume.value;
    playSettings.value.sfx_volume = localSfxVolume.value;
    await updatePlaySetting(playSettings.value);
    message.success('保存成功');
  } catch (err) {
    console.error('保存播放设置失败:', err);
    message.error('保存失败');
  } finally {
    savingPlaySettings.value = false;
  }
}

// 加载通知设置
async function loadNotifySettings() {
  try {
    const settings = await getNotifySetting();
    notifySettings.value = settings;
  } catch (err) {
    console.error('加载通知设置失败:', err);
  }
}

// 保存通知设置
async function saveNotifySettings() {
  try {
    await updateNotifySetting(notifySettings.value);
    message.success('保存成功');
  } catch (err) {
    console.error('保存通知设置失败:', err);
    message.error('保存失败');
  }
}

// 加载设备列表
async function loadDevices() {
  try {
    const response = await getDevices();
    devices.value = response.devices;
  } catch (err) {
    console.error('加载设备列表失败:', err);
  }
}

// 下线设备
async function handleLogoutDevice(deviceId: string) {
  loggingOutDevice.value = deviceId;
  try {
    await logoutDevice(deviceId);
    message.success('设备已下线');
    await loadDevices();
  } catch (err) {
    console.error('下线设备失败:', err);
    message.error('下线失败');
  } finally {
    loggingOutDevice.value = null;
  }
}

// 加载会员信息
async function loadMemberInfo() {
  try {
    const info = await getMemberInfo();
    memberInfo.value = info;
  } catch (err) {
    console.error('加载会员信息失败:', err);
  }
}

// 修改密码
async function handleChangePassword() {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    message.error('请填写完整');
    return;
  }

  if (passwordForm.value.new_password.length < 8) {
    message.error('新密码至少8位');
    return;
  }

  if (passwordForm.value.new_password !== passwordConfirm.value) {
    message.error('两次输入的密码不一致');
    return;
  }

  changingPassword.value = true;
  try {
    await changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    });
    message.success('密码修改成功');
    showPasswordModal.value = false;
    passwordForm.value = { old_password: '', new_password: '' };
    passwordConfirm.value = '';
  } catch (err: any) {
    console.error('修改密码失败:', err);
    message.error(err?.message || '修改失败');
  } finally {
    changingPassword.value = false;
  }
}

// 辅助函数
function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '未知时间';
  return date.toLocaleDateString('zh-CN');
}


function getTierIcon(tier?: string): string {
  const icons: Record<string, string> = {
    free: '🆓',
    basic: '⭐',
    standard: '💎',
    premium: '👑',
  };
  return icons[tier || 'free'] || '🆓';
}

function getTierName(tier?: string): string {
  const names: Record<string, string> = {
    free: '免费版',
    basic: '基础版',
    standard: '标准版',
    premium: '高级版',
  };
  return names[tier || 'free'] || '免费版';
}

function getStatusText(status?: string): string {
  const texts: Record<string, string> = {
    active: '生效中',
    inactive: '未激活',
    cancelled: '已取消',
    trialing: '试用中',
  };
  return texts[status || 'inactive'] || '未激活';
}

function getBenefitText(benefit: string): string {
  const texts: Record<string, string> = {
    free_chat_enabled: '自由对话',
    full_memory_access: '完整记忆',
    exclusive_cg: '专属CG',
    priority_support: '优先客服',
  };
  return texts[benefit] || benefit;
}

// 初始化
onMounted(() => {
  loadProfile();
  loadPlaySettings();
  loadNotifySettings();
  loadDevices();
  loadMemberInfo();
  // CR-043 FIX: 刷新订阅状态，确保 tier 是最新值
  subscriptionStore.fetchSubscriptionStatus();
});
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.settings-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
  padding: 24px;
}

/* 左侧导航栏 */
.settings-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 24px 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.nav-item:hover {
  background: var(--bg-secondary);
  color: var(--text-main);
}

.nav-item.active {
  background: var(--brand-primary);
  color: white;
}

.nav-icon {
  font-size: 20px;
}

.nav-label {
  font-weight: 500;
}

/* 移动端标签栏 */
.mobile-tabs {
  display: none;
  gap: 8px;
  padding: 16px;
  overflow-x: auto;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.mobile-tab {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
}

.mobile-tab.active {
  background: var(--brand-primary);
  color: white;
}

/* 右侧内容区 */
.settings-content {
  flex: 1;
  min-width: 0;
}

.content-panel {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
}

.panel-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 24px 0;
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 8px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--brand-primary);
}

.form-group input.readonly {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* 头像区域 */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 32px;
  font-weight: 700;
  color: var(--brand-primary);
}

.upload-btn {
  padding: 8px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-btn:hover {
  background: var(--bg-hover);
  border-color: var(--brand-primary);
}

/* 保存按钮 */
.save-btn {
  padding: 10px 24px;
  background: var(--brand-primary);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: var(--brand-primary-dark);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 设置组 */
.setting-group {
  margin-bottom: 20px;
}

.setting-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 8px;
}

.setting-group select {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 14px;
}

.setting-group input[type="range"] {
  width: 100%;
}

/* 开关样式 */
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-primary);
  transition: 0.3s;
  border-radius: 26px;
  border: 1px solid var(--border-color);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 2px;
  bottom: 2px;
  background-color: var(--text-secondary);
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--brand-primary);
  border-color: var(--brand-primary);
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
  background-color: white;
}

/* 通知列表 */
.notify-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notify-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.notify-info {
  flex: 1;
}

.notify-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 4px;
}

.notify-desc {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
}

/* 隐私安全 */
.privacy-section {
  margin-bottom: 32px;
}

.privacy-section h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 8px 0;
}

.section-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

/* 操作按钮 */
.action-btn {
  padding: 10px 20px;
  background: var(--brand-primary);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--brand-primary-dark);
}

/* 设备列表 */
.device-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.device-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.device-item.current {
  border-color: var(--brand-primary);
  background: rgba(167, 139, 250, 0.05);
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 4px;
}

.current-badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  background: var(--brand-primary);
  color: white;
  font-size: 12px;
  border-radius: 4px;
}

.device-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.logout-btn {
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #ef4444;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}

.logout-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}

/* 会员卡片 */
.member-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.member-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.member-tier {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tier-icon {
  font-size: 32px;
}

.tier-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
}

.member-status {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.member-status.active {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.member-status.inactive {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.member-status.cancelled {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.member-status.trialing {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 14px;
  color: var(--text-muted);
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.member-benefits {
  margin-bottom: 20px;
}

.member-benefits h4 {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 12px 0;
}

.benefits-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.benefit-item {
  font-size: 14px;
  color: var(--text-secondary);
}

.member-actions {
  display: flex;
  gap: 12px;
}

.primary-btn {
  flex: 1;
  padding: 12px 24px;
  background: var(--brand-primary);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover {
  background: var(--brand-primary-dark);
}

.secondary-btn {
  flex: 1;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn:hover {
  background: var(--bg-hover);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 20px 0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn {
  flex: 1;
  padding: 10px 20px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-main);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--bg-hover);
}

.confirm-btn {
  flex: 1;
  padding: 10px 20px;
  background: var(--brand-primary);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover:not(:disabled) {
  background: var(--brand-primary-dark);
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    flex-direction: column;
    padding: 0;
  }

  .settings-sidebar {
    display: none;
  }

  .mobile-tabs {
    display: flex;
  }

  .settings-content {
    padding: 16px;
  }

  .content-panel {
    padding: 16px;
  }

  .member-actions {
    flex-direction: column;
  }

  .modal-content {
    width: 95%;
  }
}
</style>