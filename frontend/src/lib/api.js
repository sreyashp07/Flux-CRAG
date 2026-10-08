async function getJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path} responded ${response.status}`);
  return response.json();
}

export const fetchHealth = () => getJson("/api/health");
export const fetchGraph = () => getJson("/api/graph");
export const fetchKnowledgeBase = () => getJson("/api/knowledge-base");
export const askUrl = (question) => `/api/ask?question=${encodeURIComponent(question)}`;
