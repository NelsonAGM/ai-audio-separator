import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { queryClient } from "@/lib/queryClient";
import { FileUpload } from "@/components/ui/file-upload";
import { AudioPlayer } from "@/components/ui/audio-player";
import { ProgressSteps } from "@/components/ui/progress-steps";
import { 
  Music, 
  AudioWaveform, 
  HelpCircle, 
  CheckCircle, 
  Upload, 
  Cog, 
  Download,
  Plus,
  Mic,
  Drum,
  Guitar,
  Brain,
  Scissors,
  Headphones
} from "lucide-react";

interface AudioFile {
  id: number;
  originalName: string;
  fileName: string;
  fileSize: number;
  status: string;
  uploadedAt: string;
  tracks?: SeparatedTrack[];
}

interface SeparatedTrack {
  id: number;
  audioFileId: number;
  trackType: string;
  fileName: string;
  filePath: string;
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [audioFileId, setAudioFileId] = useState<number | null>(null);
  const [currentSection, setCurrentSection] = useState<'upload' | 'processing' | 'results'>('upload');
  const { toast } = useToast();

  // Query for audio file status
  const { data: audioFile, refetch } = useQuery<AudioFile>({
    queryKey: ['/api/audio', audioFileId],
    enabled: !!audioFileId,
    refetchInterval: audioFileId && currentSection === 'processing' ? 2000 : false,
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('audio', file);
      
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      setAudioFileId(data.id);
      toast({
        title: "Upload successful",
        description: "Your audio file has been uploaded successfully.",
      });
    },
    onError: () => {
      toast({
        title: "Upload failed",
        description: "There was an error uploading your file. Please try again.",
        variant: "destructive",
      });
    },
  });

  // Separation mutation
  const separateMutation = useMutation({
    mutationFn: async (audioId: number) => {
      const response = await fetch(`/api/separate/${audioId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Separation failed');
      }
      
      return response.json();
    },
    onSuccess: () => {
      setCurrentSection('processing');
      toast({
        title: "Processing started",
        description: "Your audio is being separated. This may take 1-3 minutes.",
      });
    },
    onError: () => {
      toast({
        title: "Processing failed",
        description: "There was an error starting the separation process.",
        variant: "destructive",
      });
    },
  });

  // Reset mutation
  const resetMutation = useMutation({
    mutationFn: async (audioId: number) => {
      const response = await fetch(`/api/reset/${audioId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Reset failed');
      }
      
      return response.json();
    },
    onSuccess: () => {
      setCurrentSection('upload');
      refetch();
      toast({
        title: "Reset successful",
        description: "You can now start the separation process again.",
      });
    },
    onError: () => {
      toast({
        title: "Reset failed",
        description: "There was an error resetting the audio file.",
        variant: "destructive",
      });
    },
  });

  // Handle file selection
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) return;
    await uploadMutation.mutateAsync(selectedFile);
  };

  // Handle separation start
  const handleStartSeparation = async () => {
    if (!audioFileId) return;
    await separateMutation.mutateAsync(audioFileId);
  };

  // Handle download track
  const handleDownloadTrack = (trackType: string) => {
    if (!audioFileId) return;
    
    const link = document.createElement('a');
    link.href = `/api/download/track/${audioFileId}/${trackType}`;
    link.download = `${trackType}.wav`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast({
      title: "Download started",
      description: `Downloading ${trackType} track...`,
    });
  };

  // Handle process new file
  const handleProcessNewFile = () => {
    setSelectedFile(null);
    setAudioFileId(null);
    setCurrentSection('upload');
  };

  // Handle reset processing
  const handleResetProcessing = async () => {
    if (!audioFileId) return;
    await resetMutation.mutateAsync(audioFileId);
  };

  // Update section based on status
  if (audioFile?.status === 'completed' && currentSection === 'processing') {
    setCurrentSection('results');
  }

  const trackConfigs = [
    {
      type: 'vocals',
      title: 'Vocals',
      description: 'Lead and backing vocals',
      icon: <Mic className="w-6 h-6" />,
      gradient: 'from-purple-50 to-pink-50',
      border: 'border-purple-200',
      bgColor: 'bg-purple-500',
      textColor: 'text-purple-600',
      hoverColor: 'hover:text-purple-700',
      buttonHover: 'hover:bg-purple-600',
      waveformBg: 'bg-purple-100',
      rangeBg: 'bg-purple-200',
    },
    {
      type: 'drums',
      title: 'Drums',
      description: 'Kick, snare, cymbals',
      icon: <Drum className="w-6 h-6" />,
      gradient: 'from-red-50 to-orange-50',
      border: 'border-red-200',
      bgColor: 'bg-red-500',
      textColor: 'text-red-600',
      hoverColor: 'hover:text-red-700',
      buttonHover: 'hover:bg-red-600',
      waveformBg: 'bg-red-100',
      rangeBg: 'bg-red-200',
    },
    {
      type: 'bass',
      title: 'Bass',
      description: 'Bass guitar & low freq',
      icon: <Guitar className="w-6 h-6" />,
      gradient: 'from-blue-50 to-cyan-50',
      border: 'border-blue-200',
      bgColor: 'bg-blue-500',
      textColor: 'text-blue-600',
      hoverColor: 'hover:text-blue-700',
      buttonHover: 'hover:bg-blue-600',
      waveformBg: 'bg-blue-100',
      rangeBg: 'bg-blue-200',
    },
    {
      type: 'other',
      title: 'Other',
      description: 'Piano, strings, etc.',
      icon: <Music className="w-6 h-6" />,
      gradient: 'from-green-50 to-emerald-50',
      border: 'border-green-200',
      bgColor: 'bg-green-500',
      textColor: 'text-green-600',
      hoverColor: 'hover:text-green-700',
      buttonHover: 'hover:bg-green-600',
      waveformBg: 'bg-green-100',
      rangeBg: 'bg-green-200',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <AudioWaveform className="text-white text-lg" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Audio Separator</h1>
                <p className="text-xs text-gray-500">Powered by Spleeter AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 hidden sm:block">Free • No Registration Required</span>
              <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-600">
                <HelpCircle className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Separate Your Music into
            <span className="text-primary"> Individual Tracks</span>
          </h2>
          <p className="text-xl text-gray-600 mb-6 max-w-3xl mx-auto">
            Upload any song and our AI will automatically separate it into vocals, drums, bass, and other instruments. 
            Perfect for remixing, karaoke, or music production.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500">
            <span className="flex items-center">
              <CheckCircle className="w-4 h-4 text-secondary mr-2" />
              MP3 & WAV Support
            </span>
            <span className="flex items-center">
              <CheckCircle className="w-4 h-4 text-secondary mr-2" />
              AI-Powered Separation
            </span>
            <span className="flex items-center">
              <CheckCircle className="w-4 h-4 text-secondary mr-2" />
              Individual Downloads
            </span>
            <span className="flex items-center">
              <CheckCircle className="w-4 h-4 text-secondary mr-2" />
              No Registration
            </span>
          </div>
        </div>

        {/* Upload Section */}
        {currentSection === 'upload' && (
          <Card className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8">
            <CardContent className="p-0">
              <div className="text-center">
                <div className="mx-auto w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center mb-6">
                  <Upload className="text-primary text-3xl" />
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">Upload Your Audio File</h3>
                <p className="text-gray-600 mb-8">Drag and drop your file here, or click to browse</p>
                
                <FileUpload onFileSelect={handleFileSelect} selectedFile={selectedFile} />

                {selectedFile && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Music className="text-primary" />
                        <div className="text-left">
                          <p className="font-medium text-gray-900">{selectedFile.name}</p>
                          <p className="text-sm text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(1)} MB</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedFile(null)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        ×
                      </Button>
                    </div>
                  </div>
                )}

                {selectedFile && !audioFileId && (
                  <Button
                    onClick={handleUpload}
                    disabled={uploadMutation.isPending}
                    className="mt-6 bg-secondary text-white px-8 py-3 hover:bg-emerald-700"
                  >
                    {uploadMutation.isPending ? (
                      <>
                        <Cog className="w-4 h-4 mr-2 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Upload File
                      </>
                    )}
                  </Button>
                )}

                {audioFileId && audioFile?.status === 'uploaded' && (
                  <Button
                    onClick={handleStartSeparation}
                    disabled={separateMutation.isPending}
                    className="mt-6 bg-secondary text-white px-8 py-3 hover:bg-emerald-700"
                  >
                    {separateMutation.isPending ? (
                      <>
                        <Cog className="w-4 h-4 mr-2 animate-spin" />
                        Starting...
                      </>
                    ) : (
                      <>
                        <Scissors className="w-4 h-4 mr-2" />
                        Start AI Separation
                      </>
                    )}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Processing Section */}
        {currentSection === 'processing' && (
          <Card className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8">
            <CardContent className="p-0">
              <div className="text-center">
                <div className="mx-auto w-24 h-24 bg-yellow-50 rounded-full flex items-center justify-center mb-6">
                  <Cog className="text-yellow-500 text-3xl animate-spin" />
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">Processing Your Audio</h3>
                <p className="text-gray-600 mb-8">Our AI is separating the instruments. This may take 1-3 minutes...</p>
                
                <div className="max-w-lg mx-auto mb-8">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progress</span>
                    <span>Processing...</span>
                  </div>
                  <Progress value={65} className="h-3" />
                  <p className="text-sm text-gray-500 mt-3">Analyzing audio structure...</p>
                </div>

                <ProgressSteps currentStep={audioFile?.status || 'processing'} />
                
                {/* Reset button for stuck processing */}
                <div className="mt-8 pt-6 border-t border-gray-200">
                  <Button
                    onClick={handleResetProcessing}
                    disabled={resetMutation.isPending}
                    variant="outline"
                    className="bg-red-50 text-red-600 border-red-200 hover:bg-red-100"
                  >
                    {resetMutation.isPending ? (
                      <>
                        <Cog className="w-4 h-4 mr-2 animate-spin" />
                        Resetting...
                      </>
                    ) : (
                      <>
                        <HelpCircle className="w-4 h-4 mr-2" />
                        Reset & Try Again
                      </>
                    )}
                  </Button>
                  <p className="text-sm text-gray-500 mt-2">
                    If processing is stuck, click to reset and try again
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Section */}
        {currentSection === 'results' && audioFile?.tracks && (
          <Card className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <CardContent className="p-0">
              <div className="text-center mb-8">
                <div className="mx-auto w-24 h-24 bg-green-50 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle className="text-secondary text-3xl" />
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">Separation Complete!</h3>
                <p className="text-gray-600">Your audio has been successfully separated into individual tracks</p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {trackConfigs.map((config) => {
                  const track = audioFile.tracks?.find(t => t.trackType === config.type);
                  if (!track) return null;

                  return (
                    <div key={config.type} className={`bg-gradient-to-br ${config.gradient} border ${config.border} rounded-xl p-6`}>
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className={`w-12 h-12 ${config.bgColor} rounded-lg flex items-center justify-center text-white`}>
                            {config.icon}
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900">{config.title}</h4>
                            <p className="text-sm text-gray-600">{config.description}</p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownloadTrack(config.type)}
                          className={`${config.textColor} ${config.hoverColor}`}
                        >
                          <Download className="w-5 h-5" />
                        </Button>
                      </div>
                      
                      <AudioPlayer
                        audioFileId={audioFileId!}
                        trackType={config.type}
                        config={config}
                      />
                    </div>
                  );
                })}
              </div>

              <div className="text-center mt-8 pt-6 border-t border-gray-200">
                <Button
                  className="bg-primary text-white px-8 py-3 hover:bg-blue-700 mr-4"
                  onClick={() => {
                    // Download all tracks
                    trackConfigs.forEach(config => {
                      if (audioFile.tracks?.find(t => t.trackType === config.type)) {
                        handleDownloadTrack(config.type);
                      }
                    });
                  }}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download All Tracks
                </Button>
                <Button
                  variant="outline"
                  onClick={handleProcessNewFile}
                  className="bg-gray-100 text-gray-700 px-6 py-3 hover:bg-gray-200"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Process Another File
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Feature Info */}
        <Card className="mt-16 bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
          <CardContent className="p-0">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">How It Works</h3>
              <p className="text-gray-600 max-w-2xl mx-auto">Our AI uses advanced source separation technology to identify and isolate different instruments in your audio</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Brain className="text-primary text-2xl" />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">AI Analysis</h4>
                <p className="text-gray-600 text-sm">Advanced neural networks analyze your audio to identify different sound sources and their frequencies</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Scissors className="text-secondary text-2xl" />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Smart Separation</h4>
                <p className="text-gray-600 text-sm">Each instrument is carefully separated while preserving audio quality and maintaining proper timing</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Headphones className="text-purple-600 text-2xl" />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Ready to Use</h4>
                <p className="text-gray-600 text-sm">Download high-quality separated tracks ready for remixing, karaoke, or music production</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <AudioWaveform className="text-white text-sm" />
              </div>
              <span className="font-semibold text-gray-900">AI Audio Separator</span>
            </div>
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-primary transition-colors">Support</a>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
            <p>Powered by Spleeter AI technology. Audio processing happens securely and files are automatically deleted after 24 hours.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
