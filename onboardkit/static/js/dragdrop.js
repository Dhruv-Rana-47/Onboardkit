document.addEventListener('DOMContentLoaded', function () {
    console.log("✅ dragdrop.js loaded");

    // ✅ Drag and drop for SECTIONS
    const sectionsContainer = document.getElementById('sections-container');
    if (sectionsContainer) {
        new Sortable(sectionsContainer, {
            handle: '.handle',
            animation: 150,
            onEnd: function () {
                const order = Array.from(
                    sectionsContainer.querySelectorAll('.accordion-item')
                ).map(el => el.getAttribute('data-id'));
                htmx.trigger(sectionsContainer, 'end', { order: order });
            }
        });
    }

    // ✅ Drag and drop for ITEMS inside each section
    document.querySelectorAll('.item-list').forEach(list => {
        new Sortable(list, {
            handle: '.item-handle',
            animation: 150,
            onEnd: function (evt) {
                const order = Array.from(evt.from.children)
                    .map(el => el.getAttribute('data-id'));
                htmx.trigger(evt.from, 'end', { order: order });
            }
        });
    });
});
