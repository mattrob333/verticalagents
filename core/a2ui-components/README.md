# A2UI Dashboard Shell

> NotebookLM-style interface for vertical AI agents

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DASHBOARD SHELL                                │
├────────────────┬─────────────────────────────┬──────────────────────────┤
│   SOURCES      │         CHAT                │      INSIGHTS            │
│   PANEL        │         INTERFACE           │      PANEL               │
├────────────────┼─────────────────────────────┼──────────────────────────┤
│ • Data feeds   │ • Message history           │ • Metrics cards          │
│ • Uploads      │ • Input area                │ • Artifact viewer        │
│ • Recent items │ • Suggested actions         │ • Audio briefing         │
│ • Search       │ • Tool status               │ • Export options         │
└────────────────┴─────────────────────────────┴──────────────────────────┘
```

## Component Structure

```
a2ui-components/
├── dashboard-shell/
│   ├── DashboardShell.jsx      # Main layout container
│   ├── SourcesPanel.jsx        # Left sidebar
│   ├── ChatInterface.jsx       # Center chat area
│   ├── InsightsPanel.jsx       # Right sidebar
│   └── styles.css
│
├── chat-interface/
│   ├── ChatContainer.jsx       # Message list + input
│   ├── Message.jsx             # Individual message
│   ├── MessageInput.jsx        # Text input + actions
│   ├── SuggestedActions.jsx    # Quick action buttons
│   ├── ToolStatus.jsx          # Show active tools
│   └── styles.css
│
├── artifact-viewer/
│   ├── ArtifactViewer.jsx      # Container for artifacts
│   ├── DocumentArtifact.jsx    # PDFs, docs
│   ├── TableArtifact.jsx       # Data tables
│   ├── ChartArtifact.jsx       # Visualizations
│   ├── CodeArtifact.jsx        # Code blocks
│   └── styles.css
│
├── onboarding-wizard/
│   ├── OnboardingWizard.jsx    # Multi-step form container
│   ├── WizardStep.jsx          # Individual step
│   ├── FormFields.jsx          # Reusable field components
│   ├── ProgressBar.jsx         # Step indicator
│   └── styles.css
│
├── audio-briefing/
│   ├── AudioBriefing.jsx       # Audio player for summaries
│   ├── TranscriptView.jsx      # Text alongside audio
│   ├── PlaybackControls.jsx    # Play/pause/speed
│   └── styles.css
│
└── metrics-panel/
    ├── MetricsPanel.jsx        # Container for metrics
    ├── MetricCard.jsx          # Individual metric
    ├── TrendIndicator.jsx      # Up/down arrows
    └── styles.css
```

## Core Components

### DashboardShell

The main layout container that orchestrates all panels:

```jsx
// dashboard-shell/DashboardShell.jsx

import React, { useState } from 'react';
import { SourcesPanel } from './SourcesPanel';
import { ChatInterface } from '../chat-interface/ChatInterface';
import { InsightsPanel } from './InsightsPanel';

export function DashboardShell({ 
  agent,           // Agent configuration
  sources,         // Data sources for left panel
  onMessage,       // Chat message handler
  artifacts,       // Generated artifacts
  metrics,         // KPI data
  children 
}) {
  const [selectedSource, setSelectedSource] = useState(null);
  const [activeArtifact, setActiveArtifact] = useState(null);

  return (
    <div className="dashboard-shell">
      {/* Left Panel: Sources & Context */}
      <aside className="sources-panel">
        <SourcesPanel 
          sources={sources}
          onSourceSelect={setSelectedSource}
          selectedSource={selectedSource}
        />
      </aside>

      {/* Center: Chat Interface */}
      <main className="chat-main">
        <ChatInterface
          agent={agent}
          onMessage={onMessage}
          context={{ selectedSource }}
          onArtifactGenerated={setActiveArtifact}
        />
      </main>

      {/* Right Panel: Insights & Artifacts */}
      <aside className="insights-panel">
        <InsightsPanel
          metrics={metrics}
          artifact={activeArtifact}
          artifacts={artifacts}
        />
      </aside>
    </div>
  );
}
```

### ChatInterface

The central chat component with message handling:

```jsx
// chat-interface/ChatInterface.jsx

import React, { useState, useRef, useEffect } from 'react';
import { Message } from './Message';
import { MessageInput } from './MessageInput';
import { SuggestedActions } from './SuggestedActions';
import { ToolStatus } from './ToolStatus';

