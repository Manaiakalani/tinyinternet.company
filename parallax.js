const logo = document.querySelector(".brand-mark");
const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = window.matchMedia("(pointer: fine)");

if (logo) {
  let aimX = 0;
  let aimY = 0;
  let x = 0;
  let y = 0;
  let frame = 0;

  const enabled = () => !motion.matches && finePointer.matches;

  const place = () => {
    const scale = Math.min(window.innerWidth, window.innerHeight) / 100 * 2.2;
    logo.style.transform = `translate3d(${(-x * scale).toFixed(2)}px, ${(-y * scale).toFixed(2)}px, 0)`;
  };

  const stop = () => {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
  };

  const tick = () => {
    x += (aimX - x) * 0.08;
    y += (aimY - y) * 0.08;
    if (Math.abs(aimX - x) < 0.001 && Math.abs(aimY - y) < 0.001) {
      x = aimX;
      y = aimY;
      place();
      frame = 0;
      return;
    }
    place();
    frame = requestAnimationFrame(tick);
  };

  const wake = () => {
    if (enabled() && !frame) frame = requestAnimationFrame(tick);
  };

  window.addEventListener("pointermove", (event) => {
    if (!enabled() || event.pointerType !== "mouse") return;
    aimX = (event.clientX / window.innerWidth - 0.5) * 2;
    aimY = (event.clientY / window.innerHeight - 0.5) * 2;
    wake();
  });

  document.documentElement.addEventListener("mouseleave", () => {
    aimX = 0;
    aimY = 0;
    wake();
  });

  motion.addEventListener("change", () => {
    if (enabled()) return;
    stop();
    aimX = 0;
    aimY = 0;
    x = 0;
    y = 0;
    logo.style.transform = "";
  });
}
