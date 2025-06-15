document.addEventListener('DOMContentLoaded', function() {
    // Sections drag and drop
    new Sortable(document.getElementById('sections-container'), {
        handle: '.handle',
        animation: 150,
        onEnd: function() {
            const order = Array.from(
                document.querySelectorAll('#sections-container .accordion-item')
            ).map(el => el.getAttribute('data-id'));
            htmx.trigger('#sections-container', 'end', {order: order});
        }
    });

    // Items drag and drop (similar implementation)
    document.querySelectorAll('.item-list').forEach(list => {
        new Sortable(list, {
            handle: '.item-handle',
            animation: 150,
            onEnd: function(evt) {
                const order = Array.from(evt.from.children)
                    .map(el => el.getAttribute('data-id'));
                htmx.trigger(evt.from, 'end', {order: order});
            }
        });
    });
});



