"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Plus, Trash2, Loader2 } from "lucide-react"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { deleteVideo } from "@/services/videosService"
import type { VideoData } from "@/types/types"

interface VideoListProps {
  videos: VideoData[]
  setVideos: (videos: VideoData[]) => void
  selectedVideo: VideoData | null
  setSelectedVideo: (video: VideoData | null) => void
  onSelectVideo: (video: VideoData) => void
  onAddVideo: (videoUrl: string, title: string, description: string) => Promise<void>
}

export function VideoList({
  videos,
  setVideos,
  selectedVideo,
  setSelectedVideo,
  onSelectVideo,
  onAddVideo,
}: VideoListProps) {
  const [videoUrl, setVideoUrl] = useState("")
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [videoTitle, setVideoTitle] = useState("")
  const [videoDescription, setVideoDescription] = useState("")
  const [addVideoModalOpen, setAddVideoModalOpen] = useState(false)
  const [isAddingVideo, setIsAddingVideo] = useState(false)

  const handleAddVideo = async () => {
    if (videoUrl.trim() && videoTitle.trim()) {
      setIsAddingVideo(true)
      await onAddVideo(videoUrl.trim(), videoTitle.trim(), videoDescription.trim())
      setVideoUrl("")
      setVideoTitle("")
      setVideoDescription("")
      setIsAddingVideo(false)
      setAddVideoModalOpen(false)
    }
  }

  const handleAddVideoClick = () => {
    setAddVideoModalOpen(true)
  }

  const handleCancelAddVideo = () => {
    setVideoUrl("")
    setVideoTitle("")
    setVideoDescription("")
    setAddVideoModalOpen(false)
    setIsAddingVideo(false)
  }

  const handleDeleteClick = () => {
    setDeleteModalOpen(true)
    console.log(videos)
  }

  const handleConfirmDelete = () => {
    deleteVideo(selectedVideo?.video_id || "")
    setDeleteModalOpen(false)
    setVideos(videos.filter(v => v.video_id !== selectedVideo?.video_id))
    setSelectedVideo(null)
  }

  const handleCancelDelete = () => {
    setDeleteModalOpen(false)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        {/* <h2 className="text-xl font-semibold mb-3">Video Transcripts</h2> */}
        {/* <div className="space-y-2">
          <Input
            placeholder="Enter video URL or ID..."
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            onKeyDown={handleKeyPress}
          /> */}
          <Button
            onClick={handleAddVideoClick}
            className="w-full !bg-blue-600 hover:!bg-blue-700 active:!bg-blue-800 !text-white transition-colors"
            size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Video
          </Button>
        {/* </div> */}
      </div>

      {/* Video List */}
      <div className="flex-1 overflow-y-auto">
        {videos.map((video) => (
          <div
            key={video.id}
            onClick={() => onSelectVideo(video)}
            className={cn(
              "p-4 hover:bg-accent cursor-pointer transition-colors border-b border-border/50",
              selectedVideo?.id === video.id && "bg-accent",
            )}
          >
            <div className="space-y-2">
              <h3 className="font-medium text-sm leading-tight">{video.title}</h3>
              {video.description && <p className="text-xs text-muted-foreground">{video.description}</p>}
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-muted-foreground bg-muted px-2 py-1 rounded">
                  {video.video_id}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDeleteClick}
                  className="h-6 w-6 p-0 !bg-transparent hover:!bg-destructive/10 hover:!text-destructive !border-0"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
              {/* {video.lastQuery && (
                <p className="text-xs text-muted-foreground italic truncate">Last: {video.lastQuery}</p>
              )} */}
            </div>
          </div>
        ))}
      </div>

      <Dialog open={addVideoModalOpen} onOpenChange={setAddVideoModalOpen}>
        <DialogContent aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Add New Video</DialogTitle>
            {/* <div id="hidden-description" className="sr-only">
              Enter the video URL or ID along with a title and optional description.
            </div> */}
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="video-url">Video URL or ID *</Label>
              <Input
                id="video-url"
                placeholder="Enter video URL or ID..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                disabled={isAddingVideo}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="video-title">Title *</Label>
              <Input
                id="video-title"
                placeholder="Enter video title..."
                value={videoTitle}
                onChange={(e) => setVideoTitle(e.target.value)}
                disabled={isAddingVideo}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="video-description">Description</Label>
              <Input
                id="video-description"
                placeholder="Enter video description (optional)..."
                value={videoDescription}
                onChange={(e) => setVideoDescription(e.target.value)}
                disabled={isAddingVideo}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" 
              onClick={handleCancelAddVideo}
              disabled={isAddingVideo}>
              Cancel
            </Button>
            <Button
              onClick={handleAddVideo}
              disabled={!videoUrl.trim() || !videoTitle.trim() || isAddingVideo}
              className={cn(
                "transition-colors",
                !videoUrl.trim() || !videoTitle.trim() || isAddingVideo
                  ? "!bg-gray-300 !text-gray-500 cursor-not-allowed"
                  : "!bg-blue-600 hover:!bg-blue-700 !text-white",
              )}
            >
              {isAddingVideo ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Adding Video...
                </>
              ) : (
                "Add Video"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={deleteModalOpen} onOpenChange={setDeleteModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Video Transcript</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{selectedVideo?.title}"? This action cannot be undone and will remove all
              associated conversation history.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={handleCancelDelete}>
              Cancel
            </Button>
            <Button 
            variant="destructive" 
            onClick={handleConfirmDelete}
            className="!bg-red-600 hover:!bg-red-700 active:!bg-red-800 !text-white !border-red-600 hover:!border-red-700">
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
