import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Play, Pause } from "lucide-react";
export function AudioPlayer({ audioFileId, trackType, config }) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const audioRef = useRef(null);
    const togglePlayback = () => {
        if (!audioRef.current)
            return;
        if (isPlaying) {
            audioRef.current.pause();
        }
        else {
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };
    const handleTimeUpdate = () => {
        if (!audioRef.current)
            return;
        setCurrentTime(audioRef.current.currentTime);
    };
    const handleLoadedMetadata = () => {
        if (!audioRef.current)
            return;
        setDuration(audioRef.current.duration);
    };
    const handleSeek = (value) => {
        if (!audioRef.current)
            return;
        const newTime = (value[0] / 100) * duration;
        audioRef.current.currentTime = newTime;
        setCurrentTime(newTime);
    };
    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };
    const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
    return (<div className="space-y-3">
      <audio ref={audioRef} src={`/api/stream/${audioFileId}/${trackType}`} onTimeUpdate={handleTimeUpdate} onLoadedMetadata={handleLoadedMetadata} onEnded={() => setIsPlaying(false)} preload="metadata"/>
      
      <div className="flex items-center space-x-3">
        <Button onClick={togglePlayback} className={`w-10 h-10 ${config.bgColor} rounded-full flex items-center justify-center text-white ${config.buttonHover} transition-colors`}>
          {isPlaying ? <Pause className="w-4 h-4"/> : <Play className="w-4 h-4"/>}
        </Button>
        
        <div className="flex-1">
          {/* Simple waveform visualization */}
          <div className={`h-8 ${config.waveformBg} rounded-md flex items-end justify-center space-x-1 px-2`}>
            {Array.from({ length: 8 }, (_, i) => (<div key={i} className={`w-1 rounded-full transition-all duration-300 ${i < (progress / 100) * 8 ? config.bgColor.replace('bg-', 'bg-') : 'bg-gray-300'}`} style={{
                height: `${Math.random() * 20 + 10}px`,
            }}/>))}
          </div>
        </div>
        
        <span className="text-sm text-gray-500 min-w-[40px]">
          {duration > 0 ? formatTime(duration) : '0:00'}
        </span>
      </div>
      
      <Slider value={[progress]} onValueChange={handleSeek} max={100} step={0.1} className="w-full"/>
    </div>);
}
