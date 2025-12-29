"""
Scaffold Phase - Build complete Next.js app from specification.

This phase:
1. Creates output directory at configured location
2. Scaffolds Next.js app from templates
3. Injects persona, tools, and configuration
4. Generates A2UI components (inline chat forms)
5. Creates Supabase migrations
6. Sets up API routes
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


@dataclass
class ScaffoldResult:
    """Result of the scaffold phase"""
    output_path: str
    files_created: List[str]
    dependencies: Dict[str, str]
    env_vars_needed: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_path": self.output_path,
            "files_created": self.files_created,
            "dependencies": self.dependencies,
            "env_vars_needed": self.env_vars_needed
        }


class ScaffoldPhase:
    """
    Scaffold Phase Handler

    Creates a complete Next.js application from the specification.
    Outputs to configurable external directory, keeping factory clean.
    """

    def __init__(self, config):
        self.config = config
        self.factory_root = Path(__file__).parent.parent.parent.parent

    async def execute(
        self,
        vertical_name: str,
        vertical_slug: str,
        specification: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Execute the scaffold phase.

        Args:
            vertical_name: Human-readable vertical name
            vertical_slug: URL-friendly slug
            specification: Output from specification phase
            output_path: Where to create the app

        Returns:
            Path to the created app
        """
        output_dir = Path(output_path)

        # Step 1: Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Step 2: Scaffold base app structure
        await self._scaffold_base_app(output_dir, vertical_name, vertical_slug)

        # Step 3: Inject agent configuration
        await self._inject_agent_config(
            output_dir,
            specification.get('persona', ''),
            specification.get('tools', [])
        )

        # Step 4: Generate A2UI components
        await self._generate_a2ui_components(output_dir)

        # Step 5: Generate pages (landing, admin, chat)
        await self._generate_pages(
            output_dir,
            vertical_name,
            vertical_slug,
            specification
        )

        # Step 6: Generate API routes
        await self._generate_api_routes(output_dir, specification)

        # Step 7: Generate Supabase migrations
        await self._generate_supabase_migrations(output_dir, vertical_slug)

        # Step 8: Generate package.json and configs
        await self._generate_configs(output_dir, vertical_name, vertical_slug)

        return str(output_dir)

    async def _scaffold_base_app(
        self,
        output_dir: Path,
        vertical_name: str,
        vertical_slug: str
    ) -> None:
        """Create base app directory structure"""

        # Create directory structure
        dirs = [
            "src/app",
            "src/app/admin",
            "src/app/chat",
            "src/app/onboard",
            "src/app/api/agent",
            "src/app/api/onboarding",
            "src/app/api/webhooks",
            "src/agent",
            "src/agent/tools",
            "src/components/a2ui",
            "src/components/admin",
            "src/components/chat",
            "src/components/landing",
            "src/components/onboarding",
            "src/lib",
            "src/lib/integrations",
            "marketing",
            "deploy",
            "deploy/supabase/migrations"
        ]

        for dir_path in dirs:
            (output_dir / dir_path).mkdir(parents=True, exist_ok=True)

        # Create .gitkeep files
        for dir_path in dirs:
            gitkeep = output_dir / dir_path / ".gitkeep"
            if not any((output_dir / dir_path).iterdir()):
                gitkeep.touch()

    async def _inject_agent_config(
        self,
        output_dir: Path,
        persona: str,
        tools: List[Dict[str, Any]]
    ) -> None:
        """Inject agent persona and tool definitions"""

        agent_dir = output_dir / "src" / "agent"

        # Save persona as system prompt
        (agent_dir / "system-prompt.md").write_text(persona)

        # Generate config.ts
        config_content = '''/**
 * Agent Configuration
 *
 * This file contains the configuration for the vertical agent.
 * Template variables are replaced during onboarding.
 */

export interface AgentConfig {
  name: string;
  model: string;
  companyName: string;
  // Add vertical-specific config here
}

export const agentConfig: AgentConfig = {
  name: "{{AGENT_NAME}}",
  model: "claude-sonnet-4-20250514",
  companyName: "{{COMPANY_NAME}}",
};

// Escalation triggers - when to hand off to human
export const escalationTriggers = [
  "User requests human assistance",
  "Sensitive legal/medical questions",
  "Complaint or frustration detected",
  "Complex situation requiring judgment",
];

// Response settings
export const responseSettings = {
  maxTokens: 1024,
  temperature: 0.7,
  autoSave: true,
  notifyOnComplete: true,
};
'''
        (agent_dir / "config.ts").write_text(config_content)

        # Generate tools index
        tools_content = '''/**
 * Agent Tools
 *
 * MCP-format tool definitions for the agent.
 */

import Anthropic from "@anthropic-ai/sdk";

export const tools: Anthropic.Tool[] = [
  {
    name: "save_intake_data",
    description: "Save collected intake data to the database",
    input_schema: {
      type: "object" as const,
      properties: {
        data: { type: "object", description: "Intake data to save" },
        stage: { type: "string", description: "Current stage of intake" },
      },
      required: ["data", "stage"],
    },
  },
  {
    name: "get_user_progress",
    description: "Get the user's current progress in the onboarding flow",
    input_schema: {
      type: "object" as const,
      properties: {
        user_id: { type: "string", description: "User identifier" },
      },
      required: ["user_id"],
    },
  },
  {
    name: "notify_human",
    description: "Notify a human team member for review or escalation",
    input_schema: {
      type: "object" as const,
      properties: {
        message: { type: "string", description: "Notification message" },
        priority: {
          type: "string",
          enum: ["low", "medium", "high", "urgent"],
        },
        context: { type: "object", description: "Relevant context data" },
      },
      required: ["message", "priority"],
    },
  },
  {
    name: "schedule_followup",
    description: "Schedule a follow-up action or reminder",
    input_schema: {
      type: "object" as const,
      properties: {
        action: { type: "string", description: "What action to take" },
        when: { type: "string", description: "When to take action" },
        user_id: { type: "string", description: "User to follow up with" },
      },
      required: ["action", "when"],
    },
  },
];

// Tool execution handlers
export async function executeTool(
  name: string,
  input: Record<string, unknown>
): Promise<string> {
  switch (name) {
    case "save_intake_data":
      return await saveIntakeData(input);
    case "get_user_progress":
      return await getUserProgress(input);
    case "notify_human":
      return await notifyHuman(input);
    case "schedule_followup":
      return await scheduleFollowup(input);
    default:
      return JSON.stringify({ error: `Unknown tool: ${name}` });
  }
}

async function saveIntakeData(input: Record<string, unknown>): Promise<string> {
  // TODO: Implement Supabase save
  console.log("Saving intake data:", input);
  return JSON.stringify({ success: true, id: "record_" + Date.now() });
}

async function getUserProgress(input: Record<string, unknown>): Promise<string> {
  // TODO: Implement Supabase query
  console.log("Getting progress for:", input.user_id);
  return JSON.stringify({ stage: "welcome", completed: [] });
}

async function notifyHuman(input: Record<string, unknown>): Promise<string> {
  // TODO: Implement notification (email, Slack, etc.)
  console.log("Notifying human:", input);
  return JSON.stringify({ notified: true });
}

async function scheduleFollowup(input: Record<string, unknown>): Promise<string> {
  // TODO: Implement scheduling
  console.log("Scheduling followup:", input);
  return JSON.stringify({ scheduled: true, when: input.when });
}
'''
        (agent_dir / "tools" / "index.ts").write_text(tools_content)

    async def _generate_a2ui_components(self, output_dir: Path) -> None:
        """Generate A2UI inline chat form components"""

        a2ui_dir = output_dir / "src" / "components" / "a2ui"

        # InlineChatForm.tsx
        inline_form = '''"use client";

import React, { useState, createContext, useContext } from "react";

interface FormContextType {
  data: Record<string, unknown>;
  setField: (name: string, value: unknown) => void;
}

const FormContext = createContext<FormContextType | null>(null);

export function useFormContext() {
  const ctx = useContext(FormContext);
  if (!ctx) throw new Error("useFormContext must be used within InlineChatForm");
  return ctx;
}

interface InlineChatFormProps {
  children: React.ReactNode;
  onSubmit: (data: Record<string, unknown>) => void;
  className?: string;
}

export function InlineChatForm({
  children,
  onSubmit,
  className = "",
}: InlineChatFormProps) {
  const [data, setData] = useState<Record<string, unknown>>({});

  const setField = (name: string, value: unknown) => {
    setData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(data);
  };

  return (
    <FormContext.Provider value={{ data, setField }}>
      <form
        onSubmit={handleSubmit}
        className={`my-4 p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-4 ${className}`}
      >
        {children}
        <button
          type="submit"
          className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Continue
        </button>
      </form>
    </FormContext.Provider>
  );
}
'''
        (a2ui_dir / "InlineChatForm.tsx").write_text(inline_form)

        # InlineSelect.tsx
        inline_select = '''"use client";

import { useFormContext } from "./InlineChatForm";

interface InlineSelectProps {
  name: string;
  label: string;
  options: string[];
  required?: boolean;
}

export function InlineSelect({
  name,
  label,
  options,
  required = false,
}: InlineSelectProps) {
  const { data, setField } = useFormContext();
  const value = data[name] as string | undefined;

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setField(name, option)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              value === option
                ? "bg-blue-600 text-white shadow-md"
                : "bg-white border border-gray-300 text-gray-700 hover:border-blue-400 hover:bg-blue-50"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
'''
        (a2ui_dir / "InlineSelect.tsx").write_text(inline_select)

        # InlineSlider.tsx
        inline_slider = '''"use client";

import { useFormContext } from "./InlineChatForm";

interface InlineSliderProps {
  name: string;
  label: string;
  min: number;
  max: number;
  step?: number;
  showValue?: boolean;
  labels?: { min: string; max: string };
}

export function InlineSlider({
  name,
  label,
  min,
  max,
  step = 1,
  showValue = true,
  labels,
}: InlineSliderProps) {
  const { data, setField } = useFormContext();
  const value = (data[name] as number) ?? Math.floor((min + max) / 2);

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        {showValue && (
          <span className="text-lg font-bold text-blue-600">{value}</span>
        )}
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => setField(name, parseInt(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
      />
      {labels && (
        <div className="flex justify-between text-xs text-gray-500">
          <span>{labels.min}</span>
          <span>{labels.max}</span>
        </div>
      )}
    </div>
  );
}
'''
        (a2ui_dir / "InlineSlider.tsx").write_text(inline_slider)

        # InlineButtons.tsx
        inline_buttons = '''"use client";

import { useFormContext } from "./InlineChatForm";

interface InlineButtonsProps {
  name: string;
  label: string;
  options: string[];
  multiSelect?: boolean;
  required?: boolean;
}

export function InlineButtons({
  name,
  label,
  options,
  multiSelect = false,
  required = false,
}: InlineButtonsProps) {
  const { data, setField } = useFormContext();
  const value = data[name];

  const isSelected = (option: string) => {
    if (multiSelect) {
      return Array.isArray(value) && value.includes(option);
    }
    return value === option;
  };

  const handleClick = (option: string) => {
    if (multiSelect) {
      const current = (value as string[]) || [];
      if (current.includes(option)) {
        setField(name, current.filter((v) => v !== option));
      } else {
        setField(name, [...current, option]);
      }
    } else {
      setField(name, option);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className="grid grid-cols-2 gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => handleClick(option)}
            className={`py-3 px-4 rounded-lg text-sm font-medium transition-all ${
              isSelected(option)
                ? "bg-blue-600 text-white shadow-md"
                : "bg-white border border-gray-300 text-gray-700 hover:border-blue-400 hover:bg-blue-50"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
'''
        (a2ui_dir / "InlineButtons.tsx").write_text(inline_buttons)

        # InlineTextarea.tsx
        inline_textarea = '''"use client";

import { useFormContext } from "./InlineChatForm";

interface InlineTextareaProps {
  name: string;
  label: string;
  placeholder?: string;
  rows?: number;
  required?: boolean;
}

export function InlineTextarea({
  name,
  label,
  placeholder = "",
  rows = 3,
  required = false,
}: InlineTextareaProps) {
  const { data, setField } = useFormContext();
  const value = (data[name] as string) || "";

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <textarea
        value={value}
        onChange={(e) => setField(name, e.target.value)}
        placeholder={placeholder}
        rows={rows}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
      />
    </div>
  );
}
'''
        (a2ui_dir / "InlineTextarea.tsx").write_text(inline_textarea)

        # InlineFileUpload.tsx
        inline_file = '''"use client";

import { useState } from "react";
import { useFormContext } from "./InlineChatForm";

interface InlineFileUploadProps {
  name: string;
  label: string;
  accept?: string[];
  multiple?: boolean;
  required?: boolean;
}

export function InlineFileUpload({
  name,
  label,
  accept = [".pdf", ".jpg", ".png", ".doc", ".docx"],
  multiple = false,
  required = false,
}: InlineFileUploadProps) {
  const { setField } = useFormContext();
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (newFiles: FileList | null) => {
    if (!newFiles) return;
    const fileArray = Array.from(newFiles);
    const updated = multiple ? [...files, ...fileArray] : fileArray;
    setFiles(updated);
    setField(name, updated);
  };

  const removeFile = (index: number) => {
    const updated = files.filter((_, i) => i !== index);
    setFiles(updated);
    setField(name, updated);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragging
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
      >
        <input
          type="file"
          accept={accept.join(",")}
          multiple={multiple}
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
          id={`file-${name}`}
        />
        <label
          htmlFor={`file-${name}`}
          className="cursor-pointer text-gray-600"
        >
          <div className="text-3xl mb-2">📎</div>
          <p className="text-sm">
            Drag files here or <span className="text-blue-600">browse</span>
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {accept.join(", ")}
          </p>
        </label>
      </div>
      {files.length > 0 && (
        <ul className="space-y-1">
          {files.map((file, i) => (
            <li
              key={i}
              className="flex items-center justify-between text-sm bg-gray-100 rounded px-3 py-2"
            >
              <span className="truncate">{file.name}</span>
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="text-red-500 hover:text-red-700 ml-2"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
'''
        (a2ui_dir / "InlineFileUpload.tsx").write_text(inline_file)

        # Create index.ts barrel export
        index_content = '''export { InlineChatForm, useFormContext } from "./InlineChatForm";
export { InlineSelect } from "./InlineSelect";
export { InlineSlider } from "./InlineSlider";
export { InlineButtons } from "./InlineButtons";
export { InlineTextarea } from "./InlineTextarea";
export { InlineFileUpload } from "./InlineFileUpload";
'''
        (a2ui_dir / "index.ts").write_text(index_content)

    async def _generate_pages(
        self,
        output_dir: Path,
        vertical_name: str,
        vertical_slug: str,
        specification: Dict[str, Any]
    ) -> None:
        """Generate app pages - to be implemented in delivery phase"""
        # Placeholder - actual pages generated in delivery phase
        pass

    async def _generate_api_routes(
        self,
        output_dir: Path,
        specification: Dict[str, Any]
    ) -> None:
        """Generate API routes - to be implemented in delivery phase"""
        # Placeholder - actual routes generated in delivery phase
        pass

    async def _generate_supabase_migrations(
        self,
        output_dir: Path,
        vertical_slug: str
    ) -> None:
        """Generate Supabase migrations"""

        migrations_dir = output_dir / "deploy" / "supabase" / "migrations"

        migration = f'''-- Initial schema for {vertical_slug} agent
-- Generated by Vertical Agent Factory

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (synced from Clerk)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  clerk_id TEXT UNIQUE NOT NULL,
  email TEXT,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Intake sessions
CREATE TABLE IF NOT EXISTS intake_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  status TEXT DEFAULT 'in_progress', -- in_progress, completed, abandoned
  current_stage TEXT DEFAULT 'welcome',
  data JSONB DEFAULT '{{}}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Messages (chat history)
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES intake_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- user, assistant
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{{}}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents (uploaded files)
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES intake_sessions(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_type TEXT,
  file_size INTEGER,
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications (human escalations)
CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES intake_sessions(id),
  message TEXT NOT NULL,
  priority TEXT DEFAULT 'medium', -- low, medium, high, urgent
  context JSONB DEFAULT '{{}}',
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scheduled follow-ups
CREATE TABLE IF NOT EXISTS followups (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES intake_sessions(id),
  action TEXT NOT NULL,
  scheduled_for TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge base entries (for admin to add)
CREATE TABLE IF NOT EXISTS knowledge_base (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  embedding vector(1536), -- For RAG
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_intake_sessions_user ON intake_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_intake_sessions_status ON intake_sessions(status);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(read_at) WHERE read_at IS NULL;

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE intake_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE followups ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
'''
        (migrations_dir / "001_initial.sql").write_text(migration)

    async def _generate_configs(
        self,
        output_dir: Path,
        vertical_name: str,
        vertical_slug: str
    ) -> None:
        """Generate package.json and other config files"""

        # package.json
        package_json = {
            "name": vertical_slug,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "@anthropic-ai/sdk": "^0.27.0",
                "@clerk/nextjs": "^5.0.0",
                "@supabase/supabase-js": "^2.45.0",
                "next": "14.2.0",
                "react": "^18.3.0",
                "react-dom": "^18.3.0"
            },
            "devDependencies": {
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "autoprefixer": "^10.4.0",
                "postcss": "^8",
                "tailwindcss": "^3.4.0",
                "typescript": "^5"
            }
        }
        (output_dir / "package.json").write_text(json.dumps(package_json, indent=2))

        # .env.example
        env_example = '''# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up

# Optional: Stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_...
'''
        (output_dir / ".env.example").write_text(env_example)

        # next.config.js
        next_config = '''/** @type {import("next").NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["images.clerk.dev"],
  },
};

module.exports = nextConfig;
'''
        (output_dir / "next.config.js").write_text(next_config)

        # tailwind.config.js
        tailwind_config = '''/** @type {import("tailwindcss").Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
'''
        (output_dir / "tailwind.config.js").write_text(tailwind_config)

        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2017",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./src/*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        (output_dir / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))

        # README.md
        readme = f'''# {vertical_name} Agent

AI-powered intake and onboarding agent built by Vertical Agent Factory.

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run development server
npm run dev
```

## Stack

- **Frontend**: Next.js 14 + Tailwind CSS
- **Agent**: Claude API via @anthropic-ai/sdk
- **Database**: Supabase (PostgreSQL + pgvector)
- **Auth**: Clerk
- **Payments**: Stripe (optional)

## Structure

```
src/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Landing page
│   ├── admin/             # Admin dashboard
│   ├── chat/              # Client chat interface
│   └── api/               # API routes
├── agent/                 # Agent configuration
│   ├── system-prompt.md   # Agent persona
│   ├── config.ts          # Agent settings
│   └── tools/             # Tool definitions
├── components/
│   ├── a2ui/              # Inline chat form components
│   ├── admin/             # Admin dashboard components
│   └── chat/              # Chat interface components
└── lib/                   # Utilities and integrations
```

## Deployment

Deploy to Vercel:

```bash
npx vercel
```

---

*Built with [Vertical Agent Factory](https://github.com/tier4intelligence/vertical-agent-factory)*
'''
        (output_dir / "README.md").write_text(readme)
