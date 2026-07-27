<template>
  <div class="page-bg">
    <div class="community-page">
      <!-- Post List View -->
      <div v-if="!selectedPost">
        <header class="page-header fade-in-up">
          <h1 class="gradient-text">{{ $t('community.title') }}</h1>
          <p class="page-subtitle">{{ $t('community.subtitle') }}</p>
        </header>

        <!-- Search + Create -->
        <div class="action-bar fade-in-up">
          <SearchBar
            :placeholder="$t('communityExtra.searchPlaceholder')"
            @search="handleSearch"
            @clear="handleClearSearch"
          />
          <n-button type="primary" size="large" @click="showPostModal = true">
            ✏️ {{ $t('community.createPost') }}
          </n-button>
        </div>

        <!-- Tabs -->
        <div class="tab-bar fade-in-up">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-button"
            :class="{ active: activeTab === tab.key }"
            @click="handleTabChange(tab.key)"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>

        <!-- Post List -->
        <n-spin :show="loadingPosts">
          <div class="post-list" v-if="posts.length > 0">
            <PostCard
              v-for="(post, i) in posts"
              :key="post.id"
              :post="post"
              class="fade-in-up"
              :style="{ animationDelay: `${i * 0.06}s` }"
              @select="handleSelectPost"
              @liked="handlePostLiked"
              @unliked="handlePostUnliked"
              @deleted="handlePostDeleted"
              @image-click="(index) => handleImageClick(post, index)"
            />
          </div>
          <n-empty v-if="!loadingPosts && posts.length === 0" :description="$t('community.noPosts')" />
          
          <!-- Load More -->
          <div v-if="hasMore && !loadingPosts" class="load-more">
            <n-button @click="loadMore" :loading="loadingMore">
              加载更多
            </n-button>
          </div>
        </n-spin>
      </div>

      <!-- Post Detail View -->
      <div v-else class="post-detail">
        <n-button text @click="selectedPost = null" class="back-link">
          ← {{ $t('communityExtra.backToList') }}
        </n-button>

        <div class="detail-card glass-card fade-in-up">
          <div class="detail-header">
            <div class="detail-avatar">{{ selectedPost.author.name.charAt(0) }}</div>
            <div>
              <div class="detail-author">{{ selectedPost.author.name }}</div>
              <div class="detail-time">{{ formatTime(selectedPost.created_at) }}</div>
            </div>
          </div>
          <h2 class="detail-title">{{ selectedPost.title }}</h2>
          <div class="detail-content">{{ selectedPost.content }}</div>
          <div v-if="selectedPost.images?.length" class="detail-images">
            <img v-for="(url, idx) in selectedPost.images" :key="idx" :src="url" class="detail-img" />
          </div>
          <div class="detail-stats">
            <span>❤️ {{ selectedPost.stats.likes }}</span>
            <span>💬 {{ selectedPost.stats.comments }}</span>
            <span>👁️ {{ selectedPost.stats.views }}</span>
          </div>
        </div>

        <!-- Comments -->
        <div class="comments-section">
          <h3>{{ $t('communityExtra.comments') }} ({{ comments.length }})</h3>
          <n-spin :show="loadingComments">
            <div v-if="comments.length > 0" class="comment-list">
              <div v-for="(c, i) in comments" :key="c.id" class="comment-item glass-card fade-in-up" :style="{ animationDelay: `${i * 0.04}s` }">
                <div class="comment-header">
                  <span class="comment-author">{{ c.author_name }}</span>
                  <span class="comment-time">{{ formatTime(c.created_at) }}</span>
                  <n-button 
                    v-if="c.author_name === authStore.user?.displayName"
                    type="error"
                    size="tiny"
                    text
                    @click="handleDeleteComment(c.id)"
                    :loading="deletingCommentId === c.id"
                  >
                    删除
                  </n-button>
                </div>
                <p class="comment-text">{{ c.content }}</p>
              </div>
            </div>
            <n-empty v-else-if="!loadingComments" :description="$t('community.noComments')" />
          </n-spin>

          <div class="comment-input glass-card">
            <n-input
              v-model:value="newComment"
              type="textarea"
              :placeholder="$t('communityExtra.writeComment')"
              :rows="2"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
            <n-button type="primary" size="small" @click="submitComment" :loading="submittingComment" style="margin-top: 8px; align-self: flex-end;">
              {{ $t('communityExtra.submitComment') }}
            </n-button>
          </div>
        </div>
      </div>

      <!-- Create Post Modal -->
      <n-modal v-model:show="showPostModal" preset="card" :title="$t('communityExtra.createPost')" style="max-width: 560px">
        <n-form :label-placement="'top'">
          <n-form-item :label="$t('communityExtra.postTitle')">
            <n-input v-model:value="newPostTitle" :placeholder="$t('communityExtra.postTitlePlaceholder')" />
          </n-form-item>
          <n-form-item :label="$t('communityExtra.postContent')">
            <n-input
              v-model:value="newPostContent"
              type="textarea"
              :placeholder="$t('communityExtra.postContentPlaceholder')"
              :rows="5"
              :autosize="{ minRows: 4, maxRows: 8 }"
            />
          </n-form-item>
        </n-form>
        <template #footer>
          <div style="display: flex; gap: 8px; justify-content: flex-end;">
            <n-button @click="showPostModal = false">{{ $t('communityExtra.cancel') }}</n-button>
            <n-button type="primary" :loading="submittingPost" @click="submitPost">{{ $t('communityExtra.publish') }}</n-button>
          </div>
        </template>
      </n-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useMessage, NModal, NForm, NFormItem } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { getPosts, searchPosts, getComments, createComment, deleteComment } from '@/api/community';