export function ChatInterface({ 
  agent,
  onMessage,
  context,
  onArtifactGenerated
}) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTools, setActiveTools] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (content) => {
    // Add user message
    const userMessage = { role: 'user', content, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call agent
      const response = await onMessage(content, context);
      
      // Add assistant message
      const assistantMessage = { 
        role: 'assistant', 
        content: response.text,
        artifacts: response.artifacts,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Handle artifacts
      if (response.artifacts?.length > 0) {
        onArtifactGenerated(response.artifacts[0]);
      }
    } catch (error) {
      console.error('Message failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const suggestedActions = agent.suggestedActions || [
    { label: 'Show today\'s tasks', prompt: 'What tasks need attention today?' },
    { label: 'Generate report', prompt: 'Generate a summary report for this week' },
    { label: 'Check status', prompt: 'What\'s the current status?' },
  ];

  return (
    <div className="chat-interface">
      {/* Header with agent info */}
      <header className="chat-header">
        <div className="agent-identity">
          <span className="agent-emoji">{agent.emoji}</span>
          <h2>{agent.name}</h2>
        </div>
        <ToolStatus tools={activeTools} />
      </header>

      {/* Messages */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h3>Hi! I'm {agent.name}</h3>
            <p>{agent.greeting}</p>
            <SuggestedActions 
              actions={suggestedActions}
              onSelect={handleSend}
            />
          </div>
        ) : (
          messages.map((msg, idx) => (
            <Message 
              key={idx} 
              message={msg} 
              agentEmoji={agent.emoji}
            />
          ))
        )}
        {isLoading && (
          <div className="loading-indicator">
            <span className="agent-emoji">{agent.emoji}</span>
            <span className="typing-dots">...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <MessageInput 
        onSend={handleSend}
        disabled={isLoading}
        placeholder={`Message ${agent.name}...`}
      />
    </div>
  );
}
```

### OnboardingWizard

Multi-step form for agent setup:

```jsx
// onboarding-wizard/OnboardingWizard.jsx

import React, { useState } from 'react';
import { WizardStep } from './WizardStep';
import { ProgressBar } from './ProgressBar';

export function OnboardingWizard({ 
  steps,           // Array of step configs
  onComplete,      // Called when wizard finishes
  onStepChange,    // Called on each step
  initialData = {}
}) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState({});

  const step = steps[currentStep];
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;

  const validateStep = () => {
    const stepErrors = {};
    step.fields.forEach(field => {
      if (field.required && !formData[field.name]) {
        stepErrors[field.name] = `${field.label} is required`;
      }
      if (field.validate) {
        const error = field.validate(formData[field.name]);
        if (error) stepErrors[field.name] = error;
      }
    });
    setErrors(stepErrors);
    return Object.keys(stepErrors).length === 0;
  };

  const handleNext = () => {
    if (!validateStep()) return;
    
    if (isLastStep) {
      onComplete(formData);
    } else {
      setCurrentStep(prev => prev + 1);
      onStepChange?.(currentStep + 1, formData);
    }
  };

  const handleBack = () => {
    setCurrentStep(prev => prev - 1);
    onStepChange?.(currentStep - 1, formData);
  };

  const handleFieldChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  return (
    <div className="onboarding-wizard">
      <ProgressBar 
        steps={steps.map(s => s.title)}
        currentStep={currentStep}
      />

      <div className="wizard-content">
        <WizardStep
          step={step}
          data={formData}
          errors={errors}
          onChange={handleFieldChange}
        />
      </div>

      <div className="wizard-actions">
        {!isFirstStep && (
          <button 
            className="btn-secondary"
            onClick={handleBack}
          >
            Back
          </button>
        )}
        <button 
          className="btn-primary"
          onClick={handleNext}
        >
          {isLastStep ? 'Complete Setup' : 'Continue'}
        </button>
      </div>
    </div>
  );
}
```

### AudioBriefing

NotebookLM-style audio summaries:

```jsx
// audio-briefing/AudioBriefing.jsx

import React, { useState, useRef } from 'react';
import { PlaybackControls } from './PlaybackControls';
import { TranscriptView } from './TranscriptView';

export function AudioBriefing({ 
  audioUrl,        // URL to audio file
  transcript,      // Text transcript with timestamps
  title,
  duration
}) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  const handlePlayPause = () => {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    setCurrentTime(audioRef.current.currentTime);
  };

  const handleSeek = (time) => {
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  };

  const handleSpeedChange = (speed) => {
    audioRef.current.playbackRate = speed;
    setPlaybackSpeed(speed);
  };

  return (
    <div className="audio-briefing">
      <header className="briefing-header">
        <h3>🎧 {title}</h3>
        <span className="duration">{formatDuration(duration)}</span>
      </header>

      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
      />

      <PlaybackControls
        isPlaying={isPlaying}
        currentTime={currentTime}
        duration={duration}
        playbackSpeed={playbackSpeed}
        onPlayPause={handlePlayPause}
        onSeek={handleSeek}
        onSpeedChange={handleSpeedChange}
      />

      <TranscriptView
        transcript={transcript}
        currentTime={currentTime}
        onTimestampClick={handleSeek}
      />
    </div>
  );
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
```

## Styling

Base styles for the dashboard (Tailwind-compatible):

```css
/* styles/dashboard.css */

.dashboard-shell {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  height: 100vh;
  background: var(--bg-primary);
}

.sources-panel {
  border-right: 1px solid var(--border-color);
  padding: 1rem;
  overflow-y: auto;
}

.chat-main {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.insights-panel {
  border-left: 1px solid var(--border-color);
  padding: 1rem;
  overflow-y: auto;
}

/* Chat Interface */
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .dashboard-shell {
    grid-template-columns: 1fr;
  }
  
  .sources-panel,
  .insights-panel {
    display: none;
  }
}
```

## Usage Example

Putting it all together for a vertical:

```jsx
// verticals/veterinary-clinics/Dashboard.jsx

import { DashboardShell } from '@tier4/a2ui';
import { vetAssistAgent } from './agent';
import { useClinicData } from './hooks';

export function VetDashboard({ clinicId }) {
  const { reminders, patients, metrics } = useClinicData(clinicId);

  const sources = [
    { type: 'reminders', label: 'Upcoming Reminders', data: reminders },
    { type: 'patients', label: 'Recent Patients', data: patients },
  ];

  const handleMessage = async (content, context) => {
    return await vetAssistAgent.chat(content, {
      clinicId,
      ...context
    });
  };

  return (
    <DashboardShell
      agent={{
        name: 'VetAssist',
        emoji: '🐾',
        greeting: 'How can I help with your practice today?',
        suggestedActions: [
          { label: 'Today\'s reminders', prompt: 'Show me today\'s vaccine reminders' },
          { label: 'Weekly report', prompt: 'Generate this week\'s engagement report' },
          { label: 'Lapsed patients', prompt: 'Which patients need re-engagement?' },
        ]
      }}
      sources={sources}
      onMessage={handleMessage}
      metrics={metrics}
    />
  );
}
```

---

*A2UI Components — Tier 4 Intelligence*
