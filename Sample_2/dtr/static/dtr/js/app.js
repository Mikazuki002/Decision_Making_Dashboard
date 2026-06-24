/* Office DTR — front-end helpers.
 *
 *  • Live search: as you type in #live-search, rows whose text doesn't
 *    contain the query get hidden immediately. No page reload needed.
 *  • Auto-update highlight: when a row receives a flash class (set by
 *    the view on redirect) the row briefly highlights yellow to confirm
 *    the change was saved.
 */
(function () {
    const search = document.getElementById('live-search');
    if (search) {
        search.addEventListener('input', function () {
            const q = this.value.trim().toLowerCase();
            const table = document.querySelector('table');
            if (!table) return;
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(function (tr) {
                if (!tr.dataset.rowId && !tr.querySelector('td')) return;
                const text = tr.innerText.toLowerCase();
                tr.style.display = (!q || text.includes(q)) ? '' : 'none';
            });
        });
    }

    // Highlight rows flashed in URL hash (e.g. #row-12)
    if (location.hash && location.hash.startsWith('#row-')) {
        const id = location.hash.replace('#row-', '');
        const row = document.querySelector(`tr[data-row-id="${id}"]`);
        if (row) {
            row.classList.add('flash-update');
            row.scrollIntoView({behavior: 'smooth', block: 'center'});
        }
    }
})();
