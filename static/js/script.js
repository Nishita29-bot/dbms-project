document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle) toggle.addEventListener('click', () => links.classList.toggle('open'));

  const search = document.querySelector('#foodSearch');
  if (search) search.addEventListener('input', () => {
    const term = search.value.toLowerCase();
    document.querySelectorAll('#foodGrid .food-card').forEach(card => {
      card.style.display = card.innerText.toLowerCase().includes(term) ? '' : 'none';
    });
  });

  document.querySelectorAll('.confirm-delete').forEach(button => {
    button.addEventListener('click', event => {
      if (!confirm('Are you sure you want to remove this item?')) event.preventDefault();
    });
  });
});
