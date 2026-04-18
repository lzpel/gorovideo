import { getTags, getVideos } from "../../lib/data";
import FindClient from "./FindClient";

export default function FindPage() {
  // Ship just what's needed: minimal video records for client-side filtering.
  const videos = getVideos().map((v) => ({
    id: v.id,
    name: v.name,
    text: v.text,
    icon: v.icon,
    tlen: v.tlen,
    view: v.view,
    qual: v.qual,
    bone: v.bone,
    attr: v.attr,
  }));
  const tags = getTags();
  return <FindClient videos={videos} tags={tags} />;
}
