import videos from "../public/data/videos.json";
import users from "../public/data/users.json";
import comments from "../public/data/comments.json";
import tags from "../public/data/tags.json";
import dead from "../public/data/dead.json";
import type { Video, User, Comment, CommentsMap, Tag, Dead } from "./types";

const videoList = videos as unknown as Video[];
const userList = users as unknown as User[];
const commentsMap = comments as unknown as CommentsMap;
const tagList = tags as unknown as Tag[];
const deadList = dead as unknown as Dead[];

export function getVideos(): Video[] {
  return videoList;
}

export function getVideo(id: string | number): Video | null {
  const n = typeof id === "string" ? Number(id) : id;
  return videoList.find((v) => v.id === n) ?? null;
}

export function getUser(id: string | number | null): User | null {
  if (id == null) return null;
  const n = typeof id === "string" ? Number(id) : id;
  return userList.find((u) => u.id === n) ?? null;
}

export function getUsers(): User[] {
  return userList;
}

export function getCommentsFor(videoId: string | number): Comment[] {
  return commentsMap[String(videoId)] ?? [];
}

export function getTags(): Tag[] {
  return tagList;
}

export function getDead(): Dead[] {
  return deadList;
}

export function releaseBase(): string {
  return (
    process.env.NEXT_PUBLIC_RELEASE_BASE ??
    "https://github.com/lzpel/gorovideo/releases/download/v1-archive"
  );
}

export function liveVideoUrl(videoId: number, idx: number): string {
  return `${releaseBase()}/${videoId}_${idx}.mp4`;
}

export function deadVideoUrl(filename: string): string {
  // filename already like "dead_001_hq.mp4"
  return `${releaseBase()}/${filename}`;
}

export function withBasePath(p: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
  if (!p.startsWith("/")) return p;
  return `${base}${p}`;
}
