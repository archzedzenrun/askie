"use client"

import type React from "react"

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
import { Plus, Trash2 } from "lucide-react"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
// import type { VideoConversation } from "./chat-layout"
import type { VideoData } from "@/types/types"

interface VideoListProps {
  videos: VideoData[]
  selectedVideo: VideoData | null
  onSelectVideo: (video: VideoData) => void
  onAddVideo: (videoUrl: string, title: string, description: string) => void
}

export function VideoList({
  videos,
  selectedVideo,
  onSelectVideo,
  onAddVideo,
  // onDeleteVideo
}: VideoListProps) {
  const [videoUrl, setVideoUrl] = useState("")
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [videoToDelete, setVideoToDelete] = useState<VideoConversation | null>(null)
  const [videoTitle, setVideoTitle] = useState("")
  const [videoDescription, setVideoDescription] = useState("")
  const [addVideoModalOpen, setAddVideoModalOpen] = useState(false)

  const handleAddVideo = () => {
    if (videoUrl.trim()) {
      onAddVideo(videoUrl.trim())
      setVideoUrl("")
    }
  }

  // const handleKeyPress = (e: React.KeyboardEvent) => {
  //   if (e.key === "Enter") {
  //     e.preventDefault()
  //     handleAddVideo()
  //   }
  // }

  const handleAddVideoClick = () => {
    setAddVideoModalOpen(true)
  }

  const handleCancelAddVideo = () => {
    setVideoUrl("")
    setVideoTitle("")
    setVideoDescription("")
    setAddVideoModalOpen(false)
  }

  const handleDeleteClick = (e: React.MouseEvent, conversation: VideoConversation) => {
    e.stopPropagation()
    setVideoToDelete(conversation)
    setDeleteModalOpen(true)
  }

  const handleConfirmDelete = () => {
    if (videoToDelete) {
      onDeleteVideo(videoToDelete.id)
      setDeleteModalOpen(false)
      setVideoToDelete(null)
    }
  }

  const handleCancelDelete = () => {
    setDeleteModalOpen(false)
    setVideoToDelete(null)
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
                  onClick={(e) => handleDeleteClick(e, conversation)}
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
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add New Video</DialogTitle>
            {/* <DialogDescription>
              Enter the video URL or ID along with a title and optional description.
            </DialogDescription> */}
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="video-url">Video URL or ID *</Label>
              <Input
                id="video-url"
                placeholder="Enter video URL or ID..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="video-title">Title *</Label>
              <Input
                id="video-title"
                placeholder="Enter video title..."
                value={videoTitle}
                onChange={(e) => setVideoTitle(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="video-description">Description</Label>
              <Textarea
                id="video-description"
                placeholder="Enter video description (optional)..."
                value={videoDescription}
                onChange={(e) => setVideoDescription(e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleCancelAddVideo}>
              Cancel
            </Button>
            <Button
              onClick={handleAddVideo}
              disabled={!videoUrl.trim() || !videoTitle.trim()}
              className={cn(
                "transition-colors",
                !videoUrl.trim() || !videoTitle.trim()
                  ? "!bg-gray-300 !text-gray-500 cursor-not-allowed"
                  : "!bg-blue-600 hover:!bg-blue-700 !text-white",
              )}
            >
              Add Video
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
              Are you sure you want to delete "{videoToDelete?.title}"? This action cannot be undone and will remove all
              associated conversation history.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={handleCancelDelete}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleConfirmDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
