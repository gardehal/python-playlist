# YouTube Download Strategy: Evolution & Implementation

## Current Status (2026-11-07)

The application now uses yt-dlp without pytubefix. The user verified CLI YouTube
title lookup and a short-video download through the application. The earlier
pytubefix rescue implementation below is historical; the previously problematic
sample corpus was not retested. Audio-only download remains unsupported.

## Overview
The goal of this task was to implement a robust YouTube downloading service in Python that works reliably across different environments (specifically those without a JavaScript runtime like Node.js or Deno) and avoids `403 Forbidden` errors caused by YouTube's frequent signature obfuscation updates.

## The Core Problem: The "Signature Wall"
YouTube uses complex JavaScript to generate "signatures" for video URLs. 
- **High-Intelligence Clients (`yt-dlp`)**: Use a JS engine to execute this logic. They are powerful but depend on external runtimes (Node/Deno).
- **Regex-Based Clients (`pytubefix`/`yt-dlp` fallback)**: Use text pattern matching to "guess" the signature. They are lightweight and dependency-free but break whenever YouTube changes their HTML/JS structure.

## Experimentation Log

### Attempt 1: Standard `yt-dlp` with Android/iOS Plugins
*   **Approach**: Configure `yt-dlp` to use the `android` or `ios` extractor plugins and a modern User-Agent.
*   **Result**: **FAILED**.
*   **Reason**: YouTube's mobile clients are highly obfuscated. Without a JS engine, `yt-dlp` could not solve the signature, resulting in `403 Forbidden` errors.

### Attempt 2: The "Legacy Web" Strategy
*   **Approach**: Force `yt-dlp` to use an older `compatibility_version` (e.g., `5.20230101`) and a standard Web User-Agent. This was intended to request a simpler, less-obfuscated API version from YouTube.
*   **Result**: **PARTIAL SUCCESS**.
*   **Reason**: It worked for roughly 12 videos in the test set, but then hit a "plateau." The remaining videos used modern signature algorithms that even the legacy web client couldn't resolve without a JS engine.

### Attempt 3: The "mweb" (Mobile Web) Strategy
*   **Approach**: Switch the `yt-dlp` client to `mweb` and use a mobile-specific User-Agent. The idea was that the mobile web API is lighter and easier for regex to parse than the desktop `web` or `android` clients.
*   **Result**: **PARTIAL SUCCESS**.
*   **Reason**: While it improved some aspects, it still hit the same "Signature Wall" at the exact same 12-video limit, proving that no amount of client spoofing can bypass a hard signature requirement without actual JS execution.

### Earlier Implementation: Hybrid Rescue Method (Historical)
*   **Approach**: Implement a dual-engine architecture in `DownloadService.py`.
    1.  **Primary Engine**: `yt-dlp` using the `mweb` client (for high quality and feature support).
    2.  **Fallback/Rescue Engine**: `pytubefix` (a pure-Python, regex-based library) used in a `try-except` block when `yt-dlp` fails.
*   **Result**: **SUCCESS**.
*   **Reason**: This provides the best of both worlds: high-quality downloads when possible, and a "resilient" fallback that can bypass signature walls by using simpler (though less feature-rich) stream requests.

## Current Implementation Details (2026-11-07)
- **File**: `services/DownloadService.py`
- **Downloader**: yt-dlp only; the pytubefix branch and dependency have been removed.
- **Runtime**: `DownloadService` configures Node.js for yt-dlp when it is available.
- **Validation**: The user verified CLI title lookup and a short-video download through the app; the earlier failure corpus was not retested.

## Remaining Limits
- **Historical failure cases**: The full set of videos that failed in earlier yt-dlp experiments was not retested after migration.
- **Audio-only**: The active yt-dlp download path does not currently honor `audioOnly`.
