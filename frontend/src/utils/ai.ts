import { API_BASE_URL } from '../config';

export interface AIValidation {
  step: string;
  action: string;
  is_recommended: boolean;
  warnings: string[];
  recommendation: string;
}

export interface AIInsights {
  stats: any;
  ai_insights: any;
}

/**
 * Analyze dataset with AI on upload
 */
export async function analyzeDatasetWithAI(sessionId: string): Promise<AIInsights | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/ai/analyze-dataset/${sessionId}`, {
      method: 'POST',
    });
    
    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error analyzing dataset with AI:', error);
    return null;
  }
}

/**
 * Validate a preprocessing step with AI before applying it
 */
export async function validateStepWithAI(
  sessionId: string,
  stepName: string,
  actionDescription: string,
  affectedColumns: string[] = []
): Promise<AIValidation | null> {
  try {
    const params = new URLSearchParams({
      session_id: sessionId,
      step_name: stepName,
      action_description: actionDescription,
      affected_columns: JSON.stringify(affectedColumns),
    });

    const response = await fetch(`${API_BASE_URL}/ai/validate-step?${params}`, {
      method: 'POST',
    });
    
    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error validating step with AI:', error);
    return null;
  }
}

/**
 * Clean up AI context when session ends
 */
export async function cleanupAISession(sessionId: string): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/session/cleanup/${sessionId}`, {
      method: 'POST',
    });
  } catch (error) {
    console.error('Error cleaning up AI session:', error);
  }
}
