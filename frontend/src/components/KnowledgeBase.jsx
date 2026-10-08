import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollArea } from "@/components/ui/scroll-area";
import EmptyState from "@/components/EmptyState";
import CountUp from "@/components/CountUp";

export default function KnowledgeBase({ data }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!data || !ref.current) return;
    const bars = ref.current.querySelectorAll("[data-kb-bar]");
    const tween = gsap.fromTo(
      bars,
      { scaleX: 0 },
      { scaleX: 1, duration: 1, stagger: 0.1, ease: "power3.out", transformOrigin: "left center" }
    );
    return () => tween.kill();
  }, [data]);

  if (!data) {
    return (
      <div className="p-5">
        <EmptyState text="Loading knowledge base" />
      </div>
    );
  }

  const max = Math.max(...data.sources.map((s) => s.chunks), 1);

  return (
    <ScrollArea className="h-[560px]">
      <div ref={ref} className="space-y-5 p-5">
        <div className="flex items-end justify-between">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-fern-300">Local ChromaDB collection</p>
            <p className="mt-2 font-display text-4xl tracking-tight text-bone-100">
              <CountUp value={data.total_chunks} />
            </p>
            <p className="font-mono text-[11px] text-bone-500">chunks across {data.sources.length} documents</p>
          </div>
        </div>
        <ul className="space-y-3">
          {data.sources.map((source) => (
            <li key={source.source}>
              <div className="flex items-center justify-between font-mono text-[11px] text-bone-300">
                <span className="truncate">{source.source}</span>
                <span className="tabular-nums text-bone-500">{source.chunks}</span>
              </div>
              <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-moss-700">
                <div data-kb-bar className="bar-fill h-full rounded-full" style={{ width: `${(source.chunks / max) * 100}%` }} />
              </div>
            </li>
          ))}
        </ul>
      </div>
    </ScrollArea>
  );
}
