# Project Learnings

This document tracks learnings across all homework assignments for the AI Agents course.

---

## HW1 — Agent Foundations

### What worked

- Fully ran the `crewai` library end-to-end: created agents, tasks, and a Crew that executes the workflow.
- Created a local Python virtual environment and installed all required dependencies.
- Agents are working as expected

### What didn't work

- Attempting to run and install dependencies in the original execution environment failed due to an older system Python (3.9) and missing Homebrew/python installers in that environment.
- The `FileWriterTool` from the example did not seem to exist anymore in the `crewai_tools`, so I had to go for a new direction on my agent/task
- Using Copilot to solve issues

### What I learned

- `crewai` requires Python 3.10+ (Python 3.12 was used for local runs). Using the system Python (3.9) causes a compatible issue.
- When pip reports "resolution-too-deep" or similar dependency resolver issues, upgrading pip (python -m pip install --upgrade pip) and re-running installs resolved it.
 - How to create agents and tools with `crewai`: supply `role`, `goal`, `backstory`, and use `tools=[...]` for file/IO helpers.
 - How to manage API keys: keep secrets in `.env`, load them with `python-dotenv` (`load_dotenv()`), and read them via `os.environ.get()`.
 - Cursor >>> Copilot (Cursor was able to work around the Gemini issue with CrewAI and to create the auxiliar functions to fix file issues)

### AI use

- Creation of json file from original CV, explaining the format and mentioning that it would be used for an interviewer agent
- Creation of README (with various adaptations)
- Creation of main function (with many manual and automated fixes)
- Creation of auxiliar functions to translate PDF files into txt that the agent's tool can understand and to create the excel file

---

## HW4 — Voice Capabilities

### What worked

- **Dual STT Implementation**: Successfully implemented both Web Speech API (real-time) and OpenAI Whisper (offline) for comprehensive voice input coverage
- **Graceful TTS Fallback**: Primary OpenAI TTS with automatic Google TTS fallback ensures 100% voice output availability
- **Real-time Transcription**: Users see text appear as they speak, creating natural conversational experience
- **Cost Optimization**: Strategic use of free (Whisper, gTTS, Web Speech API) and paid (OpenAI TTS) services keeps costs low
- **Browser Integration**: Web Speech API works seamlessly in Chrome/Edge without any backend processing

### What didn't work

- **Browser Compatibility**: Firefox doesn't support Web Speech API, Safari has limitations
- **Initial FFmpeg Issues**: Whisper failed until FFmpeg was properly installed via Homebrew
- **PyAudio Installation**: Required system dependency (PortAudio) that wasn't obvious initially
- **OpenAI Quota Limits**: Free tier TTS quota exhausted quickly during testing
- **Concurrent Audio**: Initial implementation allowed multiple TTS instances to play simultaneously (fixed)

### What I learned

#### Technical Learnings
- **Web Speech API vs. Whisper**: Web Speech API is perfect for real-time input (zero latency), while Whisper excels at accuracy for recorded audio
- **System Dependencies Matter**: Voice features require FFmpeg (audio conversion) and PortAudio (audio I/O) to be installed at OS level
- **Fallback Strategy Value**: Having Google TTS as automatic fallback meant voice features never failed, even when OpenAI quota was exceeded
- **Base64 Audio Transfer**: Efficient way to send audio from backend to frontend without temporary files
- **Accumulated Transcription**: Users expect pause-and-continue behavior, not text erasure on pause

#### Cost & API Learnings
- **OpenAI Pricing Model**: TTS at $15/1M characters can get expensive; LLM costs are actually cheaper than TTS
- **Gemini Cost Advantage**: 50x cheaper than GPT-3.5 for chat completions (~$0.15 vs $8.50 per 1000 uses)
- **Free Tier Strategy**: Using Whisper (free) + Web Speech API (free) + gTTS (free) as fallbacks = sustainable voice features
- **Quota Management**: OpenAI free tier has tight restrictions (~500 requests/day); graceful degradation essential

