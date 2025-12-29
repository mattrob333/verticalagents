# A2UI Onboarding Flow Template

This template defines the standard onboarding pattern for all vertical agents.

## Flow Structure

Each onboarding flow consists of 5 phases:

1. **Welcome** — Introduce the agent, set expectations
2. **Connect** — Integrate with existing tools
3. **Configure** — Collect business-specific settings
4. **Upload** — Gather necessary files/data
5. **Activate** — Confirm and go live

---

## Schema Definition

```typescript
// types/onboarding.ts

export interface OnboardingFlow {
  id: string;
  vertical: string;
  steps: OnboardingStep[];
  completionWebhook?: string;
}

export interface OnboardingStep {
  id: string;
  type: 'welcome' | 'connect' | 'configure' | 'upload' | 'activate';
  title: string;
  description: string;
  fields?: FormField[];
  integrations?: IntegrationConfig[];
  validations?: Validation[];
}

export interface FormField {
  id: string;
  type: 'text' | 'email' | 'phone' | 'select' | 'multiselect' | 'number' | 'textarea' | 'toggle' | 'slider' | 'date' | 'time' | 'file';
  label: string;
  placeholder?: string;
  required: boolean;
  options?: SelectOption[];  // For select/multiselect
  min?: number;             // For number/slider
  max?: number;
  accept?: string[];        // For file (e.g., ['.pdf', '.docx'])
  helpText?: string;
  dependsOn?: {
    field: string;
    value: any;
  };
}

export interface IntegrationConfig {
  id: string;
  name: string;
  icon: string;
  authType: 'oauth2' | 'apikey' | 'webhook';
  authUrl?: string;
  scopes?: string[];
  required: boolean;
  helpText?: string;
}

export interface Validation {
  field: string;
  rule: 'required' | 'email' | 'phone' | 'url' | 'min' | 'max' | 'pattern' | 'custom';
  value?: any;
  message: string;
}
```

---

## Example: Construction RFQ Agent Onboarding

