// Geometry for the agent state machine. Node ids come from /api/graph;
// positions live here because the backend only describes topology.
export const NODE_W = 150;
export const NODE_H = 60;
export const VIEW = { width: 900, height: 340 };

const POSITIONS = {
  retrieve: { x: 105, y: 100 },
  grade_documents: { x: 335, y: 100 },
  generate: { x: 795, y: 100 },
  rewrite_query: { x: 475, y: 250 },
  web_search: { x: 695, y: 250 },
};

export function positionOf(id, index) {
  return POSITIONS[id] ?? { x: 105 + index * 180, y: 170 };
}

function cubic(p0, p1, p2, p3) {
  return {
    d: `M ${p0.x} ${p0.y} C ${p1.x} ${p1.y}, ${p2.x} ${p2.y}, ${p3.x} ${p3.y}`,
    mid: {
      x: (p0.x + 3 * p1.x + 3 * p2.x + p3.x) / 8,
      y: (p0.y + 3 * p1.y + 3 * p2.y + p3.y) / 8,
    },
  };
}

// Returns the SVG path for an edge plus its midpoint (used for the edge label).
export function edgeGeometry(from, to) {
  const hw = NODE_W / 2;
  const hh = NODE_H / 2;

  if (Math.abs(to.y - from.y) < 8) {
    const start = { x: from.x + hw, y: from.y };
    const end = { x: to.x - hw, y: to.y };
    return {
      d: `M ${start.x} ${start.y} L ${end.x} ${end.y}`,
      mid: { x: (start.x + end.x) / 2, y: start.y },
    };
  }

  if (to.y > from.y) {
    const p0 = { x: from.x, y: from.y + hh };
    const p3 = { x: to.x - hw, y: to.y };
    return cubic(p0, { x: p0.x, y: p3.y }, { x: p3.x - 70, y: p3.y }, p3);
  }

  const p0 = { x: from.x + hw, y: from.y };
  const p3 = { x: to.x, y: to.y + hh };
  return cubic(p0, { x: p3.x, y: p0.y }, { x: p3.x, y: p3.y + 70 }, p3);
}
