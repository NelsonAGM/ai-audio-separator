import { useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Music, Upload } from "lucide-react";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  maxSize?: number; // in MB
}

export function FileUpload({ onFileSelect, selectedFile, maxSize = 50 }: FileUploadProps) {
  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const files = Array.from(e.dataTransfer.files);
      const audioFile = files.find(file => 
        file.type.includes('audio') || 
        file.name.toLowerCase().endsWith('.mp3') || 
        file.name.toLowerCase().endsWith('.wav')
      );
      
      if (audioFile) {
        if (audioFile.size > maxSize * 1024 * 1024) {
          alert(`File size must be less than ${maxSize}MB`);
          return;
        }
        onFileSelect(audioFile);
      } else {
        alert('Please upload an MP3 or WAV file');
      }
    },
    [onFileSelect, maxSize]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > maxSize * 1024 * 1024) {
        alert(`File size must be less than ${maxSize}MB`);
        return;
      }
      onFileSelect(file);
    }
  };

  return (
    <div
      className="border-2 border-dashed border-gray-300 rounded-xl p-12 hover:border-primary hover:bg-blue-50 transition-all duration-300 cursor-pointer"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onClick={() => document.getElementById('audioFileInput')?.click()}
    >
      <input
        type="file"
        id="audioFileInput"
        className="hidden"
        accept=".mp3,.wav,audio/*"
        onChange={handleFileInput}
      />
      <div className="space-y-4 text-center">
        <Music className="text-gray-400 text-4xl mx-auto" />
        <div>
          <p className="text-lg font-medium text-gray-700">Drop your audio file here</p>
          <p className="text-sm text-gray-500">Supports MP3, WAV up to {maxSize}MB</p>
        </div>
        <Button className="bg-primary text-white px-6 py-3 hover:bg-blue-700">
          <Upload className="w-4 h-4 mr-2" />
          Choose File
        </Button>
      </div>
    </div>
  );
}