```json
{
  "id": "construction-rfq-onboarding",
  "vertical": "construction",
  "steps": [
    {
      "id": "welcome",
      "type": "welcome",
      "title": "Let's Set Up Your RFQ Agent",
      "description": "In the next 10 minutes, we'll configure your AI assistant to handle bid requests and supplier comparisons. You'll start processing RFQs 10x faster."
    },
    {
      "id": "connect-tools",
      "type": "connect",
      "title": "Connect Your Tools",
      "description": "We'll pull project data and send completed quotes through your existing systems.",
      "integrations": [
        {
          "id": "procore",
          "name": "Procore",
          "icon": "/icons/procore.svg",
          "authType": "oauth2",
          "authUrl": "https://login.procore.com/oauth/authorize",
          "scopes": ["projects:read", "rfqs:read", "rfqs:write"],
          "required": false,
          "helpText": "Sync project data and push completed RFQ responses"
        },
        {
          "id": "email",
          "name": "Email (Gmail/Outlook)",
          "icon": "/icons/email.svg",
          "authType": "oauth2",
          "required": true,
          "helpText": "Receive RFQ requests and send completed quotes"
        },
        {
          "id": "quickbooks",
          "name": "QuickBooks",
          "icon": "/icons/quickbooks.svg",
          "authType": "oauth2",
          "required": false,
          "helpText": "Pull supplier pricing and create invoices"
        }
      ]
    },
    {
      "id": "company-info",
      "type": "configure",
      "title": "Tell Us About Your Business",
      "description": "This helps the agent understand your pricing, capabilities, and preferences.",
      "fields": [
        {
          "id": "company_name",
          "type": "text",
          "label": "Company Name",
          "required": true
        },
        {
          "id": "specialties",
          "type": "multiselect",
          "label": "Primary Specialties",
          "required": true,
          "options": [
            {"value": "residential", "label": "Residential"},
            {"value": "commercial", "label": "Commercial"},
            {"value": "industrial", "label": "Industrial"},
            {"value": "renovation", "label": "Renovation"},
            {"value": "new_construction", "label": "New Construction"}
          ]
        },
        {
          "id": "typical_project_size",
          "type": "select",
          "label": "Typical Project Size",
          "required": true,
          "options": [
            {"value": "under_100k", "label": "Under $100K"},
            {"value": "100k_500k", "label": "$100K - $500K"},
            {"value": "500k_1m", "label": "$500K - $1M"},
            {"value": "over_1m", "label": "Over $1M"}
          ]
        },
        {
          "id": "markup_percentage",
          "type": "slider",
          "label": "Default Markup Percentage",
          "min": 5,
          "max": 50,
          "required": true,
          "helpText": "We'll apply this to material costs unless you specify otherwise"
        },
        {
          "id": "response_time_target",
          "type": "select",
          "label": "Target RFQ Response Time",
          "required": true,
          "options": [
            {"value": "2_hours", "label": "2 hours"},
            {"value": "4_hours", "label": "4 hours"},
            {"value": "same_day", "label": "Same day"},
            {"value": "next_day", "label": "Next business day"}
          ]
        }
      ]
    },
    {
      "id": "upload-data",
      "type": "upload",
      "title": "Upload Your Supplier Data",
      "description": "Share your preferred suppliers and pricing so the agent can compare bids accurately.",
      "fields": [
        {
          "id": "supplier_list",
          "type": "file",
          "label": "Supplier List (CSV or Excel)",
          "accept": [".csv", ".xlsx", ".xls"],
          "required": true,
          "helpText": "Include supplier name, contact, and product categories"
        },
        {
          "id": "rate_sheet",
          "type": "file",
          "label": "Current Rate Sheet (optional)",
          "accept": [".pdf", ".xlsx", ".csv"],
          "required": false,
          "helpText": "If you have standard pricing, we'll use this as a baseline"
        },
        {
          "id": "past_rfqs",
          "type": "file",
          "label": "Sample Past RFQs (optional)",
          "accept": [".pdf", ".docx", ".eml"],
          "required": false,
          "helpText": "Helps the agent learn your response style"
        }
      ]
    },
    {
      "id": "activate",
      "type": "activate",
      "title": "You're All Set!",
      "description": "Your RFQ Agent is now active. Forward any RFQ emails to rfq@yourcompany.agent.ai and we'll handle the rest.",
      "fields": [
        {
          "id": "notification_email",
          "type": "email",
          "label": "Where should we send completed RFQs for review?",
          "required": true
        },
        {
          "id": "auto_send",
          "type": "toggle",
          "label": "Auto-send responses (or review first)",
          "required": true,
          "helpText": "If off, we'll send drafts for your approval before responding"
        }
      ]
    }
  ],
  "completionWebhook": "https://api.yourdomain.com/webhooks/onboarding-complete"
}
```

---

## A2UI Component Library

### Core Components

