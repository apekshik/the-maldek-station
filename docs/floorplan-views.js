/** Lazy-load the optional 3D study; the SVG plans work independently. */
document.addEventListener('DOMContentLoaded', () => {
  const layout = document.getElementById('plan-v2');
  const plan = layout.querySelector('svg');
  const model = document.getElementById('compound-3d');
  const container = layout.querySelector('.plan-container');
  const switches = layout.querySelectorAll('[data-view]');
  const planControls = [layout.querySelector('.legend'), layout.querySelector('.toggle-sightlines'), layout.querySelector('.zoom-indicator')];
  let initialization;
  switches.forEach(button => button.addEventListener('click', async () => {
    const is3D = button.dataset.view === '3d';
    switches.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    plan.toggleAttribute('hidden', is3D);
    model.hidden = !is3D;
    container.classList.toggle('show-model', is3D);
    planControls.forEach(control => { control.hidden = is3D; });
    if (!is3D) return;
    try {
      if (!initialization) initialization = import('./floorplan-3d.js').then(m => m.initializeCompound(model, layout));
      await initialization;
      model.dispatchEvent(new Event('model-visible'));
    } catch (error) {
      model.querySelector('.model-status').textContent = 'The 3D view could not start. The 2D plan is still available; try reloading this page.';
      model.querySelector('.model-status').hidden = false;
      console.error('Compound viewer:', error);
    }
  }));
});
