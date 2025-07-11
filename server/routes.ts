import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage.js";
import { insertAudioFileSchema, insertSeparatedTrackSchema } from "../shared/schema.js";
import multer from "multer";
import path from "path";
import fs from "fs";
import { spawn } from "child_process";

const upload = multer({
  dest: "uploads/",
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = [".mp3", ".wav"];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error("Only MP3 and WAV files are allowed"));
    }
  },
});

export async function registerRoutes(app: Express): Promise<Server> {
  // Create uploads and output directories
  const uploadsDir = path.join(process.cwd(), "uploads");
  const outputDir = path.join(process.cwd(), "separated");
  
  if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
  }
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Upload audio file
  app.post("/api/upload", upload.single("audio"), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "No file uploaded" });
      }

      const audioFileData = {
        originalName: req.file.originalname,
        fileName: req.file.filename,
        fileSize: req.file.size,
      };

      const validation = insertAudioFileSchema.safeParse(audioFileData);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid file data", errors: validation.error.errors });
      }

      const audioFile = await storage.createAudioFile(validation.data);
      res.json(audioFile);
    } catch (error) {
      console.error("Upload error:", error);
      res.status(500).json({ message: "Upload failed" });
    }
  });

  // Reset audio file status
  app.post("/api/reset/:id", async (req, res) => {
    try {
      const audioFileId = parseInt(req.params.id);
      const audioFile = await storage.getAudioFile(audioFileId);

      if (!audioFile) {
        return res.status(404).json({ message: "Audio file not found" });
      }

      // Reset status and clear any existing tracks
      await storage.updateAudioFileStatus(audioFileId, "uploaded");
      await storage.deleteSeparatedTracksByAudioFileId(audioFileId);

      res.json({ message: "Audio file reset successfully", audioFileId });
    } catch (error) {
      console.error("Reset error:", error);
      res.status(500).json({ message: "Failed to reset audio file" });
    }
  });

  // Start audio separation process
  app.post("/api/separate/:id", async (req, res) => {
    try {
      const audioFileId = parseInt(req.params.id);
      const audioFile = await storage.getAudioFile(audioFileId);

      if (!audioFile) {
        return res.status(404).json({ message: "Audio file not found" });
      }

      if (audioFile.status !== "uploaded") {
        return res.status(400).json({ message: "File is already being processed or completed" });
      }

      // Update status to processing
      await storage.updateAudioFileStatus(audioFileId, "processing");

      // Start separation process asynchronously
      setTimeout(async () => {
        try {
          const inputPath = path.join(uploadsDir, audioFile.fileName);
          const outputPath = path.join(outputDir, `${audioFile.fileName}_separated`);

          // Create output directory for this file
          if (!fs.existsSync(outputPath)) {
            fs.mkdirSync(outputPath, { recursive: true });
          }

          // Run AI-powered audio separation with intelligent processor selection
          const pythonProcess = spawn("python", [
            path.join(process.cwd(), "server/services/ai-processor.py"),
            inputPath,
            outputPath,
          ], {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env, PYTHONPATH: process.cwd() }
          });

          // Set timeout for long-running processes (10 minutes)
          const timeoutId = setTimeout(() => {
            console.error("Process timeout reached, killing Python process");
            pythonProcess.kill('SIGTERM');
          }, 10 * 60 * 1000); // 10 minutes

          // Log Python process output
          pythonProcess.stdout?.on('data', (data) => {
            console.log(`Python stdout: ${data}`);
          });

          pythonProcess.stderr?.on('data', (data) => {
            console.error(`Python stderr: ${data}`);
          });

          pythonProcess.on("close", async (code) => {
            clearTimeout(timeoutId);
            console.log(`Python process exited with code ${code}`);
            if (code === 0) {
              // Process completed successfully, create track records
              const trackTypes = ["vocals", "drums", "bass", "other"];
              
              for (const trackType of trackTypes) {
                const trackFileName = `${trackType}.wav`;
                const trackFilePath = path.join(outputPath, trackFileName);
                
                if (fs.existsSync(trackFilePath)) {
                  await storage.createSeparatedTrack({
                    audioFileId,
                    trackType,
                    fileName: trackFileName,
                    filePath: trackFilePath,
                  });
                  console.log(`Created track record for ${trackType}`);
                }
              }

              await storage.updateAudioFileStatus(audioFileId, "completed");
              console.log(`Audio file ${audioFileId} processing completed`);
            } else {
              console.error(`Spleeter process failed with code ${code}`);
              await storage.updateAudioFileStatus(audioFileId, "error");
            }
          });

          pythonProcess.on("error", async (error) => {
            clearTimeout(timeoutId);
            console.error("Spleeter process error:", error);
            await storage.updateAudioFileStatus(audioFileId, "error");
          });

        } catch (error) {
          console.error("Separation error:", error);
          await storage.updateAudioFileStatus(audioFileId, "error");
        }
      }, 1000);

      res.json({ message: "Separation started", audioFileId });
    } catch (error) {
      console.error("Separation start error:", error);
      res.status(500).json({ message: "Failed to start separation" });
    }
  });

  // Get audio file status and tracks
  app.get("/api/audio/:id", async (req, res) => {
    try {
      const audioFileId = parseInt(req.params.id);
      const audioFile = await storage.getAudioFile(audioFileId);

      if (!audioFile) {
        return res.status(404).json({ message: "Audio file not found" });
      }

      const tracks = await storage.getSeparatedTracksByAudioFileId(audioFileId);
      
      res.json({
        ...audioFile,
        tracks,
      });
    } catch (error) {
      console.error("Get audio error:", error);
      res.status(500).json({ message: "Failed to get audio file" });
    }
  });

  // Download separated track
  app.get("/api/download/track/:audioId/:trackType", async (req, res) => {
    try {
      const audioFileId = parseInt(req.params.audioId);
      const trackType = req.params.trackType;

      const tracks = await storage.getSeparatedTracksByAudioFileId(audioFileId);
      const track = tracks.find(t => t.trackType === trackType);

      if (!track || !fs.existsSync(track.filePath)) {
        return res.status(404).json({ message: "Track not found" });
      }

      res.download(track.filePath, track.fileName);
    } catch (error) {
      console.error("Download track error:", error);
      res.status(500).json({ message: "Download failed" });
    }
  });

  // Stream audio track for playback
  app.get("/api/stream/:audioId/:trackType", async (req, res) => {
    try {
      const audioFileId = parseInt(req.params.audioId);
      const trackType = req.params.trackType;

      const tracks = await storage.getSeparatedTracksByAudioFileId(audioFileId);
      const track = tracks.find(t => t.trackType === trackType);

      if (!track || !fs.existsSync(track.filePath)) {
        return res.status(404).json({ message: "Track not found" });
      }

      const stat = fs.statSync(track.filePath);
      const fileSize = stat.size;
      const range = req.headers.range;

      if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
        const chunksize = (end - start) + 1;
        const file = fs.createReadStream(track.filePath, { start, end });
        const head = {
          'Content-Range': `bytes ${start}-${end}/${fileSize}`,
          'Accept-Ranges': 'bytes',
          'Content-Length': chunksize,
          'Content-Type': 'audio/wav',
        };
        res.writeHead(206, head);
        file.pipe(res);
      } else {
        const head = {
          'Content-Length': fileSize,
          'Content-Type': 'audio/wav',
        };
        res.writeHead(200, head);
        fs.createReadStream(track.filePath).pipe(res);
      }
    } catch (error) {
      console.error("Stream track error:", error);
      res.status(500).json({ message: "Stream failed" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
