import { onMounted, onUnmounted, type Ref, ref } from 'vue';

/**
 * Watches elements with `.reveal`, `.reveal-left`, `.reveal-right`, `.reveal-scale`
 * classes and adds `.revealed` when they enter the viewport.
 */
export function useScrollReveal(root?: Ref<HTMLElement | null>) {
  let observer: IntersectionObserver | null = null;

  onMounted(() => {
    const container = root?.value ?? document;
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            observer?.unobserve(entry.target); // animate once
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
    );

    const targets = container.querySelectorAll(
      '.reveal, .reveal-left, .reveal-right, .reveal-scale',
    );
    targets.forEach((el) => observer?.observe(el));
  });

  onUnmounted(() => {
    observer?.disconnect();
  });
}

/** Animate a number counting up from 0 to `target` */
export function useCountUp(target: number, durationMs = 1200) {
  const current = ref(0);
  let raf = 0;

  function start() {
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min((now - start) / durationMs, 1);
      const ease = 1 - Math.pow(1 - t, 3); // easeOutCubic
      current.value = Math.round(ease * target);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
  }

  onUnmounted(() => cancelAnimationFrame(raf));
  return { current, start };
}
