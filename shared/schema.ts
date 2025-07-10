import { pgTable, text, serial, integer, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const audioFiles = pgTable("audio_files", {
  id: serial("id").primaryKey(),
  originalName: text("original_name").notNull(),
  fileName: text("file_name").notNull(),
  fileSize: integer("file_size").notNull(),
  status: text("status").notNull().default("uploaded"), // uploaded, processing, completed, error
  uploadedAt: timestamp("uploaded_at").defaultNow(),
});

export const separatedTracks = pgTable("separated_tracks", {
  id: serial("id").primaryKey(),
  audioFileId: integer("audio_file_id").references(() => audioFiles.id),
  trackType: text("track_type").notNull(), // vocals, drums, bass, other
  fileName: text("file_name").notNull(),
  filePath: text("file_path").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertAudioFileSchema = createInsertSchema(audioFiles).pick({
  originalName: true,
  fileName: true,
  fileSize: true,
});

export const insertSeparatedTrackSchema = createInsertSchema(separatedTracks).pick({
  audioFileId: true,
  trackType: true,
  fileName: true,
  filePath: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type AudioFile = typeof audioFiles.$inferSelect;
export type InsertAudioFile = z.infer<typeof insertAudioFileSchema>;
export type SeparatedTrack = typeof separatedTracks.$inferSelect;
export type InsertSeparatedTrack = z.infer<typeof insertSeparatedTrackSchema>;
