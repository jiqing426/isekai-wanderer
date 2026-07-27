import { ref, onMounted, onUnmounted, watch, type Ref } from 'vue';

/**
 * 移动端轮播图 composable
 * - CSS scroll-snap 驱动滑动
 * - 自动播放（5s 间隔）
 * - 鼠标移入/触摸时暂停
 * - 指示器同步当前页
 */
export function useMobileCarousel(
  containerRef: Ref<HTMLElement | null>,
  itemCount: Ref<number>,
  options: {
    autoPlay?: boolean;
    interval?: number;
  } = {}
) {
  const { autoPlay = true, interval = 5000 } = options;
  const currentIndex = ref(0);
  let timer: ReturnType<typeof setInterval> | null = null;
  let paused = false;

  function scrollToIndex(index: number) {
    const el = containerRef.value;
    if (!el) return;
    const children = el.children;
    if (index < 0 || index >= children.length) return;
    const child = children[index] as HTMLElement;
    el.scrollTo({ left: child.offsetLeft, behavior: 'smooth' });
    currentIndex.value = index;
  }

  function next() {
    const count = itemCount.value;
    if (count <= 0) return;
    const nextIndex = (currentIndex.value + 1) % count;
    scrollToIndex(nextIndex);
  }

  function startAutoPlay() {
    if (!autoPlay) return;
    stopAutoPlay();
    timer = setInterval(() => {
      if (!paused && itemCount.value > 1) {
        next();
      }
    }, interval);
  }

  function stopAutoPlay() {
    if (timer !== null) {
      clearInterval(timer);
      timer = null;
    }
  }

  function pause() {
    paused = true;
  }

  function resume() {
    paused = false;
  }

  /** 通过 scroll 事件同步 currentIndex（用户手动滑动时） */
  function onScroll() {
    const el = containerRef.value;
    if (!el) return;
    const scrollLeft = el.scrollLeft;
    const width = el.offsetWidth;
    if (width <= 0) return;
    const idx = Math.round(scrollLeft / width);
    if (idx !== currentIndex.value && idx >= 0 && idx < itemCount.value) {
      currentIndex.value = idx;
    }
  }

  onMounted(() => {
    startAutoPlay();
    const el = containerRef.value;
    if (el) {
      el.addEventListener('scroll', onScroll, { passive: true });
    }
  });

  onUnmounted(() => {
    stopAutoPlay();
    const el = containerRef.value;
    if (el) {
      el.removeEventListener('scroll', onScroll);
    }
  });

  // 数量变化时重置
  watch(itemCount, () => {
    currentIndex.value = 0;
    const el = containerRef.value;
    if (el) {
      el.scrollTo({ left: 0, behavior: 'auto' });
    }
  });

  return {
    currentIndex,
    scrollToIndex,
    pause,
    resume,
    startAutoPlay,
    stopAutoPlay,
  };
}