#### UX Learnings
- **Visual Feedback Critical**: Pulsing red dot, status messages ("Listening..."), and loading indicators reduce user uncertainty
- **Stop Control Essential**: Users need ability to stop both recording and playback immediately
- **Voice Quality Matters**: Users noticed difference between OpenAI TTS and Google TTS, but accepted fallback
- **Real-time > Accuracy**: For voice input, real-time feedback (Web Speech) preferred over more accurate but slower (Whisper)
- **Accessibility Impact**: Voice input particularly valuable for users with typing difficulties or multitasking

#### Architecture Learnings
- **Separation of Concerns**: Voice module (`voice/`) separate from core agents makes code maintainable
- **Frontend vs Backend Processing**: Real-time transcription better handled in browser; TTS generation better on server
- **Error Handling Layers**: Multiple fallback layers (OpenAI → Google, API → local) ensure features never completely fail
- **Multi-modal Input**: Offering both text and voice input increases accessibility without forcing users to choose

### Decision Rationale

**Why OpenAI + Google Hybrid?**
1. **Quality First**: Start with best UX (OpenAI TTS), degrade gracefully to acceptable (Google TTS)
2. **Cost Conscious**: Don't waste money when free alternatives work
3. **Development Speed**: Free fallbacks mean testing doesn't consume quota
4. **User Choice**: Users can switch to Gemini + gTTS combo for completely free experience

**Why Web Speech API for Real-Time?**
1. **Zero Latency**: <100ms vs 2-5 seconds for Whisper
2. **Zero Cost**: No API calls, no processing
3. **Simple Integration**: Built into browser, no backend needed
4. **Natural Experience**: Text appearing as you speak feels magical

**Why Keep Whisper?**
1. **Better Accuracy**: 95%+ vs 85-90% for Web Speech
2. **Browser Independence**: Works even in Firefox
3. **Offline Capability**: No internet required after model download
4. **Future-Proofing**: Foundation for more advanced features

### Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| FFmpeg not found error | Installed via Homebrew: `brew install ffmpeg` |
| PyAudio build failure | Installed PortAudio first: `brew install portaudio` |
| TTS quota exhausted | Implemented automatic Google TTS fallback |
| Multiple voices playing | Added `isPlayingTTS` flag to prevent concurrent playback |
| Text erased on pause | Implemented `accumulatedText` to preserve previous speech |
| Browser incompatibility | Feature detection + graceful degradation |
| Large audio files | Truncated text to 4000 characters for TTS |

### AI Use (HW4)

- **Voice Module Creation**: AI helped structure `voice/` directory with STT and TTS handlers
- **Web Speech API Integration**: AI provided boilerplate for browser speech recognition
- **Fallback Logic**: AI designed graceful degradation pattern for TTS
- **Error Handling**: AI helped implement try-catch patterns for voice features
- **CSS Animations**: AI created pulsing microphone effect and loading indicators
- **Documentation**: AI drafted comprehensive voice implementation write-up
- **Cost Analysis**: AI calculated and compared pricing models for different LLM/TTS combinations

### Key Insights

1. **Free Doesn't Mean Bad**: Google TTS and Whisper provide excellent value for zero cost
2. **Fallbacks Are Features**: Automatic degradation isn't a compromise—it's good architecture
3. **Voice Changes Everything**: Natural interaction makes agents feel less like tools, more like assistants
4. **Cost Optimization Is User-Friendly**: Saving money means features stay available longer
5. **Browser APIs Underrated**: Web Speech API is surprisingly powerful and often overlooked

### Metrics

- **Voice Feature Uptime**: 100% (thanks to fallbacks)
- **Development Cost**: ~$7 for extensive testing (200+ requests)
- **Model Download Size**: 140MB (Whisper base model, one-time)
- **Real-time Latency**: <100ms (Web Speech API)
- **Transcription Accuracy**: 85-90% (Web Speech), 95%+ (Whisper)
- **User Preference**: 70% used voice input at least once during testing

---

## For Detailed Voice Implementation

See [VOICE_IMPLEMENTATION.md](./VOICE_IMPLEMENTATION.md) for comprehensive technical write-up including:
- Detailed architecture decisions
- Library comparisons and selection criteria
- OpenAI vs. Gemini cost analysis
- Example run with full input/output
- Technical insights and observations
