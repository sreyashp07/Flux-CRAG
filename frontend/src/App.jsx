import { useEffect, useMemo, useRef, useState } from "react";
import gsap from "gsap";
import AgentGraph from "@/components/AgentGraph";
import AnswerPanel from "@/components/AnswerPanel";
import ChunkLedger from "@/components/ChunkLedger";
import CommandBar from "@/components/CommandBar";
import Header from "@/components/Header";
import KnowledgeBase from "@/components/KnowledgeBase";
import RunSummary from "@/components/RunSummary";
import TelemetryTimeline from "@/components/TelemetryTimeline";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAgentRun } from "@/hooks/useAgentRun";
import { fetchGraph, fetchHealth, fetchKnowledgeBase } from "@/lib/api";

export default function App() {
  const { state, run } = useAgentRun();
  const [health, setHealth] = useState(null);
  const [topology, setTopology] = useState(null);
  const [knowledge, setKnowledge] = useState(null);
  const [tab, setTab] = useState("telemetry");
  const rootRef = useRef(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setHealth({ status: "offline" }));
    fetchGraph().then(setTopology).catch(() => setTopology(null));
    fetchKnowledgeBase().then(setKnowledge).catch(() => setKnowledge(null));
  }, []);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from("[data-reveal]", { opacity: 0, y: 28, duration: 0.85, stagger: 0.12, ease: "power3.out", delay: 0.15 });
    }, rootRef);
    return () => ctx.revert();
  }, []);

  const labelOf = useMemo(() => {
    const labels = Object.fromEntries((topology?.nodes ?? []).map((node) => [node.id, node.label]));
    return (id) => labels[id] ?? id;
  }, [topology]);

  const handleRun = (question) => {
    setTab("telemetry");
    run(question);
  };

  return (
    <div ref={rootRef} className="field-bg grain min-h-screen">
      <Header health={health} />

      <main className="mx-auto grid max-w-[1500px] gap-5 px-5 pb-14 pt-5 lg:px-8">
        <CommandBar onRun={handleRun} running={state.status === "running"} />

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(380px,1fr)]">
          <div className="grid content-start gap-5">
            <AgentGraph topology={topology} nodes={state.nodes} order={state.order} status={state.status} />
            <RunSummary final={state.final} elapsed={state.elapsed} labelOf={labelOf} />
            <AnswerPanel
              question={state.question}
              answer={state.answer}
              status={state.status}
              sources={state.sources}
              error={state.error}
            />
          </div>

          <Card data-reveal className="h-fit xl:sticky xl:top-5">
            <Tabs value={tab} onValueChange={setTab}>
              <TabsList>
                <TabsTrigger value="telemetry">
                  Telemetry
                  {state.timeline.length > 0 && <Badge variant="muted" className="ml-2">{state.timeline.length}</Badge>}
                </TabsTrigger>
                <TabsTrigger value="ledger">Ledger</TabsTrigger>
                <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
              </TabsList>
              <TabsContent value="telemetry">
                <TelemetryTimeline timeline={state.timeline} labelOf={labelOf} />
              </TabsContent>
              <TabsContent value="ledger">
                <ChunkLedger retrieved={state.retrieved} grades={state.grades} webResults={state.webResults} />
              </TabsContent>
              <TabsContent value="knowledge">
                <KnowledgeBase data={knowledge} />
              </TabsContent>
            </Tabs>
          </Card>
        </div>
      </main>
    </div>
  );
}
