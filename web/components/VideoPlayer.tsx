"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Comment } from "../lib/types";

type Props = {
  sources: { src: string; label: string }[];
  poster?: string | null;
  comments: Comment[];
};

type Active = {
  key: string;
  text: string;
  lane: number;
  startedAt: number;
};

const LANES = 10;
const DURATION_MS = 8000;

export default function VideoPlayer({ sources, poster, comments }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const firedRef = useRef<Set<number>>(new Set());
  const [active, setActive] = useState<Active[]>([]);
  const [qualityIdx, setQualityIdx] = useState(sources.length - 1);

  const sortedComments = useMemo(
    () => [...comments].sort((a, b) => a.tpos - b.tpos),
    [comments]
  );

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;

    const laneLastStart = new Array<number>(LANES).fill(0);

    const tick = () => {
      const t = v.currentTime;
      const now = performance.now();
      const newItems: Active[] = [];
      for (const c of sortedComments) {
        if (c.tpos > t) break;
        if (firedRef.current.has(c.id)) continue;
        // Only fire if within a few seconds of tpos (avoid blasting when seeking forward)
        if (t - c.tpos > 1.5) {
          firedRef.current.add(c.id);
          continue;
        }
        firedRef.current.add(c.id);
        let bestLane = 0;
        let bestAge = -1;
        for (let i = 0; i < LANES; i++) {
          const age = now - laneLastStart[i];
          if (age > bestAge) {
            bestAge = age;
            bestLane = i;
          }
        }
        laneLastStart[bestLane] = now;
        newItems.push({
          key: `${c.id}-${now}`,
          text: c.text,
          lane: bestLane,
          startedAt: now,
        });
      }
      if (newItems.length > 0) {
        setActive((prev) => [
          ...prev.filter((a) => now - a.startedAt < DURATION_MS),
          ...newItems,
        ]);
      } else {
        // periodic sweep
        setActive((prev) => {
          const filtered = prev.filter((a) => now - a.startedAt < DURATION_MS);
          return filtered.length === prev.length ? prev : filtered;
        });
      }
    };

    const reset = () => {
      firedRef.current.clear();
      setActive([]);
    };

    const interval = window.setInterval(tick, 200);
    v.addEventListener("seeking", reset);
    v.addEventListener("emptied", reset);
    return () => {
      window.clearInterval(interval);
      v.removeEventListener("seeking", reset);
      v.removeEventListener("emptied", reset);
    };
  }, [sortedComments]);

  const currentSrc = sources[qualityIdx]?.src;

  return (
    <div>
      <div className="player-stage">
        <video
          ref={videoRef}
          src={currentSrc}
          poster={poster ?? undefined}
          controls
          preload="metadata"
        />
        <div className="barrage-layer">
          {active.map((a) => (
            <div
              key={a.key}
              className="barrage-item"
              style={{ top: `${(a.lane / LANES) * 80}%` }}
            >
              {a.text}
            </div>
          ))}
        </div>
      </div>
      {sources.length > 1 ? (
        <div className="btn-group btn-group-xs" style={{ marginTop: 6 }}>
          {sources.map((s, i) => (
            <button
              key={i}
              type="button"
              className={`btn btn-default${i === qualityIdx ? " active" : ""}`}
              onClick={() => setQualityIdx(i)}
            >
              {s.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
