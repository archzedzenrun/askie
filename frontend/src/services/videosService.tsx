import axios from 'axios';
import { z } from 'zod';
import type { NewMessageData, NewVideoData } from '../types/types';
// import { TranscriptData } from '@/types/types';

// const singleSourceSchema = z.object({
//   name: z.string(),
//   database_hostname: z.string(),
//   database_port: z.number(),
//   database_user: z.string(),
//   database_dbname: z.string(),
//   database_server_name: z.string(),
//   slot_name: z.string(),
//   date_created: z.string()
// });

// const sourceSchemaArray = z.object({
//   message: z.string(),
//   data: z.array(singleSourceSchema)
// });

const basePath = "/api"

// const path = import.meta.env.VITE_NODE_ENV === 'development' ? "http://localhost:3001/api/sources" : "/api/sources";

const getVideos = async () => {
  const res = await axios.get(basePath + '/videos');
  return res.data;
};

const sendMessage = async (newMessageData: NewMessageData) => {
  const res = await axios.post(basePath + '/query', newMessageData);
  return res.data;
}

const getMessages = async (video_id: string) => {
  const res = await axios.get(basePath + '/messages/' + video_id);
  return res.data;
}

const newVideo = async (newVideoData: NewVideoData) => {
  const res = await axios.post(basePath + '/embed_transcript', newVideoData);
  return res.data;
}

// const createSource = async (sourceInfo: SourceInput) => {
//   const res = await axios.post(path + '/new_source', sourceInfo);
//   return res.data;
// }

// const deleteSource = async (sourceCredentials: SourceCredentials) => {
//   const res = await axios.delete(path, { data: sourceCredentials });
//   return res.data;
// }

export {
  getVideos,
  sendMessage,
  getMessages,
  newVideo
};