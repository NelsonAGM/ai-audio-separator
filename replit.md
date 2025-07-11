# Audio Separation App - replit.md

## Overview

This is an AI-powered audio separation web application that allows users to upload audio files (MP3, WAV) and separate them into individual instrument tracks using machine learning. The application uses a full-stack TypeScript architecture with React frontend, Express backend, and Drizzle ORM for database management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React with TypeScript
- **UI Library**: Radix UI components with shadcn/ui styling system
- **Styling**: Tailwind CSS with CSS variables for theming
- **State Management**: TanStack Query (React Query) for server state
- **Routing**: Wouter for client-side routing
- **Build Tool**: Vite with React plugin

### Backend Architecture
- **Runtime**: Node.js with Express.js
- **Language**: TypeScript with ES modules
- **File Upload**: Multer middleware for handling audio file uploads
- **AI Processing**: Python integration using Spleeter for audio source separation
- **API**: RESTful endpoints for file upload and processing

### Database Architecture
- **ORM**: Drizzle ORM with PostgreSQL dialect
- **Database**: Neon Database (serverless PostgreSQL)
- **Schema**: Three main tables:
  - `users`: User authentication data
  - `audio_files`: Uploaded audio file metadata and processing status
  - `separated_tracks`: Individual separated audio tracks per file

## Key Components

### Data Models
- **AudioFile**: Tracks uploaded files with processing status (uploaded, processing, completed, error)
- **SeparatedTrack**: Stores metadata for individual instrument tracks (vocals, drums, bass, other)
- **User**: Basic user management (currently minimal implementation)

### Frontend Components
- **FileUpload**: Drag-and-drop interface for audio file uploads
- **AudioPlayer**: Custom audio playback controls for separated tracks
- **ProgressSteps**: Visual progress indicator for processing stages
- **Home Page**: Main application interface coordinating upload, processing, and results

### Backend Services
- **Storage Interface**: Abstracted storage layer with in-memory implementation (ready for database integration)
- **Audio Processor**: Python script integration using advanced spectral filtering techniques for high-quality audio separation
- **File Management**: Temporary file storage and cleanup in uploads/separated directories
- **Multiple Processors**: Simple (fast), Advanced (high-quality), and Demucs (AI-based) processing options

## Data Flow

1. **Upload Phase**: User uploads audio file through drag-and-drop interface
2. **Storage Phase**: File saved to temporary storage, metadata recorded in database
3. **Processing Phase**: Python script processes audio using advanced spectral filtering and frequency analysis
4. **Separation Phase**: Four tracks generated using intelligent frequency masking (vocals, drums, bass, other instruments)
5. **Completion Phase**: Separated tracks saved and made available for playback/download

## External Dependencies

### AI/ML Dependencies
- **Librosa**: Advanced audio processing and analysis library for spectral filtering
- **SoundFile**: Audio file I/O operations
- **SciPy**: Signal processing filters (Butterworth filters for frequency separation)
- **NumPy**: Mathematical operations for audio processing
- **Demucs**: Facebook's modern audio separation model (installed but CPU-intensive)
- **PyTorch**: Deep learning framework for AI models

### Database
- **Neon Database**: Serverless PostgreSQL for production
- **Drizzle Kit**: Database migrations and schema management

### UI/UX
- **Radix UI**: Headless component primitives
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Icon library

## Deployment Strategy

### Development
- **Dev Server**: Vite development server with HMR
- **Database**: Local PostgreSQL or Neon development instance
- **File Storage**: Local filesystem (uploads/ and separated/ directories)

### Production Build
- **Frontend**: Vite build outputs to dist/public
- **Backend**: esbuild bundles server code to dist/index.js
- **Environment**: NODE_ENV=production with appropriate database URLs

### Resource Considerations
- **Memory**: AI processing requires significant RAM for model loading
- **CPU**: Audio separation is computationally intensive
- **Storage**: Temporary file management with automatic cleanup
- **Processing Time**: Variable based on audio length and complexity

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `NODE_ENV`: Environment mode (development/production)

The application is designed as a proof-of-concept for AI-powered audio separation, balancing functionality with resource constraints typical of cloud development environments.