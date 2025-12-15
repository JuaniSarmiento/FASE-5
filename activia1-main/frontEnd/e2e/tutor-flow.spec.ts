/**
 * E2E Test - Complete Tutor Session Flow
 */
import { test, expect } from '@playwright/test';

test.describe('Complete Tutor Session Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should complete full tutor session flow', async ({ page }) => {
    // Step 1: Navigate to Tutor page
    await page.click('text=Tutor Cognitivo');
    await expect(page).toHaveURL(/.*tutor/);

    // Step 2: Select Socratic mode
    await page.click('text=Socrático');
    await expect(page.locator('.mode-description')).toContainText(/preguntas/i);

    // Step 3: Create new session
    await page.click('button:has-text("Nueva Sesión")');
    await page.fill('input[name="student_id"]', 'test-student-123');
    await page.fill('input[name="activity_id"]', 'e2e-test-activity');
    await page.click('button:has-text("Crear")');

    // Wait for session creation
    await expect(page.locator('text=test-student-123')).toBeVisible({ timeout: 5000 });

    // Step 4: Send first message
    const messageInput = page.locator('textarea[placeholder*="pregunta"]');
    await messageInput.fill('Explain recursion in programming');
    await page.click('button:has-text("Enviar")');

    // Wait for AI response
    await expect(page.locator('.message.ai')).toBeVisible({ timeout: 10000 });

    // Step 5: Verify metadata badges
    await expect(page.locator('.metadata-badge')).toBeVisible();
    await expect(page.locator('text=/tokens/i')).toBeVisible();

    // Step 6: Send second message
    await messageInput.fill('What are the base cases in recursion?');
    await page.click('button:has-text("Enviar")');

    await expect(page.locator('.message.ai').nth(1)).toBeVisible({ timeout: 10000 });

    // Step 7: Verify message count
    const messages = page.locator('.message');
    await expect(messages).toHaveCount(4); // 2 user + 2 AI

    // Step 8: End session
    await page.click('button:has-text("Finalizar Sesión")');
    await expect(page.locator('text=/Sesión finalizada/i')).toBeVisible({ timeout: 3000 });
  });

  test('should validate message length', async ({ page }) => {
    await page.goto('/tutor');

    // Select mode
    await page.click('text=Explicativo');

    // Try to send short message
    const messageInput = page.locator('textarea[placeholder*="pregunta"]');
    await messageInput.fill('Hi');
    await page.click('button:has-text("Enviar")');

    // Should show validation error
    await expect(page.locator('text=/mínimo 10 caracteres/i')).toBeVisible({ timeout: 3000 });
  });

  test('should abort in-progress request', async ({ page }) => {
    await page.goto('/tutor');

    await page.click('text=Socrático');

    const messageInput = page.locator('textarea[placeholder*="pregunta"]');
    await messageInput.fill('This is a valid question about testing');
    await page.click('button:has-text("Enviar")');

    // Wait for abort button to appear
    await expect(page.locator('button:has-text("Cancelar")')).toBeVisible({ timeout: 2000 });

    // Click abort
    await page.click('button:has-text("Cancelar")');

    // Verify request was aborted
    await expect(page.locator('button:has-text("Enviar")')).toBeVisible({ timeout: 3000 });
  });

  test('should switch between modes', async ({ page }) => {
    await page.goto('/tutor');

    // Select Socratic
    await page.click('text=Socrático');
    await expect(page.locator('.mode-description')).toContainText(/preguntas/i);

    // Switch to Explicativo
    await page.click('text=Explicativo');
    await expect(page.locator('.mode-description')).toContainText(/explicaciones/i);

    // Switch to Guiado
    await page.click('text=Guiado');
    await expect(page.locator('.mode-description')).toContainText(/paso a paso/i);
  });
});
