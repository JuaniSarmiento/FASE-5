/**
 * E2E Test - Evaluation Generation Flow
 */
import { test, expect } from '@playwright/test';

test.describe('Evaluation Generation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should generate evaluation for completed session', async ({ page }) => {
    // Navigate to Evaluator
    await page.click('text=Evaluación de Proceso');
    await expect(page).toHaveURL(/.*evaluator/);

    // Wait for sessions to load
    await expect(page.locator('.sessions-list')).toBeVisible({ timeout: 5000 });

    // Select first session
    const firstSession = page.locator('.session-item').first();
    await firstSession.click();

    // Wait for evaluation generation
    await expect(page.locator('.loading-state')).toBeVisible({ timeout: 2000 });
    await expect(page.locator('.loading-state')).not.toBeVisible({ timeout: 15000 });

    // Verify overall score is displayed
    await expect(page.locator('.overall-score')).toBeVisible();
    await expect(page.locator('.overall-score')).toContainText(/\d+\/100/);

    // Verify 5 dimensions are displayed
    await expect(page.locator('text=Planificación')).toBeVisible();
    await expect(page.locator('text=Ejecución')).toBeVisible();
    await expect(page.locator('text=Depuración')).toBeVisible();
    await expect(page.locator('text=Reflexión')).toBeVisible();
    await expect(page.locator('text=Autonomía')).toBeVisible();

    // Verify each dimension has a score
    const dimensionCards = page.locator('.dimension-card');
    await expect(dimensionCards).toHaveCount(5);

    for (let i = 0; i < 5; i++) {
      const card = dimensionCards.nth(i);
      await expect(card.locator('.score-value')).toContainText(/\d+\/10/);
    }

    // Verify patterns are displayed
    await expect(page.locator('text=Patrones Cognitivos')).toBeVisible();
    await expect(page.locator('text=Autonomía')).toBeVisible();
    await expect(page.locator('text=Metacognición')).toBeVisible();
    await expect(page.locator('text=Delegación')).toBeVisible();

    // Verify recommendations
    await expect(page.locator('text=Recomendaciones')).toBeVisible();
    await expect(page.locator('.recommendations-list li')).toHaveCount(3, { timeout: 5000 });
  });

  test('should export evaluation as PDF', async ({ page }) => {
    await page.goto('/evaluator');

    // Select session
    const firstSession = page.locator('.session-item').first();
    await firstSession.click();

    // Wait for evaluation to load
    await expect(page.locator('.overall-score')).toBeVisible({ timeout: 15000 });

    // Setup download listener
    const downloadPromise = page.waitForEvent('download');

    // Click export button
    await page.click('button:has-text("Exportar PDF")');

    // Wait for download
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/evaluation.*\.pdf/);
  });

  test('should regenerate evaluation', async ({ page }) => {
    await page.goto('/evaluator');

    // Select session
    const firstSession = page.locator('.session-item').first();
    await firstSession.click();

    // Wait for initial evaluation
    await expect(page.locator('.overall-score')).toBeVisible({ timeout: 15000 });

    // Get initial score (stored for potential comparison, currently unused)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const initialScore = await page.locator('.overall-score').textContent();

    // Click regenerate
    await page.click('button:has-text("Regenerar")');

    // Wait for loading state
    await expect(page.locator('.loading-state')).toBeVisible({ timeout: 2000 });

    // Wait for new evaluation
    await expect(page.locator('.overall-score')).toBeVisible({ timeout: 15000 });

    // Verify evaluation was regenerated (component is visible)
    await expect(page.locator('.dimension-card')).toHaveCount(5);
  });

  test('should display circular score visualization', async ({ page }) => {
    await page.goto('/evaluator');

    const firstSession = page.locator('.session-item').first();
    await firstSession.click();

    await expect(page.locator('.overall-score')).toBeVisible({ timeout: 15000 });

    // Verify circular visualization
    const scoreCircle = page.locator('.score-circle');
    await expect(scoreCircle).toBeVisible();

    // Verify SVG circle exists
    const svgCircle = scoreCircle.locator('svg circle');
    await expect(svgCircle).toHaveCount(2); // Background + foreground
  });

  test('should show pattern bars with correct percentages', async ({ page }) => {
    await page.goto('/evaluator');

    const firstSession = page.locator('.session-item').first();
    await firstSession.click();

    await expect(page.locator('.patterns-section')).toBeVisible({ timeout: 15000 });

    // Check pattern bars
    const patternBars = page.locator('.pattern-bar');
    await expect(patternBars).toHaveCount(3); // Autonomy, Metacognition, Delegation

    // Verify each bar has a percentage
    for (let i = 0; i < 3; i++) {
      const bar = patternBars.nth(i);
      const fill = bar.locator('.pattern-fill');
      
      // Get width attribute
      const width = await fill.getAttribute('style');
      expect(width).toContain('width:');
      expect(width).toMatch(/\d+%/);
    }
  });
});
