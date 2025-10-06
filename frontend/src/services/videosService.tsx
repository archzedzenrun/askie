import axios from 'axios';
import { z } from 'zod';
import type { NewMessageData, NewVideoData } from '../types/types';

const videoDataSchema = z.object({
  date_created: z.string(),
  description: z.string(),
  id: z.string(),
  summary: z.string(),
  title: z.string(),
  video_id: z.string()
})

const videoSchemaArray = z.object({
  data: z.array(videoDataSchema)
});

const basePath = "/api"

const getVideos = async () => {
  const res = await axios.get(basePath + '/videos');
  console.log(res)
  return videoSchemaArray.parse(res.data);
};

const sendMessage = async (newMessageData: NewMessageData) => {
  const res = await axios.post(basePath + '/query', newMessageData);
  return res.data;
}

const getMessages = async (videoId: string) => {
  const res = await axios.get(basePath + '/messages/' + videoId);
  return res.data;
}

const newVideo = async (newVideoData: NewVideoData) => {
  const res = await axios.post(basePath + '/embed_transcript', newVideoData);
  return res.data;
}

const deleteVideo = async (video_id: string) => {
  const res = await axios.delete(basePath + "/videos", { data: { video_id }});
  return res.data;
}

export {
  getVideos,
  sendMessage,
  getMessages,
  newVideo,
  deleteVideo
};