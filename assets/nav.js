// 모바일 네비게이션 토글
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.main-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
      toggle.classList.toggle('open');
      toggle.setAttribute('aria-expanded', toggle.classList.contains('open'));
    });

    // 링크 클릭 시 메뉴 닫기
    nav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });

    // 뷰포트 크기 변경 시 메뉴 초기화
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        nav.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // 후기 별점 분포 클릭 → 해당 별점만 필터링 (이용 후기 페이지)
  const dist = document.querySelector('.rating-dist.interactive');
  const grid = document.querySelector('.reviews-grid-full');
  if (dist && grid) {
    const cards = Array.prototype.slice.call(grid.querySelectorAll('.review-card'));
    const empty = document.querySelector('.reviews-empty');
    const btns = Array.prototype.slice.call(dist.querySelectorAll('[data-star]'));
    let current = '';

    const apply = (star) => {
      current = star;
      let shown = 0;
      cards.forEach((c) => {
        const match = !star || c.getAttribute('data-rating') === star;
        c.style.display = match ? '' : 'none';
        if (match) shown++;
      });
      btns.forEach((b) => {
        const s = b.getAttribute('data-star');
        b.classList.toggle('is-active', s === star);
      });
      if (empty) empty.hidden = shown !== 0;
    };

    btns.forEach((b) => {
      if (b.disabled) return;
      b.addEventListener('click', () => {
        const s = b.getAttribute('data-star');
        apply(current === s ? '' : s); // 같은 별점 다시 누르면 전체로
      });
    });
    apply('');
  }
});
