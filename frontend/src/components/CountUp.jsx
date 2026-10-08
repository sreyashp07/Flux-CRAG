import { useEffect, useRef } from "react";
import gsap from "gsap";

export default function CountUp({ value, decimals = 0, suffix = "", duration = 1.1 }) {
  const ref = useRef(null);

  useEffect(() => {
    const node = ref.current;
    if (!node || value === null || value === undefined) return;
    const proxy = { n: 0 };
    const tween = gsap.to(proxy, {
      n: value,
      duration,
      ease: "power2.out",
      onUpdate: () => {
        node.textContent = proxy.n.toFixed(decimals) + suffix;
      },
    });
    return () => tween.kill();
  }, [value, decimals, suffix, duration]);

  const initial = value === null || value === undefined ? "--" : value.toFixed(decimals) + suffix;
  return (
    <span ref={ref} className="tabular-nums">
      {initial}
    </span>
  );
}
