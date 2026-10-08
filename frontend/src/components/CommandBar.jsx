import { useRef, useState } from "react";
import { LoaderCircle, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const PRESETS = [
  { label: "Grounded in local KB", question: "How do conditional edges work in LangGraph?" },
  { label: "Retrieval evaluator", question: "What does the retrieval evaluator do in CRAG?" },
  { label: "Forces web fallback", question: "Who won the 2022 FIFA World Cup?" },
];

export default function CommandBar({ onRun, running }) {
  const [value, setValue] = useState("");
  const inputRef = useRef(null);

  const submit = (event) => {
    event.preventDefault();
    const question = value.trim();
    if (!question || running) return;
    onRun(question);
  };

  const pick = (question) => {
    setValue(question);
    inputRef.current?.focus();
  };

  return (
    <Card data-reveal className="p-4">
      <form onSubmit={submit} className="flex flex-col gap-3 md:flex-row md:items-center">
        <div className="flex flex-1 items-center gap-3 rounded-md border border-moss-600 bg-moss-950/70 px-4 transition-colors focus-within:border-spark-200/70">
          <span className="font-mono text-sm text-spark-200">{">"}</span>
          <input
            ref={inputRef}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            maxLength={500}
            placeholder="Ask the agent a question..."
            aria-label="Question"
            className="h-12 w-full bg-transparent font-mono text-sm text-bone-100 outline-none placeholder:text-bone-500"
          />
        </div>
        <Button type="submit" disabled={running || !value.trim()} className="h-12 min-w-44">
          {running ? <LoaderCircle className="animate-spin" /> : <Play />}
          {running ? "Agent running" : "Run agent"}
        </Button>
      </form>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-bone-500">Try</span>
        {PRESETS.map((preset) => (
          <button
            key={preset.label}
            type="button"
            onClick={() => pick(preset.question)}
            className="rounded-sm border border-moss-600 px-2.5 py-1 font-mono text-[11px] text-bone-300 transition-colors hover:border-fern-400 hover:bg-moss-800 hover:text-bone-100"
          >
            {preset.label}
          </button>
        ))}
      </div>
    </Card>
  );
}
