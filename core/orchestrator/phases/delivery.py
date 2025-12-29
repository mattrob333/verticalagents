"""
Delivery Phase - Generate admin dashboards and client landing pages.

This phase:
1. Generates NotebookLM-style 3-panel admin dashboard
2. Generates client-facing landing page with "Start Onboarding" CTA
3. Wires up complete flow: Landing → Onboarding → Chat → Dashboard
4. Creates marketing assets and deployment configuration
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DashboardPanel:
    """Configuration for a dashboard panel"""
    name: str
    title: str
    icon: str
    description: str
    components: List[str]


@dataclass
class LandingSection:
    """Configuration for a landing page section"""
    type: str  # hero, features, testimonials, cta, faq
    content: Dict[str, Any]


class DeliveryPhase:
    """
    Delivery Phase Handler

    Generates the final UI components and wires up the complete user flow.
    Creates admin dashboard, client landing page, and marketing assets.
    """

    def __init__(self, config):
        self.config = config
        self.factory_root = Path(__file__).parent.parent.parent.parent

    async def execute(
        self,
        output_dir: Path,
        vertical_name: str,
        vertical_slug: str,
        spec_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the delivery phase.

        Args:
            output_dir: Directory where the agent app was scaffolded
            vertical_name: Human-readable vertical name
            vertical_slug: URL-friendly slug
            spec_data: Specification data from the specification phase

        Returns:
            Delivery report with generated assets
        """
        # Step 1: Generate admin dashboard
        dashboard_files = self._generate_admin_dashboard(
            output_dir,
            vertical_name,
            spec_data
        )

        # Step 2: Generate client landing page
        landing_files = self._generate_landing_page(
            output_dir,
            vertical_name,
            vertical_slug,
            spec_data
        )

        # Step 3: Generate marketing assets
        marketing_files = self._generate_marketing_assets(
            output_dir,
            vertical_name,
            spec_data
        )

        # Step 4: Generate deployment configuration
        deployment_files = self._generate_deployment_config(
            output_dir,
            vertical_slug
        )

        # Step 5: Wire up complete flow
        self._wire_up_flow(output_dir, spec_data)

        return {
            "status": "success",
            "output_dir": str(output_dir),
            "dashboard_files": dashboard_files,
            "landing_files": landing_files,
            "marketing_files": marketing_files,
            "deployment_files": deployment_files,
            "next_steps": self._get_next_steps(output_dir, vertical_slug)
        }

    def _generate_admin_dashboard(
        self,
        output_dir: Path,
        vertical_name: str,
        spec_data: Dict[str, Any]
    ) -> List[str]:
        """Generate NotebookLM-style 3-panel admin dashboard"""
        files_created = []
        admin_dir = output_dir / "src" / "app" / "admin"
        components_dir = output_dir / "src" / "components" / "admin"

        admin_dir.mkdir(parents=True, exist_ok=True)
        components_dir.mkdir(parents=True, exist_ok=True)

        # Dashboard shell component
        dashboard_shell = f'''// Admin Dashboard Shell - NotebookLM-style 3-panel layout
"use client";

import {{ useState }} from "react";
import {{ KnowledgePanel }} from "@/components/admin/KnowledgePanel";
import {{ AgentChatPanel }} from "@/components/admin/AgentChatPanel";
import {{ TuningPanel }} from "@/components/admin/TuningPanel";

interface DashboardShellProps {{
  verticalName: string;
  agentId: string;
}}

export function DashboardShell({{ verticalName, agentId }}: DashboardShellProps) {{
  const [selectedKnowledge, setSelectedKnowledge] = useState<string | null>(null);
  const [tuningMode, setTuningMode] = useState<"examples" | "tone" | "settings">("examples");

  return (
    <div className="flex h-screen bg-gray-50">
      {{/* Left Panel - Knowledge Base */}}
      <div className="w-80 border-r border-gray-200 bg-white overflow-hidden flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">Knowledge Base</h2>
          <p className="text-sm text-gray-500">Train your agent with documents and FAQs</p>
        </div>
        <KnowledgePanel
          agentId={{agentId}}
          onSelect={{setSelectedKnowledge}}
          selectedId={{selectedKnowledge}}
        />
      </div>

      {{/* Center Panel - Agent Chat (Test Interface) */}}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-white">
          <h2 className="font-semibold text-gray-900">Test Your Agent</h2>
          <p className="text-sm text-gray-500">Preview how your agent responds to clients</p>
        </div>
        <AgentChatPanel
          agentId={{agentId}}
          verticalName={{verticalName}}
          debugMode={{true}}
        />
      </div>

      {{/* Right Panel - Tuning */}}
      <div className="w-80 border-l border-gray-200 bg-white overflow-hidden flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">Tuning</h2>
          <div className="flex gap-2 mt-2">
            <button
              onClick={{() => setTuningMode("examples")}}
              className={{`px-3 py-1 text-xs rounded-full ${{
                tuningMode === "examples"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-600"
              }}`}}
            >
              Examples
            </button>
            <button
              onClick={{() => setTuningMode("tone")}}
              className={{`px-3 py-1 text-xs rounded-full ${{
                tuningMode === "tone"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-600"
              }}`}}
            >
              Tone
            </button>
            <button
              onClick={{() => setTuningMode("settings")}}
              className={{`px-3 py-1 text-xs rounded-full ${{
                tuningMode === "settings"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-100 text-gray-600"
              }}`}}
            >
              Settings
            </button>
          </div>
        </div>
        <TuningPanel
          agentId={{agentId}}
          mode={{tuningMode}}
        />
      </div>
    </div>
  );
}}
'''

        shell_path = components_dir / "DashboardShell.tsx"
        shell_path.write_text(dashboard_shell)
        files_created.append(str(shell_path))

        # Knowledge Panel component
        knowledge_panel = '''// Knowledge Panel - Upload documents, manage FAQs, case types
"use client";

import { useState } from "react";
import { Upload, FileText, HelpCircle, FolderOpen, Plus, Trash2 } from "lucide-react";

interface KnowledgePanelProps {
  agentId: string;
  onSelect: (id: string | null) => void;
  selectedId: string | null;
}

interface KnowledgeItem {
  id: string;
  type: "document" | "faq" | "case_type";
  name: string;
  status: "processing" | "ready" | "error";
  updatedAt: string;
}

export function KnowledgePanel({ agentId, onSelect, selectedId }: KnowledgePanelProps) {
  const [items, setItems] = useState<KnowledgeItem[]>([
    { id: "1", type: "document", name: "Services Guide.pdf", status: "ready", updatedAt: "2 hours ago" },
    { id: "2", type: "faq", name: "Common Questions", status: "ready", updatedAt: "1 day ago" },
    { id: "3", type: "case_type", name: "Standard Inquiry", status: "ready", updatedAt: "3 days ago" },
  ]);
  const [activeTab, setActiveTab] = useState<"documents" | "faqs" | "cases">("documents");

  const filteredItems = items.filter(item => {
    if (activeTab === "documents") return item.type === "document";
    if (activeTab === "faqs") return item.type === "faq";
    return item.type === "case_type";
  });

  const getIcon = (type: KnowledgeItem["type"]) => {
    switch (type) {
      case "document": return <FileText className="w-4 h-4" />;
      case "faq": return <HelpCircle className="w-4 h-4" />;
      case "case_type": return <FolderOpen className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {[
          { key: "documents", label: "Docs", icon: FileText },
          { key: "faqs", label: "FAQs", icon: HelpCircle },
          { key: "cases", label: "Cases", icon: FolderOpen },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as typeof activeTab)}
            className={`flex-1 py-2 px-3 text-xs font-medium flex items-center justify-center gap-1 ${
              activeTab === key
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <Icon className="w-3 h-3" />
            {label}
          </button>
        ))}
      </div>

      {/* Upload area */}
      <div className="p-3">
        <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors">
          <Upload className="w-6 h-6 text-gray-400" />
          <span className="text-xs text-gray-500 mt-1">
            {activeTab === "documents" ? "Upload document" : "Add new"}
          </span>
          <input type="file" className="hidden" />
        </label>
      </div>

      {/* Items list */}
      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-2">
        {filteredItems.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={`p-3 rounded-lg cursor-pointer transition-colors ${
              selectedId === item.id
                ? "bg-blue-50 border border-blue-200"
                : "bg-gray-50 hover:bg-gray-100 border border-transparent"
            }`}
          >
            <div className="flex items-start gap-2">
              <div className="text-gray-500 mt-0.5">
                {getIcon(item.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {item.name}
                </p>
                <p className="text-xs text-gray-500">{item.updatedAt}</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setItems(items.filter(i => i.id !== item.id));
                }}
                className="text-gray-400 hover:text-red-500"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
'''

        knowledge_path = components_dir / "KnowledgePanel.tsx"
        knowledge_path.write_text(knowledge_panel)
        files_created.append(str(knowledge_path))

        # Agent Chat Panel component
        agent_chat_panel = '''// Agent Chat Panel - Test interface with debug mode
"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bug, Eye, EyeOff } from "lucide-react";

interface AgentChatPanelProps {
  agentId: string;
  verticalName: string;
  debugMode?: boolean;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalls?: { name: string; input: Record<string, unknown>; output: unknown }[];
  timestamp: Date;
}

export function AgentChatPanel({ agentId, verticalName, debugMode = false }: AgentChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(debugMode);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate agent response (replace with actual API call)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `I'm your ${verticalName} assistant. I received your message: "${input}". How can I help you further?`,
        toolCalls: showDebug ? [
          {
            name: "searchKnowledge",
            input: { query: input },
            output: { results: [], confidence: 0.85 },
          },
        ] : undefined,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Debug toggle */}
      <div className="px-4 py-2 bg-white border-b border-gray-200 flex items-center justify-end gap-2">
        <button
          onClick={() => setShowDebug(!showDebug)}
          className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${
            showDebug ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-600"
          }`}
        >
          <Bug className="w-3 h-3" />
          Debug {showDebug ? "ON" : "OFF"}
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p className="text-sm">Start a conversation to test your agent</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white border border-gray-200"
              }`}
            >
              <p className="text-sm">{message.content}</p>

              {/* Debug: Tool calls */}
              {showDebug && message.toolCalls && message.toolCalls.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-purple-600 font-medium">Tool Calls:</p>
                  {message.toolCalls.map((tool, idx) => (
                    <div key={idx} className="mt-1 text-xs bg-purple-50 rounded p-2">
                      <p className="font-mono text-purple-700">{tool.name}</p>
                      <pre className="text-gray-600 mt-1 overflow-x-auto">
                        {JSON.stringify(tool.input, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              )}

              <p className="text-xs opacity-60 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message to test your agent..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
'''

        chat_path = components_dir / "AgentChatPanel.tsx"
        chat_path.write_text(agent_chat_panel)
        files_created.append(str(chat_path))

        # Tuning Panel component
        tuning_panel = '''// Tuning Panel - Response examples, tone adjustment, settings
"use client";

import { useState } from "react";
import { Plus, Save, Trash2, Sliders } from "lucide-react";

interface TuningPanelProps {
  agentId: string;
  mode: "examples" | "tone" | "settings";
}

interface ResponseExample {
  id: string;
  userInput: string;
  idealResponse: string;
}

export function TuningPanel({ agentId, mode }: TuningPanelProps) {
  const [examples, setExamples] = useState<ResponseExample[]>([
    {
      id: "1",
      userInput: "What are your hours?",
      idealResponse: "We're open Monday through Friday, 9 AM to 5 PM. Would you like to schedule an appointment?",
    },
  ]);

  const [tone, setTone] = useState({
    formality: 50, // 0 = casual, 100 = formal
    empathy: 75,
    directness: 60,
  });

  const [settings, setSettings] = useState({
    responseLength: "medium",
    language: "en",
    includeEmojis: false,
  });

  if (mode === "examples") {
    return (
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <button className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-400 hover:text-blue-600 flex items-center justify-center gap-2">
          <Plus className="w-4 h-4" />
          Add Example
        </button>

        {examples.map((example) => (
          <div key={example.id} className="bg-gray-50 rounded-lg p-3 space-y-2">
            <div>
              <label className="text-xs text-gray-500 font-medium">User says:</label>
              <textarea
                value={example.userInput}
                onChange={(e) => {
                  setExamples(examples.map(ex =>
                    ex.id === example.id ? { ...ex, userInput: e.target.value } : ex
                  ));
                }}
                className="w-full mt-1 p-2 text-sm border border-gray-200 rounded resize-none"
                rows={2}
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 font-medium">Ideal response:</label>
              <textarea
                value={example.idealResponse}
                onChange={(e) => {
                  setExamples(examples.map(ex =>
                    ex.id === example.id ? { ...ex, idealResponse: e.target.value } : ex
                  ));
                }}
                className="w-full mt-1 p-2 text-sm border border-gray-200 rounded resize-none"
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setExamples(examples.filter(ex => ex.id !== example.id))}
                className="text-xs text-red-600 hover:text-red-700"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}

        <button className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 text-sm">
          <Save className="w-4 h-4" />
          Save Examples
        </button>
      </div>
    );
  }

  if (mode === "tone") {
    return (
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {[
          { key: "formality", label: "Formality", low: "Casual", high: "Formal" },
          { key: "empathy", label: "Empathy", low: "Direct", high: "Warm" },
          { key: "directness", label: "Directness", low: "Gentle", high: "Direct" },
        ].map(({ key, label, low, high }) => (
          <div key={key}>
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>{low}</span>
              <span className="font-medium text-gray-900">{label}</span>
              <span>{high}</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={tone[key as keyof typeof tone]}
              onChange={(e) => setTone({ ...tone, [key]: parseInt(e.target.value) })}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>
        ))}

        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Preview</h4>
          <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600">
            Based on your settings, your agent will respond in a
            {tone.formality > 60 ? " professional" : " friendly"} tone
            {tone.empathy > 60 ? " with warmth and understanding" : ""}
            {tone.directness > 60 ? ", getting straight to the point" : ""}.
          </div>
        </div>

        <button className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 text-sm">
          <Save className="w-4 h-4" />
          Save Tone Settings
        </button>
      </div>
    );
  }

  // Settings mode
  return (
    <div className="flex-1 overflow-y-auto p-3 space-y-4">
      <div>
        <label className="text-xs text-gray-600 font-medium">Response Length</label>
        <select
          value={settings.responseLength}
          onChange={(e) => setSettings({ ...settings, responseLength: e.target.value })}
          className="w-full mt-1 p-2 text-sm border border-gray-200 rounded"
        >
          <option value="short">Short & Concise</option>
          <option value="medium">Medium</option>
          <option value="detailed">Detailed</option>
        </select>
      </div>

      <div>
        <label className="text-xs text-gray-600 font-medium">Language</label>
        <select
          value={settings.language}
          onChange={(e) => setSettings({ ...settings, language: e.target.value })}
          className="w-full mt-1 p-2 text-sm border border-gray-200 rounded"
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
        </select>
      </div>

      <div className="flex items-center justify-between">
        <label className="text-xs text-gray-600 font-medium">Include Emojis</label>
        <button
          onClick={() => setSettings({ ...settings, includeEmojis: !settings.includeEmojis })}
          className={`relative w-10 h-6 rounded-full transition-colors ${
            settings.includeEmojis ? "bg-blue-600" : "bg-gray-300"
          }`}
        >
          <span
            className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
              settings.includeEmojis ? "left-5" : "left-1"
            }`}
          />
        </button>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-2">
          <Sliders className="w-4 h-4" />
          Advanced Settings
        </h4>
        <p className="text-xs text-gray-500">
          Configure API keys, webhooks, and integrations in the Settings page.
        </p>
      </div>

      <button className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 text-sm">
        <Save className="w-4 h-4" />
        Save Settings
      </button>
    </div>
  );
}
'''

        tuning_path = components_dir / "TuningPanel.tsx"
        tuning_path.write_text(tuning_panel)
        files_created.append(str(tuning_path))

        # Admin page
        admin_page = f'''// Admin Dashboard Page
import {{ DashboardShell }} from "@/components/admin/DashboardShell";

export default function AdminPage() {{
  return (
    <DashboardShell
      verticalName="{vertical_name}"
      agentId="agent_default"
    />
  );
}}

export const metadata = {{
  title: "{vertical_name} - Admin Dashboard",
  description: "Manage your AI agent, knowledge base, and settings",
}};
'''

        page_path = admin_dir / "page.tsx"
        page_path.write_text(admin_page)
        files_created.append(str(page_path))

        # Admin layout
        admin_layout = '''// Admin Layout with auth protection
import { redirect } from "next/navigation";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // TODO: Add auth check
  // const session = await auth();
  // if (!session) redirect("/login");

  return (
    <div className="min-h-screen">
      {children}
    </div>
  );
}
'''

        layout_path = admin_dir / "layout.tsx"
        layout_path.write_text(admin_layout)
        files_created.append(str(layout_path))

        # Components index export
        components_index = '''// Admin components exports
export { DashboardShell } from "./DashboardShell";
export { KnowledgePanel } from "./KnowledgePanel";
export { AgentChatPanel } from "./AgentChatPanel";
export { TuningPanel } from "./TuningPanel";
'''

        index_path = components_dir / "index.ts"
        index_path.write_text(components_index)
        files_created.append(str(index_path))

        return files_created

    def _generate_landing_page(
        self,
        output_dir: Path,
        vertical_name: str,
        vertical_slug: str,
        spec_data: Dict[str, Any]
    ) -> List[str]:
        """Generate client-facing landing page with Start Onboarding CTA"""
        files_created = []
        landing_dir = output_dir / "src" / "app"
        components_dir = output_dir / "src" / "components" / "landing"

        components_dir.mkdir(parents=True, exist_ok=True)

        # Hero section component
        hero_section = f'''// Hero Section with CTA
"use client";

import Link from "next/link";
import {{ ArrowRight, CheckCircle }} from "lucide-react";

interface HeroSectionProps {{
  title: string;
  subtitle: string;
  benefits: string[];
}}

export function HeroSection({{ title, subtitle, benefits }}: HeroSectionProps) {{
  return (
    <section className="relative min-h-[80vh] flex items-center bg-gradient-to-br from-blue-50 to-white">
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {{/* Left: Content */}}
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
              {{title}}
            </h1>
            <p className="mt-6 text-xl text-gray-600">
              {{subtitle}}
            </p>

            <ul className="mt-8 space-y-3">
              {{benefits.map((benefit, idx) => (
                <li key={{idx}} className="flex items-center gap-3 text-gray-700">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                  {{benefit}}
                </li>
              ))}}
            </ul>

            <div className="mt-10 flex flex-col sm:flex-row gap-4">
              <Link
                href="/chat"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start Onboarding
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="#how-it-works"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-gray-700 font-semibold rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                Learn More
              </Link>
            </div>
          </div>

          {{/* Right: Visual */}}
          <div className="hidden md:block">
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xl">AI</span>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">AI Assistant</p>
                    <p className="text-sm text-gray-500">Online</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="bg-gray-100 rounded-lg px-4 py-3 text-sm text-gray-700">
                    Hi! I'm here to help you get started. What brings you here today?
                  </div>
                  <div className="flex justify-end">
                    <div className="bg-blue-600 text-white rounded-lg px-4 py-3 text-sm">
                      I need help with...
                    </div>
                  </div>
                </div>
              </div>
              {{/* Decorative elements */}}
              <div className="absolute -z-10 top-4 right-4 w-full h-full bg-blue-100 rounded-2xl" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}}
'''

        hero_path = components_dir / "HeroSection.tsx"
        hero_path.write_text(hero_section)
        files_created.append(str(hero_path))

        # Features section
        features_section = '''// Features Section
import { Clock, Shield, Zap, Users } from "lucide-react";

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}

interface FeaturesSectionProps {
  features: Feature[];
}

export function FeaturesSection({ features }: FeaturesSectionProps) {
  const defaultFeatures: Feature[] = [
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Save Time",
      description: "Automate repetitive tasks and focus on what matters most.",
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Secure & Private",
      description: "Your data is encrypted and never shared with third parties.",
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Instant Responses",
      description: "Get answers 24/7, no waiting for business hours.",
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Personalized Service",
      description: "AI that learns your preferences and adapts to your needs.",
    },
  ];

  const displayFeatures = features.length > 0 ? features : defaultFeatures;

  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900">
            Why Choose Us
          </h2>
          <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
            Experience the future of customer service with AI-powered assistance.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {displayFeatures.map((feature, idx) => (
            <div
              key={idx}
              className="p-6 bg-gray-50 rounded-xl hover:shadow-lg transition-shadow"
            >
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mb-4">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
'''

        features_path = components_dir / "FeaturesSection.tsx"
        features_path.write_text(features_section)
        files_created.append(str(features_path))

        # How it works section
        how_it_works = '''// How It Works Section
import { MessageCircle, FileText, CheckCircle } from "lucide-react";

export function HowItWorksSection() {
  const steps = [
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "Start a Conversation",
      description: "Click 'Start Onboarding' and chat with our AI assistant to tell us about your needs.",
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Provide Details",
      description: "Answer a few quick questions through our intuitive chat interface.",
    },
    {
      icon: <CheckCircle className="w-8 h-8" />,
      title: "Get Results",
      description: "Receive personalized recommendations and next steps instantly.",
    },
  ];

  return (
    <section id="how-it-works" className="py-20 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
            Getting started is easy. Just follow these simple steps.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, idx) => (
            <div key={idx} className="relative">
              {/* Connector line */}
              {idx < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 left-1/2 w-full h-0.5 bg-blue-200" />
              )}

              <div className="relative bg-white rounded-xl p-6 shadow-sm text-center">
                <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  {step.icon}
                </div>
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {idx + 1}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-600">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
'''

        hiw_path = components_dir / "HowItWorksSection.tsx"
        hiw_path.write_text(how_it_works)
        files_created.append(str(hiw_path))

        # CTA section
        cta_section = '''// Call to Action Section
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function CTASection() {
  return (
    <section className="py-20 bg-blue-600">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-3xl font-bold text-white">
          Ready to Get Started?
        </h2>
        <p className="mt-4 text-xl text-blue-100">
          Join thousands of satisfied customers who have transformed their experience.
        </p>

        <div className="mt-10">
          <Link
            href="/chat"
            className="inline-flex items-center justify-center gap-2 px-10 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition-colors text-lg"
          >
            Start Onboarding Now
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        <p className="mt-6 text-sm text-blue-200">
          No credit card required. Get started in under 2 minutes.
        </p>
      </div>
    </section>
  );
}
'''

        cta_path = components_dir / "CTASection.tsx"
        cta_path.write_text(cta_section)
        files_created.append(str(cta_path))

        # Footer component
        footer = '''// Footer Component
import Link from "next/link";

export function Footer() {
  return (
    <footer className="py-12 bg-gray-900 text-gray-400">
      <div className="max-w-6xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-white font-semibold mb-4">Company</h3>
            <ul className="space-y-2">
              <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
              <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li><Link href="/help" className="hover:text-white transition-colors">Help Center</Link></li>
              <li><Link href="/faq" className="hover:text-white transition-colors">FAQ</Link></li>
              <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
              <li><Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Contact</h3>
            <ul className="space-y-2">
              <li>support@example.com</li>
              <li>1-800-EXAMPLE</li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-800 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
'''

        footer_path = components_dir / "Footer.tsx"
        footer_path.write_text(footer)
        files_created.append(str(footer_path))

        # Landing page index
        landing_index = '''// Landing page components exports
export { HeroSection } from "./HeroSection";
export { FeaturesSection } from "./FeaturesSection";
export { HowItWorksSection } from "./HowItWorksSection";
export { CTASection } from "./CTASection";
export { Footer } from "./Footer";
'''

        index_path = components_dir / "index.ts"
        index_path.write_text(landing_index)
        files_created.append(str(index_path))

        # Main landing page
        landing_page = f'''// Landing Page
import {{ HeroSection }} from "@/components/landing/HeroSection";
import {{ FeaturesSection }} from "@/components/landing/FeaturesSection";
import {{ HowItWorksSection }} from "@/components/landing/HowItWorksSection";
import {{ CTASection }} from "@/components/landing/CTASection";
import {{ Footer }} from "@/components/landing/Footer";

export default function LandingPage() {{
  return (
    <main>
      <HeroSection
        title="Your AI-Powered {vertical_name} Assistant"
        subtitle="Get instant, personalized help 24/7. Our AI assistant guides you through every step of the process."
        benefits={{[
          "Instant responses, no waiting",
          "Personalized recommendations",
          "Available 24/7",
          "Secure and confidential",
        ]}}
      />
      <FeaturesSection features={{[]}} />
      <HowItWorksSection />
      <CTASection />
      <Footer />
    </main>
  );
}}

export const metadata = {{
  title: "{vertical_name} - AI Assistant",
  description: "Get instant, personalized help with our AI-powered assistant.",
}};
'''

        page_path = landing_dir / "page.tsx"
        page_path.write_text(landing_page)
        files_created.append(str(page_path))

        return files_created

    def _generate_marketing_assets(
        self,
        output_dir: Path,
        vertical_name: str,
        spec_data: Dict[str, Any]
    ) -> List[str]:
        """Generate marketing assets"""
        files_created = []
        public_dir = output_dir / "public"

        public_dir.mkdir(parents=True, exist_ok=True)

        # robots.txt
        robots = '''User-agent: *
Allow: /

Sitemap: /sitemap.xml
'''

        robots_path = public_dir / "robots.txt"
        robots_path.write_text(robots)
        files_created.append(str(robots_path))

        # Basic SVG logo placeholder
        logo_svg = '''<svg width="200" height="50" viewBox="0 0 200 50" xmlns="http://www.w3.org/2000/svg">
  <rect width="50" height="50" rx="10" fill="#2563eb"/>
  <text x="30" y="35" font-family="Arial, sans-serif" font-size="24" fill="white" text-anchor="middle">AI</text>
  <text x="130" y="32" font-family="Arial, sans-serif" font-size="18" fill="#1f2937" text-anchor="middle">Agent</text>
</svg>
'''

        logo_path = public_dir / "logo.svg"
        logo_path.write_text(logo_svg)
        files_created.append(str(logo_path))

        return files_created

    def _generate_deployment_config(
        self,
        output_dir: Path,
        vertical_slug: str
    ) -> List[str]:
        """Generate deployment configuration files"""
        files_created = []

        # Vercel config
        vercel_config = f'''{{
  "name": "{vertical_slug}-agent",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {{
    "NEXT_PUBLIC_APP_URL": "@app_url"
  }}
}}
'''

        vercel_path = output_dir / "vercel.json"
        vercel_path.write_text(vercel_config)
        files_created.append(str(vercel_path))

        # Docker config
        dockerfile = '''FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
'''

        docker_path = output_dir / "Dockerfile"
        docker_path.write_text(dockerfile)
        files_created.append(str(docker_path))

        # Docker compose for local development
        docker_compose = f'''version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/{vertical_slug}
      - CLAUDE_API_KEY=${{CLAUDE_API_KEY}}
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={vertical_slug}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
'''

        compose_path = output_dir / "docker-compose.yml"
        compose_path.write_text(docker_compose)
        files_created.append(str(compose_path))

        # GitHub Actions CI/CD
        github_dir = output_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)

        ci_workflow = '''name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Build
        run: npm run build

      - name: Test
        run: npm test --if-present

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
'''

        ci_path = github_dir / "ci.yml"
        ci_path.write_text(ci_workflow)
        files_created.append(str(ci_path))

        return files_created

    def _wire_up_flow(
        self,
        output_dir: Path,
        spec_data: Dict[str, Any]
    ) -> None:
        """Wire up the complete user flow: Landing → Onboarding → Chat → Dashboard"""
        # Create navigation config
        nav_config = '''// Navigation configuration
export const navConfig = {
  public: [
    { href: "/", label: "Home" },
    { href: "/#features", label: "Features" },
    { href: "/#how-it-works", label: "How It Works" },
    { href: "/chat", label: "Start Onboarding", cta: true },
  ],
  authenticated: [
    { href: "/chat", label: "Chat" },
    { href: "/admin", label: "Dashboard" },
    { href: "/settings", label: "Settings" },
  ],
  admin: [
    { href: "/admin", label: "Dashboard" },
    { href: "/admin/knowledge", label: "Knowledge Base" },
    { href: "/admin/settings", label: "Settings" },
    { href: "/admin/analytics", label: "Analytics" },
  ],
};
'''

        config_dir = output_dir / "src" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        nav_path = config_dir / "navigation.ts"
        nav_path.write_text(nav_config)

        # Create middleware for auth routing
        middleware = '''// Middleware for auth and routing
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Admin routes require authentication
  if (pathname.startsWith("/admin")) {
    // TODO: Add auth check
    // const session = await auth();
    // if (!session) {
    //   return NextResponse.redirect(new URL("/login", request.url));
    // }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/api/:path*"],
};
'''

        middleware_path = output_dir / "middleware.ts"
        middleware_path.write_text(middleware)

    def _get_next_steps(
        self,
        output_dir: Path,
        vertical_slug: str
    ) -> List[str]:
        """Generate next steps for deployment"""
        return [
            f"1. Navigate to output directory: cd {output_dir}",
            "2. Install dependencies: npm install",
            "3. Copy .env.example to .env.local and fill in values",
            "4. Run database migrations: npx supabase db push",
            "5. Start development server: npm run dev",
            "6. Test the landing page at http://localhost:3000",
            "7. Test the chat at http://localhost:3000/chat",
            "8. Test admin dashboard at http://localhost:3000/admin",
            "9. Deploy to Vercel: vercel --prod",
        ]


# Delivery phase prompts
DELIVERY_PROMPTS = {
    "customize_landing": """
Customize the landing page for {vertical}:
- What headline resonates with {vertical} customers?
- What are the 3-4 key benefits to highlight?
- What social proof should be included?
- What is the primary CTA text?
""",

    "customize_dashboard": """
Customize the admin dashboard for {vertical}:
- What knowledge categories make sense? (e.g., Services, FAQs, Case Types)
- What tuning options are most important?
- What analytics should be shown?
- What integrations need quick access?
"""
}
