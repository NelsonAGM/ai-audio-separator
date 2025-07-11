export class MemStorage {
    users;
    audioFiles;
    separatedTracks;
    currentUserId;
    currentAudioFileId;
    currentTrackId;
    constructor() {
        this.users = new Map();
        this.audioFiles = new Map();
        this.separatedTracks = new Map();
        this.currentUserId = 1;
        this.currentAudioFileId = 1;
        this.currentTrackId = 1;
    }
    async getUser(id) {
        return this.users.get(id);
    }
    async getUserByUsername(username) {
        return Array.from(this.users.values()).find((user) => user.username === username);
    }
    async createUser(insertUser) {
        const id = this.currentUserId++;
        const user = { ...insertUser, id };
        this.users.set(id, user);
        return user;
    }
    async createAudioFile(insertAudioFile) {
        const id = this.currentAudioFileId++;
        const audioFile = {
            ...insertAudioFile,
            id,
            status: "uploaded",
            uploadedAt: new Date(),
        };
        this.audioFiles.set(id, audioFile);
        return audioFile;
    }
    async getAudioFile(id) {
        return this.audioFiles.get(id);
    }
    async updateAudioFileStatus(id, status) {
        const audioFile = this.audioFiles.get(id);
        if (audioFile) {
            this.audioFiles.set(id, { ...audioFile, status });
        }
    }
    async createSeparatedTrack(insertTrack) {
        const id = this.currentTrackId++;
        const track = {
            ...insertTrack,
            id,
            audioFileId: insertTrack.audioFileId || 0
        };
        this.separatedTracks.set(id, track);
        return track;
    }
    async getSeparatedTracksByAudioFileId(audioFileId) {
        return Array.from(this.separatedTracks.values()).filter((track) => track.audioFileId === audioFileId);
    }
    async deleteSeparatedTracksByAudioFileId(audioFileId) {
        const tracksToDelete = Array.from(this.separatedTracks.entries()).filter(([_, track]) => track.audioFileId === audioFileId);
        for (const [id, _] of tracksToDelete) {
            this.separatedTracks.delete(id);
        }
    }
}
export const storage = new MemStorage();