import type { Post, PostTab } from '@/types/community';
import SearchBar from '@/components/SearchBar.vue';
import PostCard from '@/components/PostCard.vue';

const { t } = useI18n();
const message = useMessage();
const authStore = useAuthStore();

useHead({
  title: computed(() => t('community.title')),
  meta: [{ name: 'description', content: () => t('community.subtitle') }],
});

interface Comment {
  id: string;
  author_name: string;
  content: string;
  created_at: string;
}

const tabs = [
  { key: 'recommend' as PostTab, icon: '⭐', label: '推荐' },
  { key: 'latest' as PostTab, icon: '🕐', label: '最新' },
  { key: 'hot' as PostTab, icon: '🔥', label: '热门' },
  { key: 'mine' as PostTab, icon: '📝', label: '我的' }
];

const activeTab = ref<PostTab>('recommend');
const posts = ref<Post[]>([]);
const loadingPosts = ref(false);
const loadingMore = ref(false);
const hasMore = ref(true);
const currentPage = ref(1);
const searchKeyword = ref('');
const selectedPost = ref<Post | null>(null);
const comments = ref<Comment[]>([]);
const loadingComments = ref(false);
const newComment = ref('');
const submittingComment = ref(false);
const deletingCommentId = ref<string | null>(null);
const showPostModal = ref(false);
const newPostTitle = ref('');
const newPostContent = ref('');
const submittingPost = ref(false);

function formatTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  
  return date.toLocaleDateString('zh-CN');
}

async function loadPosts() {
  loadingPosts.value = true;
  try {
    const response = await getPosts({
      tab: activeTab.value,
      page: 1,
      page_size: 20
    });
    // 转换数据结构：后端返回扁平结构，前端期望嵌套的 stats 对象
    posts.value = response.posts.map((post: any) => ({
      ...post,
      stats: {
        views: post.views_count || 0,
        comments: post.comment_count || 0,
        likes: post.like_count || 0
      }
    }));
    hasMore.value = response.has_more;
    currentPage.value = 1;
  } catch (error) {
    console.error('加载帖子失败:', error);
    message.error('加载帖子失败');
  } finally {
    loadingPosts.value = false;
  }
}

async function loadMore() {
  loadingMore.value = true;
  try {
    const response = await getPosts({
      tab: activeTab.value,
      page: currentPage.value + 1,
      page_size: 20
    });
    // 转换数据结构
    const newPosts = response.posts.map((post: any) => ({
      ...post,
      stats: {
        views: post.views_count || 0,
        comments: post.comment_count || 0,
        likes: post.like_count || 0
      }
    }));
    posts.value.push(...newPosts);
    hasMore.value = response.has_more;
    currentPage.value++;
  } catch (error) {
    console.error('加载更多帖子失败:', error);
    message.error('加载更多失败');
  } finally {
    loadingMore.value = false;
  }
}

async function handleSearch(keyword: string) {
  searchKeyword.value = keyword;
  loadingPosts.value = true;
  try {
    const response = await searchPosts({
      keyword,
      page: 1,
      page_size: 20
    });
    // 转换数据结构
    posts.value = response.posts.map((post: any) => ({
      ...post,
      stats: {
        views: post.views_count || 0,
        comments: post.comment_count || 0,
        likes: post.like_count || 0
      }
    }));
    hasMore.value = response.posts.length >= 20;
    currentPage.value = 1;
  } catch (error) {
    console.error('搜索失败:', error);
    message.error('搜索失败');
  } finally {
    loadingPosts.value = false;
  }
}

async function handleClearSearch() {
  searchKeyword.value = '';
  await loadPosts();
}

async function handleTabChange(tab: PostTab) {
  activeTab.value = tab;
  searchKeyword.value = '';
  await loadPosts();
}

function handlePostLiked(postId: string, newCount: number) {
  const post = posts.value.find(p => p.id === postId);
  if (post) {
    post.is_liked = true;
    post.stats.likes = newCount;
  }
}

