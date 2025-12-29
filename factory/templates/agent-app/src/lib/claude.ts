// Claude API Integration
import Anthropic from "@anthropic-ai/sdk";
import { agentConfig, toolDefinitions } from "@/agent/config";

const anthropic = new Anthropic({
  apiKey: process.env.CLAUDE_API_KEY!,
});

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ToolCall {
  id: string;
  name: string;
  input: Record<string, unknown>;
}

export interface AgentResponse {
  content: string;
  toolCalls?: ToolCall[];
  stopReason: "end_turn" | "tool_use" | "max_tokens";
}

// Convert our tool definitions to Anthropic format
const tools = toolDefinitions.map((tool: any) => ({
  name: tool.name,
  description: tool.description,
  input_schema: tool.input_schema,
}));

export async function chat(
  messages: ChatMessage[],
  clientContext?: Record<string, unknown>
): Promise<AgentResponse> {
  // Build system prompt with context
  let systemPrompt = agentConfig.systemPrompt;

  // Replace template variables with client context
  if (clientContext) {
    Object.entries(clientContext).forEach(([key, value]) => {
      systemPrompt = systemPrompt.replace(
        new RegExp(`\\{\\{${key}\\}\\}`, "g"),
        String(value)
      );
    });
  }

  // Convert messages to Anthropic format
  const anthropicMessages = messages.map((msg) => ({
    role: msg.role as "user" | "assistant",
    content: msg.content,
  }));

  try {
    const response = await anthropic.messages.create({
      model: agentConfig.model,
      max_tokens: 1024,
      system: systemPrompt,
      messages: anthropicMessages,
      tools: tools.length > 0 ? tools : undefined,
    });

    // Extract text content
    const textContent = response.content.find((c) => c.type === "text");
    const content = textContent?.type === "text" ? textContent.text : "";

    // Extract tool calls
    const toolUseBlocks = response.content.filter((c) => c.type === "tool_use");
    const toolCalls = toolUseBlocks.map((block) => {
      if (block.type === "tool_use") {
        return {
          id: block.id,
          name: block.name,
          input: block.input as Record<string, unknown>,
        };
      }
      return null;
    }).filter(Boolean) as ToolCall[];

    return {
      content,
      toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
      stopReason: response.stop_reason as AgentResponse["stopReason"],
    };
  } catch (error) {
    console.error("Claude API error:", error);
    throw error;
  }
}

// Execute a tool call
export async function executeTool(
  toolCall: ToolCall
): Promise<unknown> {
  // Import tool implementations dynamically
  const { executeToolCall } = await import("@/agent/tools");
  return executeToolCall(toolCall.name, toolCall.input);
}

// Continue conversation after tool execution
export async function continueWithToolResult(
  messages: ChatMessage[],
  toolCall: ToolCall,
  toolResult: unknown,
  clientContext?: Record<string, unknown>
): Promise<AgentResponse> {
  // Add tool result to messages
  const updatedMessages: any[] = [
    ...messages,
    {
      role: "assistant",
      content: [
        {
          type: "tool_use",
          id: toolCall.id,
          name: toolCall.name,
          input: toolCall.input,
        },
      ],
    },
    {
      role: "user",
      content: [
        {
          type: "tool_result",
          tool_use_id: toolCall.id,
          content: JSON.stringify(toolResult),
        },
      ],
    },
  ];

  return chat(updatedMessages as ChatMessage[], clientContext);
}

// Check for escalation triggers
export function shouldEscalate(message: string): boolean {
  const lowerMessage = message.toLowerCase();
  return agentConfig.escalationTriggers.some((trigger) =>
    lowerMessage.includes(trigger.toLowerCase())
  );
}

// Stream response (for real-time chat)
export async function* streamChat(
  messages: ChatMessage[],
  clientContext?: Record<string, unknown>
): AsyncGenerator<string> {
  let systemPrompt = agentConfig.systemPrompt;

  if (clientContext) {
    Object.entries(clientContext).forEach(([key, value]) => {
      systemPrompt = systemPrompt.replace(
        new RegExp(`\\{\\{${key}\\}\\}`, "g"),
        String(value)
      );
    });
  }

  const anthropicMessages = messages.map((msg) => ({
    role: msg.role as "user" | "assistant",
    content: msg.content,
  }));

  const stream = await anthropic.messages.stream({
    model: agentConfig.model,
    max_tokens: 1024,
    system: systemPrompt,
    messages: anthropicMessages,
  });

  for await (const event of stream) {
    if (
      event.type === "content_block_delta" &&
      event.delta.type === "text_delta"
    ) {
      yield event.delta.text;
    }
  }
}
