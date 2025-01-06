//////////// HOW TO USE ////////////
/*
<display-edit-form
        save-url="{% url 'save_changes'%}"
        data-items='[
        {"label": "Name", "name": "student-name", "type": "char", "value": "John Doe", "duress": "readonly"},
        {"label": "Email", "name": "student-email", "type": "char", "value": "john@example.com", "duress": "required"},
        {"label": "Phone", "name": "student-phone", "type": "int", "value": "+1234567890"}
        ]'>
        {% csrf_token %}
</display-edit-form>
*/
////////////////////////////////////


class DisplayEditForm extends HTMLElement {
    constructor() {
        super();
        this.isEditMode = false;
    }

    // Observe these attributes for changes
    static get observedAttributes() {
        return ['data-items'];
    }

    connectedCallback() {
        this.render();
        this.attachEventListeners();
    }

    // Convert the data-items string to an array of objects
    get items() {
        try {
            return JSON.parse(this.getAttribute('data-items'));
        } catch {
            return [];
        }
    }

    attachEventListeners() {
        const editButton = this.querySelector('.edit-button');
        const saveButton = this.querySelector('.save-button');
        const cancelButton = this.querySelector('.cancel-button');

        editButton?.addEventListener('click', () => this.toggleEditMode());
        saveButton?.addEventListener('click', () => this.saveChanges());
        cancelButton?.addEventListener('click', () => this.cancelEdit());
    }

    toggleEditMode() {
        this.isEditMode = !this.isEditMode;
        this.render();
    }

    async saveChanges() {
        const form = this.querySelector('form');
        const formData = new FormData(form);
        try {
            const response = await fetch(this.getAttribute('save-url'), {
                method: 'POST',
                headers: {
                    //'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            });

            if (!response.ok) throw new Error('Save failed');

            const data = await response.json();
            console.log(data);
            this.setAttribute('data-items', JSON.stringify(data));
            this.isEditMode = false;
            this.render();
        } catch (error) {
            console.error('Save failed:', error);
            alert('Failed to save changes');
        }
    }

    cancelEdit() {
        this.isEditMode = false;
        this.render();
    }

    render() {
        const items = this.items;
        
        this.innerHTML = `
            <div class="card shadow">
                ${this.hasAttribute("title") ? 
                `<div class="card-header">
                    <strong>${this.getAttribute("title")}</strong>
                </div>` : ''}
                <div class="card-body">
                    ${this.isEditMode ? this.renderEditMode(items) : this.renderDisplayMode(items)}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderDisplayMode(items) {
        return `
            <div class="list-group list-group-flush">
                ${items.map(item => `
                    <li class="list-group-item d-flex justify-content-between">
                        <strong>${item.label}</strong>
                        <span>${item.value}</span>
                    </li>
                `).join('')}
            </div>
            <div class="text-end mt-3">
                <button type="button" class="btn btn-outline-secondary mt-3 edit-button">
                    <i class="bi bi-pencil"></i> Modify
                </button>
            </div>
        `;
    }

    renderEditMode(items) {
        return `
            <form>
                <div class="list-group list-group-flush">
                    ${items.map((item, index) => `
                        <li class="list-group-item d-flex">
                            <div class="col-4">
                            <strong>${item.label}</strong>
                            </div>
                            <div class="col-8">
                            <input type="${item.type}" 
                                class="form-control" 
                                name="${item.name}" 
                                value="${item.value}" 
                                ${item.duress}>
                            </div>
                        </li>
                    `).join('')}
                </div>
                <div class="row justify-content-between mt-3">
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-secondary mt-3 cancel-button">Cancel</button>
                    </div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-success mt-3 save-button">Save</button>
                    </div>
                </div>
            </form>
        `;
    }
}

// Register the custom element
customElements.define('display-edit-form', DisplayEditForm);