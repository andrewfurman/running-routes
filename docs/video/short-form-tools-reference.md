# Short-form trip video tools

Recorded: November 1, 2026.

## Purpose and starting decision

Use this repository for content about past trips as well as planning and filming future trips. This folder holds reusable video workflow notes; individual trip folders can hold their own story ideas and shot lists.

The immediate goal is simple vlog-style footage of Andrew walking around and talking, edited into short videos with occasional motion graphics. The preference expressed in the supplied conversation is **FFmpeg + ElevenLabs Scribe (or comparable transcription) + Remotion**. Start there and evaluate DaVinci Resolve when a specific editing need justifies it.

This is a tool reference and proposed workflow. It does not indicate that any software, account, skill, or MCP integration has been installed or tested here.

## Core stack

| Tool | Role in the workflow | Decision / practical detail |
| --- | --- | --- |
| [FFmpeg](https://ffmpeg.org/ffmpeg.html) | Trim and join clips, reframe, filter, encode, mix audio, burn captions, and composite overlays. | Preferred editing and rendering engine. Precise cuts generally require re-encoding; stream-copy cuts can be constrained by keyframes. |
| [ffprobe](https://ffmpeg.org/ffprobe.html) | Inspect duration, resolution, frame rate, codecs, and audio streams. | Use before editing and to check exports. |
| [ElevenLabs Scribe](https://elevenlabs.io/docs/overview/capabilities/speech-to-text) | Speech-to-text with word timestamps and speaker labels. | Preferred transcription candidate. Timing supports cut lists and captions; review names, places, and cut boundaries. Audio sent to Scribe is processed by a cloud service. |
| [Remotion](https://www.remotion.dev/docs/) | Create graphics with React: titles, lower thirds, location labels, animated callouts, and end cards. | Preferred graphics layer. Render overlays or entire compositions. [Transparent exports](https://www.remotion.dev/docs/transparent-videos) need an alpha-capable format; an ordinary H.264 MP4 is not a transparent overlay. |
| Coding agent + scripts / custom skills | Turn a brief and transcript into an edit plan, invoke tools, and revise drafts. | The thread mentions Claude Code and Codex as orchestrators. They require access to media and editing tools to execute an edit. Python or a small CLI can connect the steps. |

Useful [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) include `trim`/`atrim`, `concat`, `scale`/`crop`, `overlay`, `subtitles`, `highpass`, `afftdn`, `loudnorm`, `afade`, `eq`, `curves`, and `lut3d`. Availability depends on the build. Noise reduction can help, but badly clipped or wind-damaged walking audio still needs listening and judgment.

## Other tools mentioned in the thread

These are alternatives or additions to investigate, rather than a list of required dependencies.

| Tool / category | Why it came up | Relevance now |
| --- | --- | --- |
| [Whisper](https://github.com/openai/whisper) / [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Alternative transcription, including local execution. | Evaluate if local transcription is desirable. Check word-timing quality and speaker-label requirements rather than assuming parity with Scribe. |
| [video-use](https://github.com/browser-use/video-use) | Existing skill for coding agents, using transcription, FFmpeg edits, captions, and generated graphics. | Potential shortcut to assembling the pipeline. Its README describes ElevenLabs and FFmpeg dependencies; inspect the workflow before adopting it. |
| [5AM MCP / CLI](https://5am.app/cli/docs/mcp) | Agent tools for VEDL edit scripts, frame inspection, drafts, and exports. | Alternative orchestration layer. Draft/export availability and charges depend on CLI version and service terms. |
| [Agentcut](https://github.com/deifos/Agentcut) | Agent-assisted video studio using Remotion code with a visual editing interface. | Possible visual companion if working only through scripts becomes awkward. The name is shared by multiple projects; this link identifies the Remotion-based candidate. |
| Montaj | Conversational editing and a visual timeline. | The pasted conversation gives no exact URL. [montaj.ag](https://montaj.ag/) is a candidate matching the description; confirm identity before adopting it. |
| [Descript Underlord](https://feedback.descript.com/changelog/announcingunderlord-v2) | AI co-editor within Descript. | Packaged alternative for transcript-driven editing. Do not assume an external MCP interface from the thread alone. |
| [ChatCut](https://chatcut.io/features/ai-video-editor) | Conversational editing on an editable multitrack timeline. | Packaged alternative if a visual editor is useful. |
| [HyperFrames](https://hyperframes.app/docs/1-startup/1-introduction) | HTML/CSS/JavaScript rendered into video. | Alternative to Remotion for code-generated graphics; no need to start with both. |
| [Manim](https://www.manim.community/) | Programmatic explanatory animation. | Optional for diagrams or explanations; likely unnecessary for everyday trip vlogs. |
| [Pillow / PIL](https://pillow.readthedocs.io/) | Generate static image assets. | Useful for cards and labels; it is not a full video editor. |
| [MoviePy](https://zulko.github.io/moviepy/) | Higher-level Python video composition. | Optional convenience layer; direct FFmpeg may already cover the intended edits. |
| FFmpeg MCP servers / Premiere MCP servers | Expose editing commands to agents. | Categories mentioned without specific implementations. Verify a particular server's capabilities before relying on it. |
| [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) | Visual timeline, advanced grading, Fusion compositing, Fairlight audio, and multicam work. | Defer until one of these needs appears. Blackmagic's [21.1 announcement](https://www.blackmagicdesign.com/media/partial/release/20260908-03) confirms AI-assistant integration for project analysis, media organization, settings, and batch rendering; it does not establish unlimited autonomous timeline editing. Verify edition and integration requirements before setup. |

## Proposed first-video workflow

1. Pick one small story from a past trip or a future outing. Start with a 30–60 second vertical draft as a working target.
2. Inspect the source clips with ffprobe. Keep original media separate from generated files.
3. Transcribe the spoken audio with Scribe or a local alternative. Save timestamped text.
4. Create an explicit cut list: retain the main story, remove retakes and distracting pauses, and add relevant trip B-roll. Keep enough breathing room for natural speech.
5. Use FFmpeg for cuts, framing, basic color adjustments, audio cleanup, and short audio fades at edits.
6. Add captions and, where useful, a Remotion location label, title, or other overlay. Adjust transcript timestamps to the edited timeline before timing captions and graphics.
7. Render a draft, watch it with sound, and review pacing, caption accuracy, framing, sync, and audio quality. Revise, then export and inspect the finished file.

Local FFmpeg and Remotion rendering can keep media on the machine. The complete workflow is only local if transcription and other services are local too. Repository notes can record media locations, edit plans, and templates without committing large raw footage or exports.

## When to add Resolve

Revisit Resolve when advanced selective color correction, multicam editing, interactive timeline adjustments, complex compositing, or detailed audio finishing becomes a recurring need. The starting stack is a practical fit for the stated scope; the first few finished videos should reveal any specific gaps.

## Source context and verification

The source supplied by Andrew is a pasted conversation beginning with an October 31 post attributed to `@ashebytes`, followed by discussion of agent-assisted video editing. No original post URL or complete source list was included. Attribution of a particular setup to that creator remains unverified.

The preference for FFmpeg, Scribe or similar transcription, Remotion, and deferring Resolve comes from Andrew's statements in that conversation. Tool links above point to project or vendor sources, with the main stack and several named alternatives checked on November 1, 2026. The proposed short-video workflow is an adaptation for this repository, not a claim that it was demonstrated by the original post.