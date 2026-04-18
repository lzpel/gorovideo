export type Blob = { idx: number; quality: "lq" | "hq" | "u"; size: number };

export type Video = {
  id: number;
  name: string;
  text: string;
  icon: string | null; // data URI thumbnail
  authorId: number | null;
  view: number;
  qual: number;
  bone: string; // ISO datetime
  tlen: number;
  tpos: number;
  attr: string[];
  blobs: Blob[];
};

export type User = {
  id: number;
  name: string;
  icon: string | null;
  text: string;
};

export type Comment = {
  id: number;
  authorId: number | null;
  text: string;
  tpos: number; // seconds within video, for barrage
  bone: string;
};

export type CommentsMap = Record<string, Comment[]>; // keyed by video id string

export type Tag = { name: string; videoIds: number[] };

export type Dead = {
  filename: string;
  origFilename: string | null;
  size: number;
  quality: "lq" | "hq" | "u";
  creation: string | null;
};