function handlePostUnliked(postId: string, newCount: number) {
  const post = posts.value.find(p => p.id === postId);
  if (post) {
    post.is_liked = false;
    post.stats.likes = newCount;
  }
}

function handlePostDeleted(postId: string) {
  posts.value = posts.value.filter(p => p.id !== postId);
  message.success('帖子已删除');
}

function handleImageClick(post: Post, index: number) {
  // TODO: 实现图片预览功能
  console.log('Image clicked:', post.images[index]);
}

function handleSelectPost(post: Post) {
  selectedPost.value = post;
}

async function loadComments() {
  if (!selectedPost.value) return;
  loadingComments.value = true;
  try {
    const res = await getComments(selectedPost.value.id);
    comments.value = res.comments;
  } catch (error) {
    console.error('加载评论失败:', error);
    message.error('加载评论失败');
  } finally {
    loadingComments.value = false;
  }
}

async function submitComment() {
  if (!newComment.value.trim()) {
    message.warning(t('communityExtra.enterComment'));
    return;
  }
  if (!selectedPost.value) return;
  
  submittingComment.value = true;
  try {
    await createComment(selectedPost.value.id, newComment.value);
    message.success(t('communityExtra.commentSuccess'));
    newComment.value = '';
    await loadComments(); // 刷新评论列表
    selectedPost.value.stats.comments += 1; // 更新计数
  } catch (error) {
    message.error(t('communityExtra.commentFailed'));
  } finally {
    submittingComment.value = false;
  }
}

async function handleDeleteComment(commentId: string) {
  if (!selectedPost.value) return;
  
  deletingCommentId.value = commentId;
  try {
    await deleteComment(commentId);
    message.success('评论已删除');
    await loadComments(); // 刷新评论列表
    selectedPost.value.stats.comments -= 1; // 更新计数
  } catch (error) {
    message.error('删除评论失败');
  } finally {
    deletingCommentId.value = null;
  }
}

async function submitPost() {
  if (!newPostTitle.value.trim() || !newPostContent.value.trim()) {
    message.warning(t('communityExtra.fillRequired'));
    return;
  }
  submittingPost.value = true;
  try {
    // TODO: 实现创建帖子的 API
    message.success(t('communityExtra.postSuccess'));
    newPostTitle.value = '';
    newPostContent.value = '';
    showPostModal.value = false;
    await loadPosts();
  } catch (error) {
    message.error(t('communityExtra.postFailed'));
  } finally {
    submittingPost.value = false;
  }
}

onMounted(() => {
  loadPosts();
});

// 打开帖子时自动加载评论
watch(selectedPost, (newPost) => {
  if (newPost) {
    loadComments();
  }
});
</script>

<style scoped>
.community-page { max-width: 800px; margin: 0 auto; padding: 24px 16px 80px; }
.page-header { margin-bottom: 20px; }
.page-header h1 { font-size: 24px; font-weight: 700; margin: 0; }
.page-subtitle { color: var(--text-muted); font-size: 14px; margin: 4px 0 0; }
.action-bar { display: flex; gap: 12px; margin-bottom: 20px; align-items: center; }

.tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 4px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.tab-button {
  flex: 1;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.tab-button.active {
  background: var(--color-primary);
  color: white;
}

.post-list { display: flex; flex-direction: column; gap: 16px; }

.load-more {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.post-detail { max-width: 700px; margin: 0 auto; }
.back-link { color: var(--text-muted) !important; margin-bottom: 16px; font-size: 13px !important; }
.detail-card { padding: 24px; margin-bottom: 20px; }
.detail-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.detail-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, #818CF8, #C084FC);
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 18px; flex-shrink: 0;
}
.detail-author { font-size: 15px; font-weight: 600; color: var(--text-main); }
.detail-time { font-size: 12px; color: var(--text-subtle); }
.detail-title { font-size: 22px; font-weight: 700; color: var(--text-main); margin: 0 0 12px; }
.detail-content { font-size: 15px; color: var(--text-main); line-height: 1.8; white-space: pre-wrap; }
.detail-images { display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; }
.detail-img { max-width: 200px; max-height: 200px; border-radius: 12px; object-fit: cover; }
.detail-stats { display: flex; gap: 16px; margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(167, 139, 250, 0.1); font-size: 13px; color: var(--text-subtle); }

.comments-section { margin-top: 8px; }
.comments-section h3 { font-size: 16px; font-weight: 600; color: var(--text-main); margin: 0 0 12px; }
.comment-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.comment-item { padding: 12px 16px; }
.comment-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.comment-author { font-size: 13px; font-weight: 600; color: var(--text-main); }
.comment-time { font-size: 11px; color: var(--text-subtle); }
.comment-text { font-size: 14px; color: var(--text-main); line-height: 1.5; margin: 0; }
.comment-input { padding: 12px 16px; display: flex; flex-direction: column; }
</style>
