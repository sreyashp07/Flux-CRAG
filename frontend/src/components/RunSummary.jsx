import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ArrowRight, Clock, Globe, Route } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import CountUp from "@/components/CountUp";

export default function RunSummary({ final, elapsed, labelOf }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!final || !ref.current) return;
    const chips = ref.current.querySelectorAll("[data-chip]");
    const tween = gsap.fromTo(
      chips,
      { opacity: 0, y: 10, scale: 0.94 },
      { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.07, ease: "back.out(1.6)" }
    );
    return () => tween.kill();
  }, [final]);

  return (
    <Card ref={ref} data-reveal className="px-5 py-4">
      {!final ? (
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-bone-500">
          Run summary appears when the agent finishes
        </p>
      ) : (
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Route className="size-4 text-fern-300" />
            {final.path.map((id, index) => (
              <span key={`${id}-${index}`} data-chip className="flex items-center gap-2">
                {index > 0 && <ArrowRight className="size-3 text-moss-500" />}
                <Badge variant="default">{labelOf(id)}</Badge>
              </span>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge data-chip variant={final.relevance === "relevant" ? "success" : "warn"}>
              local retrieval {final.relevance ?? "n/a"}
            </Badge>
            <Badge data-chip variant={final.used_web_search ? "warn" : "muted"}>
              <Globe className="size-3" />
              {final.used_web_search ? "web fallback used" : "no web fallback"}
            </Badge>
            <Badge data-chip variant="muted">
              <Clock className="size-3" />
              <CountUp value={elapsed} decimals={2} suffix="s" />
            </Badge>
          </div>
        </div>
      )}
    </Card>
  );
}
