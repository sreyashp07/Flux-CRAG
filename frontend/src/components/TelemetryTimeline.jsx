import { useEffect, useRef } from "react";
import gsap from "gsap";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import EmptyState from "@/components/EmptyState";

const STATUS_VARIANT = { started: "muted", progress: "default", completed: "success", failed: "danger" };

const DOT = {
  muted: "border-moss-500 bg-moss-700",
  default: "border-fern-400 bg-fern-400/30",
  success: "border-spark-200 bg-spark-200/40",
  warn: "border-ochre-400 bg-ochre-400/40",
  danger: "border-rust-400 bg-rust-400/40",
};

function variantFor(event) {
  if (event.status === "decision") return event.data?.relevance === "relevant" ? "success" : "warn";
  return STATUS_VARIANT[event.status] ?? "muted";
}

function Quote({ label, text }) {
  return (
    <p className="mt-2 rounded-sm border-l-2 border-fern-400 bg-moss-850 px-3 py-1.5 font-mono text-[11px] leading-relaxed text-bone-300">
      <span className="mr-2 uppercase tracking-[0.16em] text-bone-500">{label}</span>
      {text}
    </p>
  );
}

function Extras({ event }) {
  const data = event.data ?? {};
  if (event.status === "started" && data.query) return <Quote label="query" text={data.query} />;
  if (event.node === "rewrite_query" && event.status === "completed" && data.rewritten) {
    return <Quote label="rewritten" text={data.rewritten} />;
  }
  if (event.node === "web_search" && event.status === "completed" && data.results?.length) {
    return (
      <ul className="mt-2 space-y-1">
        {data.results.map((result) => (
          <li key={result.url} className="truncate font-mono text-[11px] text-bone-300">
            {result.title}
          </li>
        ))}
      </ul>
    );
  }
  if (event.status === "progress" && data.reason) {
    return <p className="mt-1.5 font-mono text-[11px] leading-relaxed text-bone-500">{data.reason}</p>;
  }
  if (event.status === "failed" && data.error) {
    return <p className="mt-1.5 font-mono text-[11px] leading-relaxed text-rust-400">{data.error}</p>;
  }
  return null;
}

function Entry({ event, label }) {
  const ref = useRef(null);
  const variant = variantFor(event);

  useEffect(() => {
    const tween = gsap.fromTo(ref.current, { x: 26, opacity: 0 }, { x: 0, opacity: 1, duration: 0.5, ease: "power3.out" });
    return () => tween.kill();
  }, []);

  return (
    <div ref={ref} className="relative pl-6">
      <span className={`absolute -left-[5.5px] top-1.5 size-2.5 rounded-full border ${DOT[variant]}`} />
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={variant}>{event.status}</Badge>
        <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-bone-300">{label}</span>
        <span className="ml-auto font-mono text-[10px] tabular-nums text-bone-500">+{event.t.toFixed(2)}s</span>
      </div>
      <p className="mt-1.5 text-sm leading-snug text-bone-100">{event.message}</p>
      <Extras event={event} />
    </div>
  );
}

export default function TelemetryTimeline({ timeline, labelOf }) {
  const endRef = useRef(null);

  useEffect(() => {
    const viewport = endRef.current?.closest("[data-radix-scroll-area-viewport]");
    if (viewport) viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
  }, [timeline.length]);

  return (
    <ScrollArea className="h-[560px]">
      <div className="p-5">
        {timeline.length === 0 ? (
          <EmptyState text="Telemetry streams here, event by event, while the agent works" />
        ) : (
          <ol className="relative ml-1.5 space-y-5 border-l border-moss-700">
            {timeline.map((event) => (
              <li key={event.id}>
                <Entry event={event} label={labelOf(event.node)} />
              </li>
            ))}
          </ol>
        )}
        <div ref={endRef} />
      </div>
    </ScrollArea>
  );
}
