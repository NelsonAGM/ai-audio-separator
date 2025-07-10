import { users, audioFiles, separatedTracks, type User, type InsertUser, type AudioFile, type InsertAudioFile, type SeparatedTrack, type InsertSeparatedTrack } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  createAudioFile(audioFile: InsertAudioFile): Promise<AudioFile>;
  getAudioFile(id: number): Promise<AudioFile | undefined>;
  updateAudioFileStatus(id: number, status: string): Promise<void>;
  
  createSeparatedTrack(track: InsertSeparatedTrack): Promise<SeparatedTrack>;
  getSeparatedTracksByAudioFileId(audioFileId: number): Promise<SeparatedTrack[]>;
  deleteSeparatedTracksByAudioFileId(audioFileId: number): Promise<void>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private audioFiles: Map<number, AudioFile>;
  private separatedTracks: Map<number, SeparatedTrack>;
  private currentUserId: number;
  private currentAudioFileId: number;
  private currentTrackId: number;

  constructor() {
    this.users = new Map();
    this.audioFiles = new Map();
    this.separatedTracks = new Map();
    this.currentUserId = 1;
    this.currentAudioFileId = 1;
    this.currentTrackId = 1;
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createAudioFile(insertAudioFile: InsertAudioFile): Promise<AudioFile> {
    const id = this.currentAudioFileId++;
    const audioFile: AudioFile = {
      ...insertAudioFile,
      id,
      status: "uploaded",
      uploadedAt: new Date(),
    };
    this.audioFiles.set(id, audioFile);
    return audioFile;
  }

  async getAudioFile(id: number): Promise<AudioFile | undefined> {
    return this.audioFiles.get(id);
  }

  async updateAudioFileStatus(id: number, status: string): Promise<void> {
    const audioFile = this.audioFiles.get(id);
    if (audioFile) {
      this.audioFiles.set(id, { ...audioFile, status });
    }
  }

  async createSeparatedTrack(insertTrack: InsertSeparatedTrack): Promise<SeparatedTrack> {
    const id = this.currentTrackId++;
    const track: SeparatedTrack = { 
      ...insertTrack, 
      id,
      audioFileId: insertTrack.audioFileId || 0
    };
    this.separatedTracks.set(id, track);
    return track;
  }

  async getSeparatedTracksByAudioFileId(audioFileId: number): Promise<SeparatedTrack[]> {
    return Array.from(this.separatedTracks.values()).filter(
      (track) => track.audioFileId === audioFileId,
    );
  }

  async deleteSeparatedTracksByAudioFileId(audioFileId: number): Promise<void> {
    const tracksToDelete = Array.from(this.separatedTracks.entries()).filter(
      ([_, track]) => track.audioFileId === audioFileId,
    );
    
    for (const [id, _] of tracksToDelete) {
      this.separatedTracks.delete(id);
    }
  }
}

export const storage = new MemStorage();