```tsx
// components/onboarding/Welcome.tsx
export function Welcome({ title, description, onNext }: WelcomeProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-8">
      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6">
        <Sparkles className="w-8 h-8 text-white" />
      </div>
      <h1 className="text-3xl font-bold mb-4">{title}</h1>
      <p className="text-gray-600 max-w-md mb-8">{description}</p>
      <Button onClick={onNext} size="lg">
        Get Started <ArrowRight className="ml-2" />
      </Button>
    </div>
  );
}

// components/onboarding/IntegrationCard.tsx
export function IntegrationCard({ integration, connected, onConnect }: IntegrationCardProps) {
  return (
    <div className={`p-4 border rounded-xl flex items-center justify-between ${connected ? 'border-green-500 bg-green-50' : 'border-gray-200'}`}>
      <div className="flex items-center gap-3">
        <img src={integration.icon} className="w-10 h-10" />
        <div>
          <p className="font-medium">{integration.name}</p>
          <p className="text-sm text-gray-500">{integration.helpText}</p>
        </div>
      </div>
      {connected ? (
        <Badge variant="success">Connected</Badge>
      ) : (
        <Button variant="outline" onClick={onConnect}>
          Connect
        </Button>
      )}
    </div>
  );
}

// components/onboarding/FileUpload.tsx
export function FileUpload({ field, value, onChange }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  
  return (
    <div
      className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
        isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <Upload className="w-8 h-8 mx-auto mb-3 text-gray-400" />
      <p className="font-medium">{field.label}</p>
      <p className="text-sm text-gray-500 mt-1">{field.helpText}</p>
      <p className="text-xs text-gray-400 mt-2">
        Accepts: {field.accept?.join(', ')}
      </p>
      <input
        type="file"
        accept={field.accept?.join(',')}
        onChange={(e) => onChange(e.target.files?.[0])}
        className="hidden"
        id={field.id}
      />
      <label htmlFor={field.id}>
        <Button variant="outline" className="mt-4" asChild>
          <span>Choose File</span>
        </Button>
      </label>
    </div>
  );
}

// components/onboarding/Activation.tsx
export function Activation({ title, description, agentEmail, autoSend }: ActivationProps) {
  return (
    <div className="text-center px-8">
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <CheckCircle className="w-10 h-10 text-green-600" />
      </div>
      <h1 className="text-3xl font-bold mb-4">{title}</h1>
      <p className="text-gray-600 max-w-md mx-auto mb-8">{description}</p>
      
      <div className="bg-gray-50 rounded-xl p-6 max-w-md mx-auto">
        <p className="text-sm text-gray-500 mb-2">Forward RFQs to:</p>
        <code className="text-lg font-mono bg-white px-4 py-2 rounded-lg border">
          {agentEmail}
        </code>
      </div>
      
      <div className="flex items-center justify-center gap-2 mt-6 text-sm text-gray-500">
        {autoSend ? (
          <>
            <Zap className="w-4 h-4 text-yellow-500" />
            <span>Auto-sending enabled</span>
          </>
        ) : (
          <>
            <Eye className="w-4 h-4 text-blue-500" />
            <span>Review mode enabled</span>
          </>
        )}
      </div>
    </div>
  );
}
```

---

## Progress Indicator

```tsx
// components/onboarding/ProgressBar.tsx
export function ProgressBar({ steps, currentStep }: ProgressBarProps) {
  return (
    <div className="flex items-center justify-between max-w-2xl mx-auto mb-12">
      {steps.map((step, i) => (
        <React.Fragment key={step.id}>
          <div className="flex flex-col items-center">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              i < currentStep 
                ? 'bg-green-500 text-white'
                : i === currentStep
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-500'
            }`}>
              {i < currentStep ? <Check /> : i + 1}
            </div>
            <span className="text-xs mt-2 text-gray-500">{step.title}</span>
          </div>
          {i < steps.length - 1 && (
            <div className={`flex-1 h-1 mx-2 ${
              i < currentStep ? 'bg-green-500' : 'bg-gray-200'
            }`} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
```

---

## Data Persistence

All onboarding data is saved to the user's account as they progress:

```typescript
// lib/onboarding/persist.ts

export async function saveOnboardingProgress(
  userId: string,
  flowId: string,
  stepId: string,
  data: Record<string, any>
) {
  await supabase
    .from('onboarding_progress')
    .upsert({
      user_id: userId,
      flow_id: flowId,
      step_id: stepId,
      data,
      updated_at: new Date().toISOString()
    });
}

export async function completeOnboarding(
  userId: string,
  flowId: string,
  allData: Record<string, any>
) {
  // Save final configuration
  await supabase
    .from('agent_configurations')
    .insert({
      user_id: userId,
      agent_type: flowId,
      configuration: allData,
      status: 'active',
      created_at: new Date().toISOString()
    });
  
  // Trigger agent provisioning
  await fetch('/api/agents/provision', {
    method: 'POST',
    body: JSON.stringify({ userId, flowId, configuration: allData })
  });
}
```
