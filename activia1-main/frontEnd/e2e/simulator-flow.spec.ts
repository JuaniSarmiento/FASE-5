/**
 * E2E Test - Simulator Interaction Flow
 */
import { test, expect } from '@playwright/test';

test.describe('Simulator Interaction Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should interact with Product Owner simulator', async ({ page }) => {
    // Navigate to Simulators
    await page.click('text=Simuladores');
    await expect(page).toHaveURL(/.*simulators/);

    // Select Product Owner simulator
    await page.click('.simulator-card:has-text("Product Owner")');

    // Verify simulator started
    await expect(page.locator('.simulator-interface')).toBeVisible();
    await expect(page.locator('text=Product Owner')).toBeVisible();

    // Send message to simulator
    const input = page.locator('textarea[placeholder*="mensaje"]');
    await input.fill('I need help prioritizing user stories for our sprint');
    await page.click('button:has-text("Enviar")');

    // Wait for response
    await expect(page.locator('.message.ai')).toBeVisible({ timeout: 10000 });

    // Verify evaluation feedback
    await expect(page.locator('.evaluation-card')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.evaluation-score')).toBeVisible();
    await expect(page.locator('.evaluation-feedback')).toBeVisible();
  });

  test('should interact with Scrum Master simulator', async ({ page }) => {
    await page.goto('/simulators');

    await page.click('.simulator-card:has-text("Scrum Master")');

    await expect(page.locator('.simulator-interface')).toBeVisible();

    const input = page.locator('textarea[placeholder*="mensaje"]');
    await input.fill('How should I handle blockers in our daily standup?');
    await page.click('button:has-text("Enviar")');

    await expect(page.locator('.message.ai')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.evaluation-card')).toBeVisible({ timeout: 5000 });
  });

  test('should interact with CX Designer simulator', async ({ page }) => {
    await page.goto('/simulators');

    await page.click('.simulator-card:has-text("CX Designer")');

    await expect(page.locator('.simulator-interface')).toBeVisible();

    const input = page.locator('textarea[placeholder*="mensaje"]');
    await input.fill('What user research methods should I use for a mobile app?');
    await page.click('button:has-text("Enviar")');

    await expect(page.locator('.message.ai')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.evaluation-card')).toBeVisible({ timeout: 5000 });
  });

  test('should interact with DevOps Engineer simulator', async ({ page }) => {
    await page.goto('/simulators');

    await page.click('.simulator-card:has-text("DevOps Engineer")');

    await expect(page.locator('.simulator-interface')).toBeVisible();

    const input = page.locator('textarea[placeholder*="mensaje"]');
    await input.fill('Help me set up CI/CD pipeline for a Node.js application');
    await page.click('button:has-text("Enviar")');

    await expect(page.locator('.message.ai')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.evaluation-card')).toBeVisible({ timeout: 5000 });
  });

  test('should interact with Security Engineer simulator', async ({ page }) => {
    await page.goto('/simulators');

    await page.click('.simulator-card:has-text("Security Engineer")');

    await expect(page.locator('.simulator-interface')).toBeVisible();

    const input = page.locator('textarea[placeholder*="mensaje"]');
    await input.fill('What security vulnerabilities should I check for in our API?');
    await page.click('button:has-text("Enviar")');

    await expect(page.locator('.message.ai')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.evaluation-card')).toBeVisible({ timeout: 5000 });
  });

  test('should interact with Software Architect simulator', async ({ page }) => {
    await page.goto('/simulators');

    await page.click('.simulator-card:has-text("Software Architect")');

    await expect(page.locator('.simulator-interface')).toBeVisible();

    const input = page.locator('textarea[placeholder*="mensaje"]');
    await input.fill('Design a microservices architecture for an e-commerce platform');
    await page.click('button:has-text("Enviar")');

    await expect(page.locator('.message.ai')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.evaluation-card')).toBeVisible({ timeout: 5000 });
  });

  test('should switch between different simulators', async ({ page }) => {
    await page.goto('/simulators');

    // Start with Product Owner
    await page.click('.simulator-card:has-text("Product Owner")');
    await expect(page.locator('text=Product Owner')).toBeVisible();

    // Go back to selector
    await page.click('button:has-text("Cambiar Rol")');
    await expect(page.locator('.simulators-grid')).toBeVisible();

    // Select Scrum Master
    await page.click('.simulator-card:has-text("Scrum Master")');
    await expect(page.locator('text=Scrum Master')).toBeVisible();
  });

  test('should display evaluation criteria for each simulator', async ({ page }) => {
    await page.goto('/simulators');

    // Check Product Owner criteria
    const poCard = page.locator('.simulator-card:has-text("Product Owner")');
    await expect(poCard.locator('text=/criterios/i')).toBeVisible();

    // Check Scrum Master criteria
    const smCard = page.locator('.simulator-card:has-text("Scrum Master")');
    await expect(smCard.locator('text=/criterios/i')).toBeVisible();

    // Check CX Designer criteria
    const cxCard = page.locator('.simulator-card:has-text("CX Designer")');
    await expect(cxCard.locator('text=/criterios/i')).toBeVisible();
  });

  test('should show evaluation score after interaction', async ({ page }) => {
    await page.goto('/simulators');

    await page.click('.simulator-card:has-text("Product Owner")');

    const input = page.locator('textarea[placeholder*="mensaje"]');
    await input.fill('I need help prioritizing user stories for our sprint');
    await page.click('button:has-text("Enviar")');

    await expect(page.locator('.evaluation-card')).toBeVisible({ timeout: 10000 });

    // Verify score is displayed
    const scoreElement = page.locator('.evaluation-score');
    await expect(scoreElement).toBeVisible();
    await expect(scoreElement).toContainText(/\d+\/10/);
  });
});
