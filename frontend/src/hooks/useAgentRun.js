import { useCallback, useEffect, useReducer, useRef } from "react";
import { askUrl } from "@/lib/api";

const initialState = {
  status: "idle", // idle | running | done | error
  runId: null,
  question: "",
  startedAt: null,
  elapsed: 0,
  timeline: [], // every node event except answer tokens
  nodes: {}, // node id -> active | done | warn
  order: [], // node ids in the order they started
  retrieved: [],
  grades: [],
  rewritten: null,
  webResults: [],
  sources: [],
  answer: "",
  final: null,
  error: null,
};

function applyEvent(state, msg) {
  const { node, status } = msg;
  const data = msg.data ?? {};

  // Answer tokens go straight to the answer, not the timeline.
  if (status === "progress" && data.token !== undefined) {
    return { ...state, answer: state.answer + data.token };
  }

  const nodes = { ...state.nodes };
  const next = { ...state };
  let order = state.order;

  if (status === "started") {
    nodes[node] = "active";
    if (order[order.length - 1] !== node) order = [...order, node];
    if (node === "generate") next.sources = data.sources ?? [];
  } else if (status === "completed") {
    nodes[node] = nodes[node] === "warn" ? "warn" : "done";
    if (node === "retrieve") next.retrieved = data.chunks ?? [];
    if (node === "grade_documents") next.grades = data.grades ?? [];
    if (node === "rewrite_query") next.rewritten = data.rewritten ?? null;
    if (node === "web_search") next.webResults = data.results ?? [];
    if (node === "generate") {
      next.answer = data.answer ?? state.answer;
      next.sources = data.sources ?? state.sources;
    }
  } else if (status === "failed") {
    nodes[node] = "warn";
  }

  const t = state.startedAt ? msg.timestamp - state.startedAt : 0;
  next.timeline = [...state.timeline, { ...msg, id: state.timeline.length, t }];
  return { ...next, nodes, order };
}

function reducer(state, action) {
  switch (action.type) {
    case "reset":
      return { ...initialState, status: "running", question: action.question };
    case "run_started":
      return { ...state, runId: action.msg.run_id, startedAt: action.msg.timestamp };
    case "event":
      return applyEvent(state, action.msg);
    case "final":
      return {
        ...state,
        status: "done",
        final: action.msg,
        answer: state.answer || action.msg.answer,
        elapsed: state.startedAt ? action.msg.timestamp - state.startedAt : 0,
      };
    case "error":
      if (state.status !== "running") return state;
      return { ...state, status: "error", error: action.message };
    default:
      return state;
  }
}

export function useAgentRun() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const sourceRef = useRef(null);

  const close = useCallback(() => {
    sourceRef.current?.close();
    sourceRef.current = null;
  }, []);

  const run = useCallback(
    (question) => {
      close();
      dispatch({ type: "reset", question });

      const source = new EventSource(askUrl(question));
      sourceRef.current = source;
      const onMessage = (handler) => (e) => handler(JSON.parse(e.data));

      source.addEventListener("run_started", onMessage((msg) => dispatch({ type: "run_started", msg })));
      source.addEventListener("event", onMessage((msg) => dispatch({ type: "event", msg })));
      source.addEventListener(
        "final",
        onMessage((msg) => {
          dispatch({ type: "final", msg });
          source.close(); // stop EventSource from auto-reconnecting and re-running the question
        })
      );
      source.addEventListener("error", (e) => {
        // A server-sent `error` message carries data; a dropped connection does not.
        const message = e.data ? JSON.parse(e.data).message : "Lost the connection to the agent.";
        dispatch({ type: "error", message });
        source.close();
      });
    },
    [close]
  );

  useEffect(() => close, [close]);

  return { state, run };
}
